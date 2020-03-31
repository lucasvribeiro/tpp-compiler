import ply.yacc as yacc

import lexical as lex

from anytree import Node

tokens = lex.tokens

success = True
total_lines = 0

def f_column(token, pos):
  input = token.lexer.lexdata
  line_start = input.rfind('\n', 0, token.lexpos(pos)) + 1
  return (token.lexpos(pos) - line_start) + 1

def p_programa(p):
  '''
    programa : lista_declaracoes
  '''

  p[0] = Node('programa', value = 'programa', children = [p[1]])

def p_lista_declaracoes(p):
  '''
    lista_declaracoes : lista_declaracoes declaracao
                        | declaracao
  '''

  if(len(p) == 3):
    p[0] = Node('lista_declaracoes', value = 'lista_declaracoes', children = [
      p[1],
      p[2]
    ])
  else:
    p[0] = Node('lista_declaracoes', value = 'lista_declaracoes', children = [p[1]])

def p_declaracao(p):
  '''
    declaracao : declaracao_variaveis
                | inicializacao_variaveis
                | declaracao_funcao
  '''

  p[0] = Node('declaracao', value = 'declaracao', children = [p[1]])

def p_declaracao_variaveis(p):
  '''
    declaracao_variaveis : tipo DOIS_PONTOS lista_variaveis
  '''

  p[0] = Node('declaracao_variaveis', value = 'declaracao_variaveis', children = [
    p[1],
    Node(str(p[2]), value = str(p[2]), line = (p.lineno(2) - (total_lines - 1)), column = f_column(p, 2)),
    p[3]
  ])

def p_inicializacao_variaveis(p):
  '''
    inicializacao_variaveis : atribuicao
  '''

  p[0] = Node('inicializacao_variaveis', value = 'inicializacao_variaveis', children = [p[1]])

def p_lista_variaveis(p):
  '''
    lista_variaveis : lista_variaveis VIRGULA var 
                    | var
  '''

  if(len(p) == 4):
    p[0] = Node('lista_variaveis', value = 'lista_variaveis', children = [
      p[1],
      Node(str(p[2]), value = str(p[2]), line = (p.lineno(2) - (total_lines - 1)), column = f_column(p, 2)),
      p[3]
    ])
  else:
    p[0] = Node('lista_variaveis', value = 'lista_variaveis', children = [p[1]])

def p_var(p):
  '''
    var : ID
        | ID indice
  '''

  if(len(p) == 3):
    p[0] = Node('var', value = 'var', children = [
      Node(str(p[1]), value = str(p[1]), line = (p.lineno(1) - (total_lines - 1)), column = f_column(p, 1)),
      p[2]
    ])
  else:
    p[0] = Node('var', value = 'var', children = [
      Node(str(p[1]), value = str(p[1]), line = (p.lineno(1) - (total_lines - 1)), column = f_column(p, 1))
    ])

def p_indice(p):
  '''
    indice : indice ABRE_COLCHETES expressao FECHA_COLCHETES
            | ABRE_COLCHETES expressao FECHA_COLCHETES
  '''

  if(len(p) == 5):
    p[0] = Node('indice', value = 'indice', children = [
      p[1],
      Node(str(p[2]), value = str(p[2]), line = (p.lineno(2) - (total_lines - 1)), column = f_column(p, 2)),
      p[3],
      Node(str(p[4]), value = str(p[4]), line = (p.lineno(4) - (total_lines - 1)), column = f_column(p, 4))
    ])
  else:
    p[0] = Node('indice', value = 'indice', children = [
      Node(str(p[1]), value = str(p[1]), line = (p.lineno(1) - (total_lines - 1)), column = f_column(p, 1)),
      p[2],
      Node(str(p[3]), value = str(p[3]), line = (p.lineno(3) - (total_lines - 1)), column = f_column(p, 3))
    ])

def p_tipo(p):
  '''
    tipo : INTEIRO
          | FLUTUANTE
  '''

  p[0] = Node('tipo', value = 'tipo', children = [
    Node(str(p[1]), value = str(p[1]), line = (p.lineno(1) - (total_lines - 1)), column = f_column(p, 1))
  ])

def p_declaracao_funcao(p):
  '''
    declaracao_funcao : tipo cabecalho 
                        | cabecalho
  '''

  if(len(p) == 3):
    p[0] = Node('declaracao_funcao', value = 'declaracao_funcao', children = [
      p[1],
      p[2]
    ])
  else:
    p[0] = Node('declaracao_funcao', value = 'declaracao_funcao', children = [p[1]])

def p_cabecalho(p):
  '''
    cabecalho : ID ABRE_PARENTESES lista_parametros FECHA_PARENTESES corpo FIM
  '''

  p[0] = Node('cabecalho', value = 'cabecalho', children = [
    Node(str(p[1]), value = str(p[1]), line = (p.lineno(1) - (total_lines - 1)), column = f_column(p, 1)),
    Node(str(p[2]), value = str(p[2]), line = (p.lineno(2) - (total_lines - 1)), column = f_column(p, 2)),
    p[3],
    Node(str(p[4]), value = str(p[4]), line = (p.lineno(4) - (total_lines - 1)), column = f_column(p, 4)),
    p[5]
  ])

def p_lista_parametros(p):
  '''
    lista_parametros : lista_parametros VIRGULA parametro
                      | parametro
                      | vazio
  '''

  if(len(p) == 4):
    p[0] = Node('lista_parametros', value = 'lista_parametros', children = [
      p[1],
      Node(str(p[2]), value = str(p[2]), line = (p.lineno(2) - (total_lines - 1)), column = f_column(p, 2)),
      p[3]
    ])
  else:
    if(p[1] is not None):
      p[0] = Node('lista_parametros', value = 'lista_parametros', children = [p[1]])
    else:
      p[0] = Node('lista_parametros', value = 'lista_parametros')

def p_parametro(p):
  '''
    parametro : tipo DOIS_PONTOS ID
              |  parametro ABRE_COLCHETES FECHA_COLCHETES
  '''

  p[0] = Node('parametro', value = 'parametro', children = [
    p[1],
    Node(str(p[2]), value = str(p[2]), line = (p.lineno(2) - (total_lines - 1)), column = f_column(p, 2)),
    Node(str(p[3]), value = str(p[3]), line = (p.lineno(3) - (total_lines - 1)), column = f_column(p, 3))
  ])

def p_corpo(p):
  '''
    corpo : corpo acao
          | vazio
  '''

  if(len(p) == 3):
    p[0] = Node('corpo', value = 'corpo', children = [
      p[1],
      p[2]
    ])
  else: 
    p[0] = Node('corpo', value = 'corpo')

def p_acao(p):
  '''
    acao : expressao
          | declaracao_variaveis
          | se
          | repita
          | leia
          | escreva
          | retorna
  '''

  p[0] = Node('acao', value = 'acao', children = [p[1]])

def p_se(p):
  '''
    se : SE expressao ENTAO corpo FIM
        | SE expressao ENTAO corpo SENAO corpo FIM
  '''

  if(len(p) == 6):
    p[0] = Node('condicional', value = 'condicional', children = [
      Node(str(p[1]), value = str(p[1]), line = (p.lineno(1) - (total_lines - 1)), column = f_column(p, 1)),
      p[2],
      Node(str(p[3]), value = str(p[3]), line = (p.lineno(3) - (total_lines - 1)), column = f_column(p, 3)),
      p[4],
      Node(str(p[5]), value = str(p[5]), line = (p.lineno(5) - (total_lines - 1)), column = f_column(p, 5))
    ])
  else:
    p[0] = Node('condicional', value = 'condicional', children = [
      Node(str(p[1]), value = str(p[1]), line = (p.lineno(1) - (total_lines - 1)), column = f_column(p, 1)),
      p[2],
      Node(str(p[3]), value = str(p[3]), line = (p.lineno(3) - (total_lines - 1)), column = f_column(p, 3)),
      p[4],
      Node(str(p[5]), value = str(p[5]), line = (p.lineno(5) - (total_lines - 1)), column = f_column(p, 5)),
      p[6],
      Node(str(p[7]), value = str(p[7]), line = (p.lineno(7) - (total_lines - 1)), column = f_column(p, 7))
    ])

def p_repita(p):
  '''
    repita : REPITA corpo ATE expressao
  '''

  p[0] = Node('repita', value = 'repita', children = [
    Node(str(p[1]), value = str(p[1]), line = (p.lineno(1) - (total_lines - 1)), column = f_column(p, 1)),
    p[2],
    Node(str(p[3]), value = str(p[3]), line = (p.lineno(3) - (total_lines - 1)), column = f_column(p, 3)),
    p[4]
  ])

def p_atribuicao(p):
  '''
    atribuicao : var ATRIBUICAO expressao
  '''

  p[0] = Node('atribuicao', value = 'atribuicao', children = [
    p[1],
    Node(str(p[2]), value = str(p[2]), line = (p.lineno(2) - (total_lines - 1)), column = f_column(p, 2)),
    p[3]
  ])

def p_leia(p):
  '''
    leia : LEIA ABRE_PARENTESES var FECHA_PARENTESES
  '''

  p[0] = Node('leia', value = 'leia', children = [
    Node(str(p[1]), value = str(p[2]), line = (p.lineno(1) - (total_lines - 1)), column = f_column(p, 1)),
    Node(str(p[2]), value = str(p[2]), line = (p.lineno(2) - (total_lines - 1)), column = f_column(p, 2)),
    p[3],
    Node(str(p[4]), value = str(p[4]), line = (p.lineno(4) - (total_lines - 1)), column = f_column(p, 4))
  ])

def p_escreva(p):
  '''
    escreva : ESCREVA ABRE_PARENTESES expressao FECHA_PARENTESES
  '''

  p[0] = Node('escreva', value = 'escreva', children = [
    Node(str(p[1]), value = str(p[1]), line = (p.lineno(1) - (total_lines - 1)), column = f_column(p, 1)),
    Node(str(p[2]), value = str(p[2]), line = (p.lineno(2) - (total_lines - 1)), column = f_column(p, 2)),
    p[3],
    Node(str(p[4]), value = str(p[4]), line = (p.lineno(4) - (total_lines - 1)), column = f_column(p, 4))
  ])

def p_retorna(p):
  '''
    retorna : RETORNA ABRE_PARENTESES expressao FECHA_PARENTESES
  '''

  p[0] = Node('retorna', value = 'retorna', children = [
    Node(str(p[1]), value = str(p[1]), line = (p.lineno(1) - (total_lines - 1)), column = f_column(p, 1)),
    Node(str(p[2]), value = str(p[2]), line = (p.lineno(2) - (total_lines - 1)), column = f_column(p, 2)),
    p[3],
    Node(str(p[4]), value = str(p[4]), line = (p.lineno(4) - (total_lines - 1)), column = f_column(p, 4))
  ])

def p_expressao(p):
  '''
    expressao : expressao_logica
              | atribuicao
  '''

  p[0] = Node('expressao', value = 'expressao', children = [p[1]])

def p_expressao_logica(p):
  '''
    expressao_logica : expressao_simples
                      | expressao_logica operador_logico expressao_simples
  '''

  if(len(p) == 4):
    p[0] = Node('expressao_logica', value = 'expressao_logica', children = [
      p[1],
      p[2],
      p[3]
    ])
  else:
    p[0] = Node('expressao_logica', value = 'expressao_logica', children = [p[1]])

def p_expressao_simples(p):
  '''
    expressao_simples : expressao_aditiva
                      | expressao_simples operador_relacional expressao_aditiva
  '''

  if(len(p) == 4):
    p[0] = Node('expressao_simples', value = 'expressao_simples', children = [
      p[1],
      p[2],
      p[3]
    ])
  else:
    p[0] = Node('expressao_simples', value = 'expressao_simples', children = [p[1]])

def p_expressao_aditiva(p):
  '''
    expressao_aditiva : expressao_multiplicativa
                      | expressao_aditiva operador_soma expressao_multiplicativa
  '''

  if(len(p) == 4):
    p[0] = Node('expressao_aditiva', value = 'expressao_aditiva', children = [
      p[1],
      p[2],
      p[3]
    ])
  else:
    p[0] = Node('expressao_aditiva', value = 'expressao_aditiva', children = [p[1]])

def p_expressao_multiplicativa(p):
  '''
    expressao_multiplicativa : expressao_unaria
                              | expressao_multiplicativa operador_multiplicacao expressao_unaria
  '''

  if(len(p) == 4):
    p[0] = Node('expressao_multiplicativa', value = 'expressao_multiplicativa', children = [
      p[1],
      p[2],
      p[3]
    ])
  else:
    p[0] = Node('expressao_multiplicativa', value = 'expressao_multiplicativa', children = [p[1]])

def p_expressao_unaria(p):
  '''
    expressao_unaria : fator
                      | operador_soma fator
                      | operador_negacao fator
  '''

  if(len(p) == 3):
    p[0] = Node('expressao_unaria', value = 'expressao_unitaria', children = [
      p[1],
      p[2]
    ])
  else:
    p[0] = Node('expressao_unaria', value = 'expressao_unitaria', children = [p[1]])

def p_operador_relacional(p):
  '''
    operador_relacional : MENOR
                        | MAIOR
                        | IGUAL
                        | DIFERENTE
                        | MENOR_IGUAL
                        | MAIOR_IGUAL
  '''

  p[0] = Node('operador_relacional', value = 'operador_relacional', children = [
    Node(str(p[1]), value = str(p[1]), line = (p.lineno(1) - (total_lines - 1)), column = f_column(p, 1))
  ])

def p_operador_soma(p):
  '''
    operador_soma : ADICAO
                  | SUBTRACAO
  '''

  p[0] = Node('operador_soma', value = 'operador_soma', children = [
    Node(str(p[1]), value = str(p[1]), line = (p.lineno(1) - (total_lines - 1)), column = f_column(p, 1))
  ])

def p_operador_logico(p):
  '''
    operador_logico : E_LOGICO
                    | OU_LOGICO
  '''

  p[0] = Node('operador_logico', value = 'operador_logico', children = [
    Node(str(p[1]), value = str(p[1]), line = (p.lineno(1) - (total_lines - 1)), column = f_column(p, 1))
  ])

def p_operador_negacao(p):
  '''
    operador_negacao : NEGACAO
  '''

  p[0] = Node('operador_negacao', value = 'operador_negacao', children = [
    Node(str(p[1]), value = str(p[1]), line = (p.lineno(1) - (total_lines - 1)), column = f_column(p, 1))
  ])

def p_operador_multiplicacao(p):
  '''
    operador_multiplicacao : MULTIPLICACAO
                            | DIVISAO
  '''

  p[0] = Node('operador_multiplicacao', value = 'operador_multiplicacao', children = [
    Node(str(p[1]), value = str(p[1]), line = (p.lineno(1) - (total_lines - 1)), column = f_column(p, 1))
  ])

def p_fator(p):
  '''
    fator : ABRE_PARENTESES expressao FECHA_PARENTESES
          | var
          | chamada_funcao
          | numero
  '''

  if(len(p) == 4):
    p[0] = Node('fator', value = 'fator', children = [
      Node(str(p[1]), value = str(p[1]), line = (p.lineno(1) - (total_lines - 1)), column = f_column(p, 1)),
      p[2],
      Node(str(p[3]), value = str(p[3]), line = (p.lineno(3) - (total_lines - 1)), column = f_column(p, 3))
    ])
  else:
    p[0] = Node('fator', value = 'fator', children = [p[1]])
  
def p_numero(p):
  '''
    numero : NUM_INTEIRO
            | NUM_PONTO_FLUTUANTE
            | NUM_NOTACAO_CIENTIFICA
  '''

  p[0] = Node('numero', value = 'numero', children = [
    Node(str(p[1]), value = p[1], line = (p.lineno(1) - (total_lines - 1)), column = f_column(p, 1))
  ])

def p_chamada_funcao(p):
  '''
    chamada_funcao : ID ABRE_PARENTESES lista_argumentos FECHA_PARENTESES
  '''

  p[0] = Node('chamada_funcao', value = 'chamada_funcao', children = [
    Node(str(p[1]), value = str(p[1]), line = (p.lineno(1) - (total_lines - 1)), column = f_column(p, 1)),
    Node(str(p[2]), value = str(p[2]), line = (p.lineno(2) - (total_lines - 1)), column = f_column(p, 2)),
    p[3],
    Node(str(p[4]), value = str(p[4]), line = (p.lineno(4) - (total_lines - 1)), column = f_column(p, 4))
  ])


def p_lista_argumentos(p):
  '''
    lista_argumentos : lista_argumentos VIRGULA expressao
                      | expressao
                      | vazio
  '''

  if(len(p) == 4):
    p[0] = Node('lista_argumentos', value = 'lista_argumentos', children = [
      p[1],
      Node(str(p[2]), value = str(p[2]), line = (p.lineno(2) - (total_lines - 1)), column = f_column(p, 2)),
      p[3]
    ])
  else:
    if(p[1] is not None):
      p[0] = Node('lista_argumentos', value = 'lista_argumentos', children = [p[1]])
    else:
      p[0] = Node('lista_argumentos', value = 'lista_argumentos')

def p_vazio(p):
  '''
    vazio : 
  '''
  pass


#### Errors Section ####

# def p_chamada_funcao_error(p):
#   global success
#   success = False
#   '''
#     chamada_funcao : ID ABRE_PARENTESES error FECHA_PARENTESES
#   '''
#   print("Erro lista de argumentos da chamada de funcao")
#   exit(1)


def p_error(p):
  global success
  success = False

  if p:
    print('Sintaxe Inválida do token \'' + str(p.value) + '\' em ' + str(p.lineno) + ':' + str(lex.f_column(p)))
  else:
    print('Sintaxe Inválida da saída')


yacc.yacc()

def parser(data, file_num_lines):
  global total_lines
  total_lines = file_num_lines
  tree = yacc.parse(data, tracking = True)

  return tree, success