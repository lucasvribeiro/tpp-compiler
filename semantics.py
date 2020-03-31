from anytree import Node

import anytree

# Constants
OPERATIONS = ['+', '-', '*', '/', ':=', ':']
SIMPLE_PRUNE_NODES = [
    'acao', 'expressao', 'expressao_logica', 'expressao_simples', 'expressao_aditiva', 
    'expressao_multiplicativa', 'expressao_unaria', 'operador_relacional', 
    'operador_logico', 'operador_negacao', 'fator', 'lista_variaveis'
    ]

# Global Variables
symbol_table = []
attr_vars = []
variables = []
attr = []
arrays_errors = []
indice = False
scope = "global"
found_node = None
success = True

errors = {
    "has_principal": False,
    "principal_has_return": False,
    "wrong_function_call": []
}


# ----- Prunning Functions -----
def prune_especial(tree):
    aux = []

    if(tree.parent.name in ["operador_soma", "operador_multiplicacao"]):
        prune_one_node(tree.parent)

    dad = tree.parent
    aux = [dad.children[0], dad.children[2]] 
    tree.children = aux
    dad.children = [tree]
    
def prune_one_node(tree):
    aux = []
    dad = tree.parent

    for i in range(len(dad.children)):
        if (dad.children[i].name == tree.name):
            aux += tree.children
        else:
            aux.append(dad.children[i])

    dad.children = aux

def prune(tree):
    for node in tree.children:
        prune(node)

    if(tree.name in OPERATIONS):
        prune_especial(tree)

    if(tree.name in SIMPLE_PRUNE_NODES):
        prune_one_node(tree)
    
    if(tree.name in ['corpo', 'lista_declaracoes', 'lista_parametros', 'lista_argumentos'] and tree.parent.name == tree.name):
        prune_one_node(tree)

# ----- Auxiliar functions -----
def get_node(node, name):
    global found_node
    for n in node.children:
        if (n.name == name):
            found_node = n.children
        
        else:
            get_node(n, name)
    
    return found_node

def find_scope(node):
    global scope
    if(node.parent.name != "programa"):
        if(node.parent.name == "cabecalho"):
            scope = node.parent.children[0].name
        else:
            find_scope(node.parent)

def get_func(func):
    for symbol in symbol_table:
        if(symbol["symbol_type"] == "function" and symbol["name"] == func):
            return symbol
    
    return None

def get_attr(node):
    global indice
    for n in node.children:
        if (n.name == "indice"):
            indice = True
        if (n.name == "var" and len(n.children) == 1):
            for s in symbol_table:
                if (n.children[0].name == s["name"] and s["symbol_type"] == "variable"):
                    attr_vars.append(s["value_type"])
        elif (n.name == "numero"):
            if (n.children[0].name.isdigit()):
                attr_vars.append("inteiro")
            else:
                attr_vars.append("flutuante")
        get_attr(n)

# Function to generate symbol table
def generate_symbol_table(tree):
    for node in tree.children:
        symbol = {
            "symbol_type": None,
            "name": None,
            "value_type": None,
            "scope": None,
            "parameters": [],
            "return": [],
            "dimensions": [],
            "declared": True,
            "inicialized": False,
            "used": False
        }

        if(node.name == "declaracao_funcao"):
            symbol["symbol_type"] = "function"
            symbol["value_type"] = get_node(node, "tipo")[0].name
            symbol["name"] = get_node(node, "cabecalho")[0].name

            retorno = get_node(node, "retorna")[2]

            if(retorno.name == "numero"):
                ret_type = "inteiro"
                if(not retorno.children[0].name.isdigit()):
                    ret_type = "flutuante"

                symbol["return"].append({
                    "is_variable": False,
                    "ret_type": ret_type,
                    "ret_value": retorno.children[0].name
                })

            elif(retorno.name == "var"):
                ret_type = "inteiro"
                
                for s in symbol_table:
                    if(s["name"] == retorno.children[0].name and s["symbol_type"] == "variable"):
                        ret_type = s["value_type"]

                symbol["return"].append({
                    "is_variable": True,
                    "ret_type": ret_type,
                    "ret_value": retorno.children[0].name
                })

            for param in (get_node(node, "lista_parametros")):
                if(param.name == "parametro"):
                    symbol["parameters"].append({
                        "par_type": get_node(param, "tipo")[0].name,
                        "par_name": get_node(param, ":")[1].name
                    })

                    symbol_table.append({
                        "symbol_type": "variable",
                        "name": get_node(param, ":")[1].name,
                        "value_type": get_node(param, "tipo")[0].name,
                        "scope": node.children[0].children[0].name,
                        "parameters": [],
                        "declared": True,
                        "inicialized": False,
                        "used": False
                    })
            symbol_table.append(symbol)

        elif(node.name == "declaracao_variaveis"):
            symbol["symbol_type"] = "variable"
            symbol["value_type"] = get_node(node, "tipo")[0].name
            symbol["name"] = get_node(node, "var")[0].name

            if(node.parent.name == "corpo"):
                symbol["scope"] = node.parent.parent.children[0].name
            
            else:
                symbol["scope"] = "global"

            
            if(len(node.children[0].children[1].children) > 1):
                indice = node.children[0].children[1].children[1]

                if(len(indice.children) == 3):
                    symbol["dimensions"].append(indice.children[1].children[0].name)
                
                elif(len(indice.children) >  3):
                    symbol["dimensions"].append(indice.children[0].children[1].children[0].name)
                    symbol["dimensions"].append(indice.children[2].children[0].name)
            symbol_table.append(symbol)

        generate_symbol_table(node)

# ----- Semantic rules functions -----
def check_recursive_call(node):
    for n in node.children:
        if(n.name == "chamada_funcao" and n.children[0].name == "principal"):
            print("AVISO: Chamada recursiva para principal.")
        check_recursive_call(n)

def check_main_function(tree):
    for node in tree.children:
        if(node.name == "cabecalho" and node.children[0].name == "principal"):
            check_recursive_call(node)
            errors["has_principal"] = True

            if(node.children[-1].children[-1].name == "retorna"):
                errors["principal_has_return"] = True
             
        
        check_main_function(node)

def check_func_call(tree):
    global success
    for node in tree.children:
        if(node.name == "chamada_funcao"):
            func = get_func(node.children[0].name)

            if(func == None):
                success = False
                print("ERRO: Chamada à função \'", func["name"], "\' que não foi declarada.")

            else:
                func["used"] = True

                if(node.children[0].name == "principal" and  node.parent.name == "corpo" and node.parent.parent.children[0].name != "principal"):
                    success = False
                    print("ERRO: Chamada para a função principal não permitida.")

                else:
                    if(len(func["parameters"]) == 1):
                        if (len(func["parameters"]) != len(node.children[2].children)):
                            errors["wrong_function_call"].append(func["name"])
                    elif(len(func["parameters"]) > 1):
                        if (len(func["parameters"]) != len(node.children[2].children)-1):
                            errors["wrong_function_call"].append(func["name"])


        check_func_call(node)

def check_not_used_functions():
    for symbol in symbol_table:
        if(symbol["symbol_type"] == "function" and not symbol["used"] and symbol["name"] != "principal"):
            print("AVISO: Função \'", symbol["name"], "\' declarada, mas não utilizada.")

def check_var_errors():
    global success
    for symbol in symbol_table:
        if(symbol["symbol_type"] == "variable"):
            declared = symbol["declared"]
            inicialized = symbol["inicialized"]
            used = symbol["used"]

            if(declared and not inicialized or not used):
                print("AVISO: Variável \'", symbol["name"], "\' declarada e não utilizada")

def check_var_inicialization(tree):
    global success
    for node in tree.children:
        if (node.name in [":=", "leia", "escreva", "repita", "se", "lista_argumentos"]):
            for n in node.children:
                if(n.name == "var"):
                    if (n.children[0].name not in variables):
                        variables.append(n.children[0].name)

            for symbol in symbol_table:
                if(symbol["symbol_type"] == "variable" and symbol["name"] in variables):
                    find_scope(node)
                    if(symbol["scope"] == "global" or symbol["scope"] == scope):
                        symbol["used"] = True

                        if (node.name in [":=", "leia"]):
                            symbol["inicialized"] = True

        check_var_inicialization(node)

def check_attrib(tree):
    global success
    global attr_vars
    global indice
    value_type = ""
    for node in tree.children:
        if(node.name == ":="):
            indice = False
            attr_vars = []
            get_attr(node)

            if(not indice):
                for s in symbol_table:
                    if(s["symbol_type"] == "variable"):
                        if(s["name"] == node.children[0].children[0].name):
                            value_type = s["value_type"]
                
                if(value_type == "inteiro" and "flutuante" in attr_vars):
                    print("AVISO: Atribuição de tipos distintos \'", node.children[0].children[0].name, "\' inteiro e expressão flutuante.")
                
                elif(value_type == "flutuante" and "inteiro" in attr_vars):
                    print("AVISO: Atribuição de tipos distintos \'", node.children[0].children[0].name, "\' flutuante e expressão inteiro.")
        
        check_attrib(node)

def check_array(node):
    global success
    indice = None
    aux = 1
    err = False
    for n in node.children:
        if(n.name == ":" and len(n.children[1].children) > 1):
            indice = n.children[1].children[1]
        
        elif(n.name == ":=" and len(n.children[0].children) > 1):
            indice = n.children[0].children[1]
            aux = 0

        if(indice != None):
            if(n.children[aux].children[0].name not in arrays_errors):
                if(len(indice.children) == 3):
                    if(indice.children[1].name == "numero"):
                        if (not indice.children[1].children[0].name.isdigit()):
                            success = False
                            print("ERRO: Índice de array \'", n.children[aux].children[0].name ,"\' não inteiro.")
                            err = True
                    else:
                        var = indice.children[1].children[0].name
                        for s in symbol_table:
                            if(var == s["name"] and s["symbol_type"] == "variable" and s["value_type"] == "flutuante"):
                                success = False
                                print("ERRO: Índice de array \'", n.children[aux].children[0].name ,"\' não inteiro.")
                                err = True
                
                else:
                    if(indice.children[0].children[1].name == "numero"):
                        if (not indice.children[0].children[1].children[0].name.isdigit()):
                            success = False
                            print("ERRO: Índice de array \'", n.children[aux].children[0].name ,"\' não inteiro.")
                            err = True
                    else:
                        var = indice.children[0].children[1].children[0].name
                        for s in symbol_table:
                            if(var == s["name"] and s["symbol_type"] == "variable" and s["value_type"] == "flutuante"):
                                success = False
                                print("ERRO: Índice de array \'", n.children[aux].children[0].name ,"\' não inteiro.")
                                err = True

                    if(not err):
                        if(indice.children[2].name == "numero"):
                            if (not indice.children[2].children[0].name.isdigit()):
                                success = False
                                print("ERRO: Índice de array \'", n.children[aux].children[0].name ,"\' não inteiro.")
                                err = True
                        else:
                            var = indice.children[2].children[0].name
                            for s in symbol_table:
                                if(var == s["name"] and s["symbol_type"] == "variable" and s["value_type"] == "flutuante"):
                                    success = False
                                    print("ERRO: Índice de array \'", n.children[aux].children[0].name ,"\' não inteiro.")
                                    err = True

            if (err):
                arrays_errors.append(n.children[aux].children[0].name)

        check_array(n)

def check_index(node):
    global success
    indices = []
    for n in node.children:
        if(n.name == ":="):
            if(len(n.children[0].children) > 1):
                indice = n.children[0].children[1]

                if(len(indice.children) == 3):
                    if(indice.children[1].name == "numero"):
                        numero = indice.children[1].children[0].name

                        for s in symbol_table:
                            if(n.children[0].children[0].name == s["name"] and s["symbol_type"] == "variable"):
                                if(numero >= s["dimensions"]):
                                    success = False
                                    print("ERRO: índice de array ", s["name"] ," fora do intervalo (out of range)")
                
                else:
                    if(indice.children[0].children[1].name == "numero"):
                        indices.append(indice.children[0].children[1].children[0].name)
                    
                    if(indice.children[2].name == "numero"):
                        indices.append(indice.children[2].children[0].name)

                    for s in symbol_table:
                            if(n.children[0].children[0].name == s["name"] and s["symbol_type"] == "variable"):
                                if(len(s["dimensions"]) > 0):
                                    for i in range(len(s["dimensions"])):

                                        if(int(indices[i]) >= int(s["dimensions"][i])):
                                            success = False
                                            print("ERRO: índice de array ", s["name"] ," fora do intervalo (out of range)")
                                            break




        check_index(n)

# ----- Main Function -----
def semantics(tree):
    global success

    # Prune Tree and Generate Symbol Table
    prune(tree)
    generate_symbol_table(tree)

    # Principal Function Verifications
    check_main_function(tree)

    if(not errors["has_principal"]):
        success = False
        print("ERRO: Função principal não declarada.")
    
    elif(not errors["principal_has_return"]):
        success = False
        print("ERRO: Função principal deveria retornar inteiro, mas retorna vazio.")
    

    # Function calls verifications
    check_func_call(tree)
    check_not_used_functions()

    if(len(errors["wrong_function_call"]) > 0):
        for err in errors["wrong_function_call"]:
            success = False
            print("ERRO: Chamada à função \'", err , "\' com número de parâmetros diferente que o declarado.")

    check_var_inicialization(tree)

    for symbol in symbol_table:
        if (symbol["name"] in variables):
            variables.remove(symbol["name"])

        if(symbol["symbol_type"] == "variable"):
            if (not symbol["inicialized"] and not symbol["used"]):
                print("AVISO: Variável \'", symbol["name"] , "\' declarada e não utilizada.")
            
            elif(not symbol["inicialized"] and symbol["used"]):
                print("AVISO: Variável \'", symbol["name"] , "\' declarada e não inicializada.")
    
    if(len(variables) > 0):
        for var in variables:
            success = False
            print("ERRO: Variável \'", var ,"\'  não declarada.")

    count = 0

    for s in symbol_table:
        for t in symbol_table:
            if (s["name"] == t["name"] and s["scope"] == t["scope"]):
                count += 1
        
        if(count > 1):
            print("AVISO: Variável \'", t["name"] ,"\' já declarada anteriormente")

        count = 0
    
    check_attrib(tree)
    check_array(tree)
    check_index(tree)

    return tree, symbol_table, success