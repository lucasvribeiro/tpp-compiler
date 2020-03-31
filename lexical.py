import ply.lex as lex

success = True

reserved = { # Reserved Words in T++
  # 'principal': 'PRINCIPAL',
  'retorna': 'RETORNA',
  'leia': 'LEIA',
  'escreva': 'ESCREVA',
  'se': 'SE',
  'então': 'ENTAO',
  'senão': 'SENAO',
  'repita': 'REPITA',
  'até': 'ATE',
  'fim': 'FIM',
  'inteiro': 'INTEIRO',
  'flutuante': 'FLUTUANTE'
}

tokens = [
  # Numbers (Type of)
  'NUM_NOTACAO_CIENTIFICA',
  'NUM_PONTO_FLUTUANTE',
  'NUM_INTEIRO',

  'ID',
  'ATRIBUICAO',

  # Language Symbols
  'DOIS_PONTOS',
  'VIRGULA',
  'ABRE_PARENTESES',
  'FECHA_PARENTESES',
  'ABRE_COLCHETES',
  'FECHA_COLCHETES',

  # Operators
  'ADICAO',
  'SUBTRACAO',
  'MULTIPLICACAO',
  'DIVISAO',
  'IGUAL',
  'DIFERENTE',
  'MENOR_IGUAL',
  'MAIOR_IGUAL',
  'MENOR',
  'MAIOR',

  # Logical
  'E_LOGICO',
  'OU_LOGICO',
  'NEGACAO'
] + list(reserved.values())

t_ANY_ignore = ' \t\r\f\v'

# Regular Expressions
def t_ATRIBUICAO(t):
  r':='
  return t

def t_DOIS_PONTOS(t):
  r':'
  return t

def t_VIRGULA(t):
  r','
  return t

def t_ABRE_PARENTESES(t):
  r'\('
  return t
  
def t_FECHA_PARENTESES(t):
  r'\)'
  return t

def t_ABRE_COLCHETES(t):
  r'\['
  return t

def t_FECHA_COLCHETES(t):
  r'\]'
  return t

def t_ADICAO(t):
  r'\+'
  return t

def t_SUBTRACAO(t):
  r'\-'
  return t

def t_MULTIPLICACAO(t):
  r'\*'
  return t

def t_DIVISAO(t):
  r'\/'
  return t

def t_IGUAL(t):
  r'\='
  return t

def t_DIFERENTE(t):
  r'\!'
  return t

def t_MENOR_IGUAL(t):
  r'<='
  return t

def t_MAIOR_IGUAL(t):
  r'>='
  return t

def t_MENOR(t):
  r'<'
  return t

def t_MAIOR(t):
  r'>'
  return t

def t_E_LOGICO(t):
  r'\&\&'
  return t

def t_OU_LOGICO(t):
  r'\|\|'
  return t

def t_NEGACAO(t):
  r'\<\>'
  return t

# Other (More Specific) Regular Expressions
def t_NUM_NOTACAO_CIENTIFICA(t):
  r'(-|\+)?[\d+]+\.?[\d+]*(e|E)(-|\+)?[\d+]+'
  t.value = float(t.value)
  return t

def t_NUM_PONTO_FLUTUANTE(t):
  r'(-|\+)?[\d+]+\.[\d+]*'
  t.value = float(t.value)
  return t

def t_NUM_INTEIRO(t):
  r'(-|\+)?\d+'
  t.value = int(t.value)
  return t

def t_ID(t):
  r'[a-zA-Z_áàâãéèêíïóôõöúçñÁÀÂÃÉÈÍÏÓÔÕÖÚÇÑ][a-zA-Z_0-9áàâãéèêíïóôõöúçñÁÀÂÃÉÈÍÏÓÔÕÖÚÇÑ]*'
  t.type = reserved.get(t.value, 'ID')
  return t

def t_comment(t):
  r'(\{(.|\n)*?\})|(\{(.|\n)*?)$'
  t.lexer.lineno += len(t.value.split('\n')) - 1
  pass

def t_ANY_error(t):
	global success
	success = False

	print('Caracter Inválido \'' + t.value[0] + '\' em ' + str(t.lineno) + ':' + str(f_column(t)))
	t.lexer.skip(1)

def f_column(token):
  input = token.lexer.lexdata
  line_start = input.rfind('\n', 0, token.lexpos) + 1
  return (token.lexpos - line_start) + 1

def t_ANY_newline(t):
  r'\n+'
  t.lexer.lineno += len(t.value)

lexer = lex.lex()

def tokenizator(data):
  lexer.input(data)

  tokens = []

  while True:
    generated_token = lexer.token()
    if not generated_token: break

    tokens.append({
      'token_itself': generated_token,
      'token': generated_token.type,
      'value': generated_token.value,
      'line': generated_token.lineno,
      'column': f_column(generated_token)
    })

  return tokens, success