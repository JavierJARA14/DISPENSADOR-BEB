#analizador Lexico
import ply.lex as lex

lista_errores_lexicos = []
errores_Desc = []

def limpiar_errores_lex():
    global lista_errores_lexicos
    lista_errores_lexicos = []
    global errores_Desc
    errores_Desc = []

reservadas = {
    'BEGIN':'BEGIN',
    'END':'END',
    'FOR':'FOR',
    'WHILE':'WHILE',
    'ELSE':'ELSE',
    'int':'int',
    'real':'real',
    'bool':'bool',
    'stg':'stg',
    'SMS':'SMS',
    'FUN':'FUN',
    'TRUE':'TRUE',
    'FALSE':'FALSE',
    'SLOT':'SLOT',
    'CA':'CA',
    'moveTo':'moveTo',
    'glassPosition':'glassPosition',
    'gateOpen':'gateOpen',
    'GATE': 'GATE'
}

tokens = [
    'ID',
    'NUMERO',
    'REAL',
    'SUMA',
    'ASIGNACION',
    'RESTA',
    'DIVISION',
    'MULTIPLICACION',
    'IGUAL',
    'DIFERENTE',
    'MAYORQUE',
    'MENORQUE',
    'MENORIGUAL',
    'MAYORIGUAL',
    'PUNTO',
    'COMA',
    'DOSPUNTOS',
    'PUNTOCOMA',
    'COMILLASIMPLE',
    'COMILLADOBLE',
    'PARENTESIS_A',
    'PARENTESIS_B',
    'LLAVE_A',
    'LLAVE_C',
    'CORCHETE_A',
    'CORCHETE_B',
    'MASMAS',
    'MENOSMENOS',
    'AND',
    'OR',
    'NOT',
    'CADENA',
    'BEGIN',
    'END',
    'TRUE',
    'FALSE',
    'IMPORT',
    'FUN',
    'FROM',
    'WHILE',
    'FOR',
    'IF',
    'ELSE',
    'RETURN',
    'DESTROY', 
    'ONOFF',
    'SMS',
    'DSEN',
    'DLED',
    'GVS',
    'real',
    'int',
    'bool',
    'stg',
    'moveTo',
    'glassPosition',
    'gateOpen',
    'SLOT',
    'CA',
    'GATE',
    'BE_OPEN',
    'BE_CLOSE',
    'SETGATE'
]

t_ignore = ' \t'

t_SUMA = r'\+'
t_ASIGNACION = r'='
t_RESTA = r'\-'
t_DIVISION = r'/'
t_MULTIPLICACION = r'\*'
t_IGUAL = r'=='
t_DIFERENTE = r'!='
t_MAYORQUE = r'>'
t_MENORQUE = r'<'
t_MAYORIGUAL = r'>='
t_MENORIGUAL = r'<='
t_PUNTO = r'\.'
t_COMA = r'\,'
t_DOSPUNTOS = r'\:'
t_PUNTOCOMA = r'\;'
t_COMILLASIMPLE = r'\''
t_COMILLADOBLE = r'\"'
t_PARENTESIS_A = r'\('
t_PARENTESIS_B = r'\)'
t_LLAVE_A = r'\{'
t_LLAVE_C = r'\}'
t_CORCHETE_A = r'\['
t_CORCHETE_B = r'\]'
t_MASMAS = r'\+\+'
t_MENOSMENOS = r'\-\-'
t_AND = r'\&\&'
t_OR = r'\|{2}'
t_NOT = r'\!'

contador = 0

def t_SALTOLINEA(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_CADENA(t):
    r'\#.*?\#'
    t.type = 'CADENA'
    return t

def t_BE_OPEN(t):
    r'BE_OPEN'
    return t

def t_BE_CLOSE(t):
    r'BE_CLOSE'
    return t

def t_SETGATE(t):
    r'SETGATE'
    return t

# Token para IF
def t_SI(t):
    r'IF'
    t.type = 'IF'
    return t

# Identificadores no válidos
def t_IDError(t):
    r'\d+[a-zA-ZñÑ]+[a-zA-Z0-9ñÑ]*'
    global lista_errores_lexicos
    lista_errores_lexicos.append(t.lineno)
    global errores_Desc
    errores_Desc.append("Identificador no válido en la línea " + str(t.lineno))
    # t.lexer.skip(1)

# Expresión regular para identificadores (nombres de variables, funciones, etc.)
def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    if t.value in reservadas:
        t.type = reservadas.get(t.value, 'ID')
    return t

# Rango de valores para int y real (32 bits)
INT_MIN = -2147483648
INT_MAX = 2147483647
REAL_MIN = -3.4e38
REAL_MAX = 3.4e38

# Validar rango de valores para tipo int
def validar_int(valor):
    if valor < INT_MIN or valor > INT_MAX:
        return False
    return True

# Validar rango de valores para tipo real
def validar_real(valor):
    if valor < REAL_MIN or valor > REAL_MAX:
        return False
    return True


def t_COMENTARIO(t):
    r'\/\/(.*?)\/\/'
    pass

def t_REAL(t):
    r'-?(\d+\.\d+|\.\d+)'
    t.value = float(t.value)
    if not validar_real(t.value):
        global lista_errores_lexicos
        lista_errores_lexicos.append(t.lineno)
        global errores_Desc
        errores_Desc.append(f"Valor real fuera de rango en la línea {t.lineno}: {t.value}")
        t.value = None
    return t

def t_NUMERO(t):
    r'-?\d+'
    t.value = int(t.value)
    if not validar_int(t.value):
        global lista_errores_lexicos
        lista_errores_lexicos.append(t.lineno)
        global errores_Desc
        errores_Desc.append(f"Valor entero fuera de rango en la línea {t.lineno}: {t.value}")
        t.value = None
    return t

def t_TRUE(t):
    r'TRUE'
    t.type = 'TRUE'
    return t

def t_FALSE(t):
    r'FALSE'
    t.type = 'FALSE'
    return t

def t_error(t):
    global lista_errores_lexicos
    lista_errores_lexicos.append(t.lineno)
    global errores_Desc
    errores_Desc.append(f"Símbolo no válido '{t.value[0]}' en la línea {t.lineno}")
    t.lexer.skip(1)

# Build the lexer
lexer = lex.lex()

def analisis(cadena):
    lexer.input(cadena)
    tokens = []
    # Inicia el número de línea en 1
    lexer.lineno = 1
    for tok in lexer:
        columna = tok.lexpos - cadena.rfind('\n', 0, tok.lexpos)
        tokens.append((tok.value, tok.type, tok.lineno, columna))
    return tokens