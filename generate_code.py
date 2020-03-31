from llvmlite import ir
from llvmlite import binding as llvm

import itertools

llvm.initialize()
llvm.initialize_all_targets()
llvm.initialize_native_target()
llvm.initialize_native_asmprinter()

module = ir.Module('module.bc')
module.triple = llvm.get_default_triple()

target = llvm.Target.from_triple(module.triple)
target_machine = target.create_target_machine()

module.data_layout = target_machine.target_data

escrevaInteiro = ir.Function(module,ir.FunctionType(ir.VoidType(), [ir.IntType(32)]),name="escrevaInteiro")
escrevaFlutuante = ir.Function(module,ir.FunctionType(ir.VoidType(),[ir.FloatType()]),name="escrevaFlutuante")
leiaInteiro = ir.Function(module,ir.FunctionType(ir.IntType(32),[]),name="leiaInteiro")
leiaFlutuante = ir.Function(module,ir.FunctionType(ir.FloatType(),[]),name="leiaFlutuante")

info = {
    "global_variables": []
}
local_vars = []
aux = []
functions = []

def find_var(name, local_vars, function):
    for var in info["global_variables"] + local_vars:
        if(var.name == name):
            return var, "var"
    
    for arg in function["function"].args:
        if(arg.name == name):
            return arg, "arg"


def solve_expression(n, local_vars, function):
    param_1 = 0
    param_2 = 0

    if(n.children[0].name == "numero"):
        param_1 = ir.Constant(ir.IntType(32), int(n.children[0].children[0].name))
    elif(n.children[0].name == "var"):
        ret, what = find_var(n.children[0].children[0].name, local_vars, function)

        if(what == "var"):
            param_1 = function["builder"].load(ret)
        
        else:
            param_1 = ret
    
    if(n.children[1].name == "numero"):
        param_2 = ir.Constant(ir.IntType(32), int(n.children[1].children[0].name))
    elif(n.children[1].name == "var"):
        ret, what = find_var(n.children[1].children[0].name, local_vars, function)
        
        if(what == "var"):
            param_2 = function["builder"].load(ret)
        
        else:
            param_2 = ret
        
    if(n.name == "+"): return function["builder"].add(param_1, param_2, name='summ')
    elif(n.name == "-"): return function["builder"].sub(param_1, param_2, name='sub')
    elif(n.name == "*"): return function["builder"].mul(param_1, param_2, name='mult')
    elif(n.name == "/"): return function["builder"].sdiv(param_1, param_2, name='div')


def solve_func_call(n, builder, local_vars, function):
    global functions
    params = []

    for f in functions:
        if(f["function"].name == n.children[0].name):
            if(len(n.children[2].children) > 0):
                for arg in n.children[2].children:
                    if(arg.name == "var"):
                        ret, what = find_var(arg.children[0].name, local_vars, f)
                        params.append(
                            function["builder"].load(ret)
                        )
                    elif(arg.name == "numero"):
                        params.append(
                            ir.Constant(ir.IntType(32), int(arg.children[0].name))
                        )
                return builder.call(f["function"], params)

            else:
                return builder.call(f["function"], [])

def fill_function(corpo, function):
    global local_vars
    global aux

    for node in corpo.children:
        if(node not in aux):
            aux.append(node)
            if(node.name == "declaracao_variaveis"):
                if(node.children[0].children[0].children[0].name == "inteiro"):
                    var = function["builder"].alloca(ir.IntType(32), name=node.children[0].children[1].children[0].name)

                elif(node.children[0].children[0].children[0].name == "flutuante"):
                    var = function["builder"].alloca(ir.FloatType(), name=node.children[0].children[1].children[0].name)

                var.align = 4
                local_vars.append(var)
            
            elif(node.name == "atribuicao"):
                # Atribuição de um único número ou uma única variável.

                if(node.children[0].children[1].name == "numero" or node.children[0].children[1].name == "var"):
                    var = 0
                    
                    for local in local_vars + info["global_variables"]:
                        if(local.name == node.children[0].children[0].children[0].name):
                            var = local

                    if(node.children[0].children[1].name == "var"):
                        aux = local_vars + info["global_variables"]

                        for a in aux:
                            if(node.children[0].children[1].children[0].name == a.name):
                                temp = function["builder"].load(a,"")
                                function["builder"].store(temp, var)
                    
                    else:
                        if(str(var.type) == "i32*"):
                            function["builder"].store(ir.Constant(ir.IntType(32),  int(node.children[0].children[1].children[0].name)) , var)
                        
                        elif(str(var.type) == "float*"):
                            function["builder"].store(ir.Constant(ir.FloatType(),  float(node.children[0].children[1].children[0].name)) , var)

                elif(node.children[0].children[1].name in ["+", "-", "*", "/"]):
                    op = solve_expression(node.children[0].children[1] ,local_vars, function)
                    ret, what = find_var(node.children[0].children[0].children[0].name,local_vars, function)
                    function["builder"].store(op, ret)

                elif(node.children[0].children[1].name == "chamada_funcao"):
                    f = solve_func_call(node.children[0].children[1], function["builder"], local_vars, function)
                    ret, what = find_var(node.children[0].children[0].children[0].name ,local_vars, function)
                    function["builder"].store(f, ret)

            elif(node.name == "repita" and len(node.children) > 0):
                repita = function["builder"].append_basic_block('repita')
                ate = function["builder"].append_basic_block('ate')
                repita_fim = function["builder"].append_basic_block('repita_fim')

                function["builder"].branch(repita)
                function["builder"].position_at_end(repita)
                fill_function(node.children[1], function)
                function["builder"].branch(ate)

                function["builder"].position_at_end(ate)

                if (node.children[3].name == "var"):
                    for var in local_vars + info["global_variables"]:
                        if (var.name == node.children[3].children[0].name):
                            a_cmp = function["builder"].load(var, 'a_cmp', align=4)
                
                elif (node.children[3].name == "numero"):
                    a_cmp = ir.Constant(ir.IntType(32), int(node.children[3].children[0].name))
                
                if (node.children[5].name == "var"):
                    for var in local_vars + info["global_variables"]:
                        if (var.name == node.children[5].children[0].name):
                            b_cmp = function["builder"].load(var, 'a_cmp', align=4)
                
                elif (node.children[5].name == "numero"):
                    b_cmp = ir.Constant(ir.IntType(32), int(node.children[5].children[0].name))

                comp = function["builder"].icmp_signed("==", a_cmp, b_cmp, name='comp')
                function["builder"].cbranch(comp, repita_fim, repita)

                function["builder"].position_at_end(repita_fim)

            elif(node.name == "condicional"):
                has_else = False

                for n in node.children:
                    if (n.name == "senão"):
                        has_else = True

                iftrue_1 = function["builder"].append_basic_block('iftrue_1')
                iffalse_1 = function["builder"].append_basic_block('iffalse_1')
                ifend_1 = function["builder"].append_basic_block('ifend_1')

                if (node.children[1].name == "var"):
                    for var in local_vars + info["global_variables"]:
                        if (var.name == node.children[1].children[0].name):
                            a_cmp = function["builder"].load(var, 'a_cmp', align=4)
                
                elif (node.children[1].name == "numero"):
                    a_cmp = ir.Constant(ir.IntType(32), int(node.children[1].children[0].name))
                
                if (node.children[3].name == "var"):
                    for var in local_vars + info["global_variables"]:
                        if (var.name == node.children[3].children[0].name):
                            b_cmp = function["builder"].load(var, 'a_cmp', align=4)
                
                elif (node.children[3].name == "numero"):
                    b_cmp = ir.Constant(ir.IntType(32), int(node.children[3].children[0].name))
                
                If_1 = function["builder"].icmp_signed(node.children[2].name, a_cmp, b_cmp, name='if_test_1')
                function["builder"].cbranch(If_1, iftrue_1, iffalse_1)

                then_body = node.children[5]

                function["builder"].position_at_end(iftrue_1)
                fill_function(then_body, function)
                function["builder"].branch(ifend_1)

                if(has_else):
                    else_body = node.children[7]
                    function["builder"].position_at_end(iffalse_1)
                    fill_function(else_body, function)
                    function["builder"].branch(ifend_1)
                else:
                    function["builder"].position_at_end(iffalse_1)
                    function["builder"].branch(ifend_1)

                function["builder"].position_at_end(ifend_1)

            elif(node.name == "leia" and len(node.children) > 0):
                if(node.children[2].name == "var"):
                    for v in local_vars + info["global_variables"]:
                        if (v.name == node.children[2].children[0].name):
                            if(str(v.type) == "i32*"):
                                ret = function["builder"].call(leiaInteiro, [])
                                function["builder"].store(ret, v)

                            elif(str(v.type) == "float*"):
                                ret = function["builder"].call(leiaFlutuante, [])
                                function["builder"].store(ret, v)
            
            elif(node.name == "escreva" and len(node.children) > 0):
                if(node.children[2].name == "var"):
                    for v in local_vars + info["global_variables"]:
                        if (v.name == node.children[2].children[0].name):
                            if(str(v.type) == "i32*"):
                                var = function["builder"].load(v, name='write_var', align=4)
                                function["builder"].call(escrevaInteiro, [var])
                            elif(str(v.type) == "float*"):
                                var = function["builder"].load(v, name='write_var', align=4)
                                function["builder"].call(escrevaFlutuante, [var])
                elif(node.children[2].name == "numero"):
                    if(node.children[2].children[0].name.isdigit()):
                        var = ir.Constant(ir.IntType(32), int(node.children[2].children[0].name))
                        
                        function["builder"].call(escrevaInteiro, [var])

                    elif(not node.children[2].children[0].name.isdigit()):
                        var = ir.Constant(ir.FloatType(), float(node.children[2].children[0].name))
                        function["builder"].call(escrevaFlutuante, [var]) 

            elif(node.name == "retorna" and len(node.children) > 0):
                r = 0
                if(node.children[2].name == "numero"):
                    r = ir.Constant(ir.IntType(32), int(node.children[2].children[0].name))
                
                elif(node.children[2].name == "var"):
                    for var in local_vars+info["global_variables"]:
                        if(var.name == node.children[2].children[0].name):
                            r = function["builder"].load(var, name='ret_temp', align=4)
                
                elif(node.children[2].name in ["+", "-", "*", "/"]):
                    r = function["builder"].alloca(ir.IntType(32), name='ret_temp')
                    op = solve_expression(node.children[2], local_vars, function)
                    function["builder"].store(op, r)

                function["builder"].ret(r)
            
            # elif(node.name == "chamada_funcao"):
            #     solve_func_call(node, function["builder"])
        
        fill_function(node, function)


def go_through_tree(tree, functions):
    global local_vars
    for node in tree.children:

        for f in functions:
            if((f["function"].name == node.name or (f["function"].name == "main" and node.name == "principal")) and node.parent.name == "cabecalho"):
                local_vars = []
                fill_function(node.parent.children[-1], f)

        go_through_tree(node, functions)
    
def gen_code(tree, symbol_table, sema_success):
    # symbol = {
    #         "symbol_type": None,
    #         "name": None,
    #         "value_type": None,
    #         "scope": None,
    #         "parameters": [],
    #         "dimensions": [],
    #         "declared": True,
    #         "inicialized": False,
    #         "used": False
    #     }
    global module
    global info


    # Define Global Variables and Functions
    for symbol in symbol_table:
        if (symbol["symbol_type"] == "variable" and symbol["scope"] == "global"):
            var_type = symbol["value_type"]

            if(var_type == "inteiro"):
                if(len(symbol["dimensions"]) == 0):
                    g = ir.GlobalVariable(module, ir.IntType(32), symbol["name"])

                if(len(symbol["dimensions"]) == 1):
                    g_type = ir.ArrayType(ir.IntType(32), int(symbol["dimensions"][0]))
                    g = ir.GlobalVariable(module, g_type, symbol["name"])
                    info["global_variables"].append(g)
            
            elif(var_type == "flutuante"):

                if(len(symbol["dimensions"]) == 0):
                    g = ir.GlobalVariable(module, ir.FloatType(), symbol["name"])

                if(len(symbol["dimensions"]) == 1):
                    g_type = ir.ArrayType(ir.FloatType(), int(symbol["dimensions"][0]))
                    g = ir.GlobalVariable(module, g_type, symbol["name"])
            
            g.linkage = "common"
            g.align = 4
            info["global_variables"].append(g)

        elif (symbol["symbol_type"] == "function"):
            if(symbol["name"] == "principal"):
                symbol["name"] = "main"
            
            arguments_list = []

            if (len(symbol["parameters"]) > 0):
                for a in symbol["parameters"]:
                    if(a["par_type"] == "inteiro"):
                        arguments_list.append(ir.IntType(32))
                    else:
                        arguments_list.append(ir.FloatType())


            if(len(symbol["return"]) > 0):
                if(symbol["return"][0]["ret_type"] == "inteiro"):
                    f_ret = ir.IntType(32)
                else:
                    f_ret = ir.FloatType()
            
                f_func = ir.FunctionType(f_ret, arguments_list)
                f = ir.Function(module, f_func, name=symbol["name"])
                entryBlock = f.append_basic_block('entry')
                builder = ir.IRBuilder(entryBlock)
                
            else:
                f_func = ir.FunctionType(ir.VoidType(), arguments_list)
                f = ir.Function(module, f_func, name=symbol["name"])
                entryBlock = f.append_basic_block('entry')
                builder = ir.IRBuilder(entryBlock)
            
            for i in range(len(f.args)):
                f.args[i].name = symbol["parameters"][i]["par_name"]


            functions.append({"function": f, "builder": builder, "arguments": f.args})

    go_through_tree(tree, functions)

    file = open('module.ll', 'w')
    file.write(str(module))
    file.close()
    print(module)