#analizador Sintactico
import ply.yacc as yacc
from AnalizadorLexico import tokens  # Importa tokens desde archivo léxico
import sys
import io
from TablaSimbolos import SymbolTable
from AnalizadorSemantico import *

def limpiar_errores():
    global lista_errores_sintacticos
    lista_errores_sintacticos = []
    global errores_Sinc_Desc
    errores_Sinc_Desc = []
    global lista_errores_semanticos
    lista_errores_semanticos = []
    global errores_Sem_Desc
    errores_Sem_Desc = []
    global tabla_simbolos

global lista_errores_sintacticos
lista_errores_sintacticos = []
global errores_Sinc_Desc
errores_Sinc_Desc = []
global lista_errores_semanticos
lista_errores_semanticos = []
global errores_Sem_Desc
errores_Sem_Desc = []
codigo_intermedio = []  # Lista para almacenar las instrucciones IR
tabla_temporales = {}  # clave: expresión, valor: temporal

global tabla_simbolos
tabla_simbolos = SymbolTable()
contador_temporales = 0
contador_etiquetas = 0

linea = 0

precedence = (
    ('left', 'SUMA', 'RESTA'),
    ('left', 'MULTIPLICACION', 'DIVISION'),
    ('left', 'IGUAL', 'DIFERENTE'),
    ('left', 'MENORQUE', 'MENORIGUAL', 'MAYORQUE', 'MAYORIGUAL'),
)

# Programa principal
def p_programa(p):
    """
    programa : gate_declaracion BEGIN bloque_codigo END
    """
    global codigo_intermedio
    for instr in p[3]:   # ← p[3] contiene la lista de todas las instrucciones acumuladas
        codigo_intermedio.append(instr)
    p[0] = ('programa', p[3])


# Bloque de código
def p_bloque_codigo(p):
    """
    bloque_codigo : LLAVE_A lista_declaraciones LLAVE_C
    """
    p[0] = p[2]

# Bloque de código funciones
def p_bloque_codigo_funcion(p):
    """
    bloque_codigo_funcion : LLAVE_A lista_declaraciones_funciones LLAVE_C
    """
    p[0] = ('bloque_codigo_funcion', p[2])
    
    if p[3] == 'LLAVE_C':
        tabla_simbolos.set_scope("global")

# Lista de declaraciones
def p_lista_declaraciones(p):
    """
    lista_declaraciones : lista_declaraciones lista_declaraciones
                        | declaracion
                        | si
                        | mientras
                        | for_loop
                        | graImport
                        | funcion
                        | mover
                        | posicion
                        | abrir
                        | llamadafunc
                        | imprimir
                        | gate_instruccion
    """
    if len(p) == 3:
        p[0] = p[1] + p[2]  # ← concatenamos listas directamente
    else:
        p[0] = p[1]         # ← si es una sola lista, simplemente se pasa

# Lista de declaraciones funciones
def p_lista_declaraciones_funciones(p):
    """
    lista_declaraciones_funciones : lista_declaraciones_funciones lista_declaraciones_funciones
                        | declaracion_funcion
                        | si
                        | mientras
                        | for_loop
                        | graImport
                        | funcion
                        | mover
                        | posicion
                        | abrir
                        | llamadafunc
                        | imprimir
                        | gate_instruccion
    """
    if len(p) == 3:
        p[0] = p[1] + p[2]  # ← concatenamos listas directamente
    else:
        p[0] = p[1]         # ← si es una sola lista, simplemente se pasa

#DEFINIR CADENAS
#----------- Validar cadenas dentro de las comillas del SMS -------------
def p_listaExpresiones(p):
    """
    lista_expresiones : CADENA 
                      | ID
                      | lista_expresiones SUMA CADENA
                      | lista_expresiones SUMA ID              

    """

    if len(p) == 2:
        p[0] = [p[1]]
    else: 
        p[0]=p[1] + [p[3]]
#---------------------Imprimir cadenas----------------
def p_imprimirPantalla(p):
    """
    imprimir : SMS PARENTESIS_A lista_expresiones PARENTESIS_B PUNTOCOMA            
    """
    if len(p)==8:
        for expresion in p[4]:  # p[4] contiene la lista de expresiones
         print(expresion)
        p[0]="Imprimir",p[4]
        print(p[3])
    else:
        print(p[3])
        p[0]="imprimir",p[3]

#-----------------------------------------------------------------------#
def p_imprimirPantallaError(p):
    """
    imprimir : SMS PARENTESIS_A lista_expresiones PARENTESIS_B 
                          
    """
    errores_Sinc_Desc.append("Error sintactico en la linea: "+str(p.lineno(2)-linea)+
                            "\nFalta punto y coma cerca de: "+"'"+p[4]+"'"+
                             "\nSe espera SMS PARENTESIS_A lista_expresiones PARENTESIS_B PUNTOCOMA"+
                             "\n                                                          ^^^^^^^^^"+
                             "\nPruebe con: "+str(p[1])+str(p[2])+str(p[3])+str(p[4])+";")
    
def p_imprimirPantallaError2(p):
    """
    imprimir : SMS PARENTESIS_A lista_expresiones PUNTOCOMA
                          
    """
    errores_Sinc_Desc.append("Error sintactico en la linea: "+str(p.lineno(2)-linea)+
                             "\nFalta parentesis B (')') cerca de: "+"'"+str(p[3])+"'"+
                             "\nSe espera SMS PARENTESIS_A lista_expresiones PARENTESIS_B PUNTOCOMA"+
                             "\n                                             ^^^^^^^^^^^^"+
                             "\nPruebe con: "+str(p[1])+str(p[2])+str(p[3])+")"+str(p[4]))

def p_imprimirPantallaError3(p):
    """
    imprimir : SMS PARENTESIS_A PARENTESIS_B PUNTOCOMA
                          
    """
    errores_Sinc_Desc.append("Error sintactico en la linea: "+str(p.lineno(2)-linea)+
                             "\nSMS Sin argumentos cerca de: "+"'"+str(p[2])+"'"+
                             "\nSe espera SMS PARENTESIS_A lista_expresiones PARENTESIS_B PUNTOCOMA"+
                             "\n                           ^^^^^^^^^^^^^^^^^"+
                             "\nPruebe con: "+str(p[1])+str(p[2])+"ExpresionesAImprimir"+str(p[3])+str(p[4]))

def p_imprimirPantallaError4(p):
    """
    imprimir : SMS lista_expresiones PARENTESIS_B PUNTOCOMA
                          
    """
    errores_Sinc_Desc.append("Error sintactico en la linea: "+str(p.lineno(2)-linea)+
                             "\nFalta parentesis A ('()') cerca de: "+"'"+str(p[2])+"'"+
                             "\nSe espera SMS PARENTESIS_A lista_expresiones PARENTESIS_B PUNTOCOMA"+
                             "\n              ^^^^^^^^^^^^"+
                             "\nPruebe con: "+str(p[1])+"("+str(p[2])+str(p[3])+str(p[4]))
 
def p_imprimirPantallaError5(p):
    """
    imprimir : PARENTESIS_A lista_expresiones PARENTESIS_B PUNTOCOMA
                          
    """
    errores_Sinc_Desc.append("Error sintactico en la linea: "+str(p.lineno(2)-linea)+
                             "\nPosible Funcion de SMS cerca de: "+"'"+str(p[2])+"'"+
                             "\nSe espera SMS PARENTESIS_A lista_expresiones PARENTESIS_B PUNTOCOMA"+
                             "\n          ^^^"+
                             "\nPruebe con: SMS "+str(p[1])+str(p[2])+str(p[3])+str(p[4]))

def nueva_temporal():
    global contador_temporales
    contador_temporales += 1
    return f"t{contador_temporales}"
      
def nueva_etiqueta():
    global contador_etiquetas
    contador_etiquetas += 1
    return f"L{contador_etiquetas}"

def buscar_temporal(identificador):
    return tabla_temporales.get(identificador, None)

def registrar_temporal(identificador, temporal):
    tabla_temporales[identificador] = temporal

        
def imprimirIT():
    print("\nCódigo Intermedio Generado:")
    for instr in codigo_intermedio:
        print(instr)

def obtener_codigo_intermedio():
    codigo = "\nCódigo Intermedio Generado:\n"
    for instr in codigo_intermedio:
        codigo += str(instr) + "\n"  # Concatenar cada instrucción con un salto de línea
    return codigo


def p_declaracion(p):
    """
    declaracion : tipo ID ASIGNACION expresion PUNTOCOMA
    """
    # Semántica y verificación
    if tabla_simbolos.insertar_variable(p[2], p[1], p[4], 'global'):
        errores_Sem_Desc.append(f"Error semántico en la línea {p.lineno(2)-linea}: La variable '{p[2]}' ya ha sido declarada")
    else:
        try:
            verificar_asignacion(tabla_simbolos, p[2], str(p[4]), p.lineno(2)-linea)
        except Exception as e:
            errores_Sem_Desc.append(str(e))

    # Código intermedio
    temp = nueva_temporal()
    instrucciones = [
        f"{temp} = {p[4]}",
        f"{p[2]} = {temp}"
    ]
    tabla_temporales.append
    p[0] = instrucciones

def p_declaracion_funcion(p):
    """
    declaracion_funcion : tipo ID ASIGNACION expresion PUNTOCOMA
    """
    if tabla_simbolos.insertar_variable(p[2], p[1], p[4], 'nulo'):
        errores_Sem_Desc.append(f"Error semántico en la línea {p.lineno(2)-linea}: La variable '{p[2]}' ya ha sido declarada")
    else:
        try:
            verificar_asignacion(tabla_simbolos, p[2], str(p[4]), p.lineno(2)-linea)
        except Exception as e:
            errores_Sem_Desc.append(str(e))

    temp = nueva_temporal()
    instrucciones = [
        f"{temp} = {p[4]}",
        f"{p[2]} = {temp}"
    ]

    p[0] = instrucciones


def p_declaracionsintipo(p):
    """
    declaracion : ID ASIGNACION expresion PUNTOCOMA
    """
    try:
        verificar_asignacion(tabla_simbolos, p[1], str(p[3]), p.lineno(2)-linea)
        verificar_ambito(tabla_simbolos, p[1], p.lineno(2)-linea)

        temp = nueva_temporal()
        instrucciones = [
            f"{temp} = {p[3]}",
            f"{p[1]} = {temp}"
        ]

        p[0] = instrucciones
    except Exception as e:
        errores_Sem_Desc.append(str(e))
        p[0] = []  # En caso de error, devolvemos lista vacía

#-----------------Crear Slot------------------------------
def p_declaracion_crearObj(p):
    '''declaracion : ID ASIGNACION SLOT CORCHETE_A NUMERO CORCHETE_B PUNTOCOMA'''

def p_gate_declaracion(p):
    """
    gate_declaracion  : GATE SETGATE CADENA PUNTOCOMA         
    """
    global codigo_intermedio

    codigo_intermedio.append(f"GATE SETGATE {p[3]}")

    p[0] = ('gate_declaracion', p[3])


def p_gate_instruccion(p):
    """
    gate_instruccion  : GATE PUNTO gate_options PUNTOCOMA         
    """
    instruccion = f"GATE.{p[3]}"
    p[0] = [instruccion]
    
def p_gate_options(p):
    """
    gate_options  : BE_OPEN
                  | BE_CLOSE           
    """
    p[0] = p[1]
    
#-----------------Arreglo------------------------------
def p_declaracion_crearArreglo(p):
    '''declaracion : tipo ID ASIGNACION CA CORCHETE_A NUMERO CORCHETE_B PUNTOCOMA
                   | tipo ID ASIGNACION CA CORCHETE_A ID CORCHETE_B PUNTOCOMA'''
    
    if tabla_simbolos.declarar_arreglo(p[2], p[1], p[6],'global'):
        errores_Sem_Desc.append(f"Error semántico en la línea {p.lineno(2)-linea}: el arreglo '{p[2]}' ya ha sido declarado")
    else:
        if p.slice[5].type == 'ID':
            try:
                verificar_asignacion_arreglo(tabla_simbolos, p[6], 'ID', p.lineno(2)-linea)
            except Exception as e:
                errores_Sem_Desc.append(str(e))
        else:
            try:
                verificar_asignacion_arreglo(tabla_simbolos, p[6], 'VALOR', p.lineno(2)-linea)
            except Exception as e:
                errores_Sem_Desc.append(str(e))

    # Código intermedio para la declaración de arreglo
    temp = nueva_temporal()
    instrucciones = [
        f"{temp} = {p[6]}",
        f"DECLARE_ARRAY {p[2]}, {temp}"
    ]
    p[0] = instrucciones

                

def p_declaracion_AsignarArreglo(p):
    '''declaracion : ID CORCHETE_A NUMERO CORCHETE_B ASIGNACION expresion PUNTOCOMA
                   | ID CORCHETE_A NUMERO CORCHETE_B ASIGNACION TRUE PUNTOCOMA
                   | ID CORCHETE_A NUMERO CORCHETE_B ASIGNACION FALSE PUNTOCOMA
                   | ID CORCHETE_A ID CORCHETE_B ASIGNACION expresion PUNTOCOMA
                   | ID CORCHETE_A ID CORCHETE_B ASIGNACION TRUE PUNTOCOMA
                   | ID CORCHETE_A ID CORCHETE_B ASIGNACION FALSE PUNTOCOMA
    '''
    if p.slice[3].type == 'ID':
            try:
                verificar_asignacion_arreglo(tabla_simbolos, p[3], 'ID',p.lineno(2)-linea)
                valor_id = valor_identificador(tabla_simbolos, p[3])
                verificar_asignacion_arreglo2(tabla_simbolos, p[1], str(p[6]), valor_id, p.lineno(2)-linea)
                verificar_ambito(tabla_simbolos, p[1], p.lineno(2)-linea)
                verificar_ambito(tabla_simbolos, p[3], p.lineno(2)-linea)
                tabla_simbolos.valor_arreglo(p[1], p[3], valor_id, 'global')
            except Exception as e:
                errores_Sem_Desc.append(str(e))
    else:
        try:
            verificar_asignacion_arreglo2(tabla_simbolos, p[1], str(p[6]), p[3], p.lineno(2)-linea)
            verificar_ambito(tabla_simbolos, p[1], p.lineno(2)-linea)
            tabla_simbolos.valor_arreglo(p[1], p[3], p[6], 'global')
        except Exception as e:
            errores_Sem_Desc.append(str(e))
    
    # Código intermedio para la asignación en arreglo
    temp = nueva_temporal()
    instrucciones = [
        f"{temp} = {p[6]}",
        f"{p[1]}[{p[3]}] = {temp}"
    ]
    p[0] = instrucciones

def p_declaracion_crearArreglo_funcion(p):
    '''declaracion_funcion : tipo ID ASIGNACION CA CORCHETE_A NUMERO CORCHETE_B PUNTOCOMA
                           | tipo ID ASIGNACION CA CORCHETE_A ID CORCHETE_B PUNTOCOMA'''
    if tabla_simbolos.declarar_arreglo(p[2], p[1], p[6],'nulo'):
        errores_Sem_Desc.append(f"Error semántico en la línea {p.lineno(2)-linea}: el arreglo '{p[2]}' ya ha sido declarado")
    else:
        if p.slice[5].type == 'ID':
            try:
                verificar_asignacion_arreglo(tabla_simbolos, p[6], 'ID', p.lineno(2)-linea)
            except Exception as e:
                errores_Sem_Desc.append(str(e))
        else:
            try:
                verificar_asignacion_arreglo(tabla_simbolos, p[6], 'VALOR', p.lineno(2)-linea)
            except Exception as e:
                errores_Sem_Desc.append(str(e))

def p_declaracion_AsignarArreglo_funcion(p):
    '''declaracion_funcion : ID CORCHETE_A NUMERO CORCHETE_B ASIGNACION expresion PUNTOCOMA
                   | ID CORCHETE_A NUMERO CORCHETE_B ASIGNACION TRUE PUNTOCOMA
                   | ID CORCHETE_A NUMERO CORCHETE_B ASIGNACION FALSE PUNTOCOMA
                   | ID CORCHETE_A ID CORCHETE_B ASIGNACION expresion PUNTOCOMA
                   | ID CORCHETE_A ID CORCHETE_B ASIGNACION TRUE PUNTOCOMA
                   | ID CORCHETE_A ID CORCHETE_B ASIGNACION FALSE PUNTOCOMA
    '''
    if p.slice[3].type == 'ID':
            try:
                verificar_asignacion_arreglo(tabla_simbolos, p[3], 'ID',p.lineno(2)-linea)
                valor_id = valor_identificador(tabla_simbolos, p[3])
                verificar_asignacion_arreglo2(tabla_simbolos, p[1], str(p[6]), valor_id, p.lineno(2)-linea)
                tabla_simbolos.valor_arreglo(p[1], p[3], valor_id, 'nulo')
            except Exception as e:
                errores_Sem_Desc.append(str(e))
    else:
        try:
            verificar_asignacion_arreglo2(tabla_simbolos, p[1], str(p[6]), p[3], p.lineno(2)-linea)
            tabla_simbolos.valor_arreglo(p[1], p[3], p[6], 'nulo')
        except Exception as e:
            errores_Sem_Desc.append(str(e))

# Tipos de datos
def p_tipo(p):
    """
    tipo : int
         | bool
         | stg
         | real
    """
    p[0] = p[1]

# Expresiones
def p_expresion_suma(p):
    'expresion : expresion SUMA expresion'

    operando1 = p[1]
    operando2 = p[3]

    # Si los operandos son identificadores, obtener su valor de la tabla de símbolos
    if isinstance(operando1, str):  # Es un identificador
        operando1 = valor_identificador(tabla_simbolos, operando1)
    
    if isinstance(operando2, str):  # Es un identificador
        operando2 = valor_identificador(tabla_simbolos, operando2)
    
    tipo = TipoValor(operando1)
    tipo2 = TipoValor(operando2)

    # Verificar si los tipos son compatibles
    if tipo == 'bool' or tipo == 'stg' or tipo == None or tipo2 == 'bool' or tipo2 == 'stg' or tipo2 == None:
        errores_Sem_Desc.append(f"Error semántico en la línea {p.lineno(2)-linea}: La operación no es compatible con los tipos {tipo} y {tipo2}")
    else:
        instruccion = f"{operando1} + {operando2}"
        p[0] = instruccion

def p_expresion_resta(p):
    'expresion : expresion RESTA expresion'
    operando1 = p[1]
    operando2 = p[3]

    # Si los operandos son identificadores, obtener su valor de la tabla de símbolos
    if isinstance(operando1, str):
        operando1 = valor_identificador(tabla_simbolos, operando1)
    
    if isinstance(operando2, str):
        operando2 = valor_identificador(tabla_simbolos, operando2)

    tipo = TipoValor(operando1)
    tipo2 = TipoValor(operando2)

    # Verificar si los tipos son compatibles
    if tipo == 'bool' or tipo == 'stg' or tipo == None or tipo2 == 'bool' or tipo2 == 'stg' or tipo2 == None:
        errores_Sem_Desc.append(f"Error semántico en la línea {p.lineno(2)-linea}: La operación no es compatible con los tipos {tipo} y {tipo2}")
    else:
        # Generar la instrucción intermedia
        instruccion = f"{operando1} - {operando2}"
        p[0] = instruccion

def p_expresion_mult(p):
    'expresion : expresion MULTIPLICACION expresion'
    operando1 = p[1]
    operando2 = p[3]

    # Si los operandos son identificadores, obtener su valor de la tabla de símbolos
    if isinstance(operando1, str):
        operando1 = valor_identificador(tabla_simbolos, operando1)
    
    if isinstance(operando2, str):
        operando2 = valor_identificador(tabla_simbolos, operando2)

    tipo = TipoValor(operando1)
    tipo2 = TipoValor(operando2)

    # Verificar si los tipos son compatibles
    if tipo == 'bool' or tipo == 'stg' or tipo == None or tipo2 == 'bool' or tipo2 == 'stg' or tipo2 == None:
        errores_Sem_Desc.append(f"Error semántico en la línea {p.lineno(2)-linea}: La operación no es compatible con los tipos {tipo} y {tipo2}")
    else:
        # Generar la instrucción intermedia
        instruccion = f"{operando1} * {operando2}"
        p[0] = instruccion

def p_expresion_div(p):
    'expresion : expresion DIVISION expresion'
    operando1 = p[1]
    operando2 = p[3]

    # Si los operandos son identificadores, obtener su valor de la tabla de símbolos
    if isinstance(operando1, str):
        operando1 = valor_identificador(tabla_simbolos, operando1)
    
    if isinstance(operando2, str):
        operando2 = valor_identificador(tabla_simbolos, operando2)

    tipo = TipoValor(operando1)
    tipo2 = TipoValor(operando2)

    # Verificar si los tipos son compatibles
    if tipo == 'bool' or tipo == 'stg' or tipo == None or tipo2 == 'bool' or tipo2 == 'stg' or tipo2 == None:
        errores_Sem_Desc.append(f"Error semántico en la línea {p.lineno(2)-linea}: La operación no es compatible con los tipos {tipo} y {tipo2}")
    else:
        # Verificar si no se está dividiendo por cero
        if operando2 == 0:
            errores_Sem_Desc.append(f"Error semántico en la línea {p.lineno(2)-linea}: No se puede dividir por cero")
            p[0] = None  # Devuelve None si ocurre el error
        else:
            # Realizar la operación y comprobar si el resultado es entero
            resultado = operando1 / operando2
            if resultado % 1 == 0:
                resultado = int(resultado)
            p[0] = resultado

def p_expresion_comparacion(p):
    '''
    expresion : expresion MENORQUE expresion
              | expresion MENORIGUAL expresion
              | expresion MAYORQUE expresion
              | expresion MAYORIGUAL expresion
              | expresion IGUAL expresion
              | expresion DIFERENTE expresion
    '''
    # Obtener operandos manteniendo variables
    left = p[1] if isinstance(p[1], str) else str(p[1])
    right = p[3] if isinstance(p[3], str) else str(p[3])
    operador = p[2]
    
    # Manejo especial para valores booleanos literales
    if right == 'FALSE':
        right = 'FALSE'
        tipo_right = 'bool'
    elif right == 'TRUE':
        right = 'TRUE'
        tipo_right = 'bool'
    else:
        tipo_right = obtener_tipo(p[3])
    
    tipo_left = obtener_tipo(p[1])
    
    # Validar compatibilidad de tipos
    if not tipos_compatibles(tipo_left, tipo_right, operador):
        errores_Sem_Desc.append(f"Error semántico en línea {p.lineno(2)}: Tipos incompatibles {tipo_left} y {tipo_right} para operador '{operador}'")
        p[0] = ('error', 'error', 'error', 'error')
    else:
        p[0] = ('comparacion', left, operador, right)

def obtener_tipo(operando):
    """Determina el tipo del operando"""
    if isinstance(operando, str):
        # Si es variable, busca en tabla de símbolos
        simbolo = tabla_simbolos.Buscar(operando)
        return simbolo['type'] if simbolo else None
    elif operando == 'TRUE' or operando == 'FALSE':
        return 'bool'
    else:
        return TipoValor(str(operando))

def tipos_compatibles(tipo1, tipo2, operador):
    """Determina si los tipos son compatibles para la operación"""
    if operador in ['==', '!=']:
        # Para igualdad/desigualdad, permitir:
        # - bool con bool
        # - numérico con numérico
        # - bool con cualquier tipo si es comparación con TRUE/FALSE
        if tipo1 == 'bool' or tipo2 == 'bool':
            return True
        return tipo1 == tipo2 or (tipo1 in ['int', 'float'] and tipo2 in ['int', 'float'])
    else:
        # Operadores relacionales solo para números
        return tipo1 in ['int', 'float'] and tipo2 in ['int', 'float']

def p_expresion(p):
    """
    expresion : PARENTESIS_A expresion PARENTESIS_B
              | ID CORCHETE_A NUMERO CORCHETE_B
              | ID CORCHETE_A ID CORCHETE_B
              | NUMERO
              | REAL
              | CADENA
              | TRUE
              | FALSE
              | posicion
    """
    p[0] = p[1]
    
def p_expresionId(p):
    """
    expresion : ID
    """
    valorVar = tabla_simbolos.Buscar(p[1])
    if valorVar is not None:
        if valorVar['type'] != 'funcion':
            p[0] = p[1]  # Retornamos el nombre de la variable, no su valor
        else:
            p[0] = 'funcion'
    else:
        errores_Sem_Desc.append("Error semántico en la línea " + str(p.lineno(1)-linea) + ": La variable " + p[1] + " no ha sido declarada")

# Operadores
def p_operador(p):
    """
    operador : SUMA
             | RESTA
             | MULTIPLICACION
             | DIVISION
             | IGUAL
             | DIFERENTE
             | MENORQUE
             | MAYORQUE
             | MENORIGUAL
             | MAYORIGUAL
             | AND
             | OR
             | NOT
    """
    if p[1] in ['AND', 'OR']:
        if isinstance(p[2], bool) and isinstance(p[3], bool):
            p[0] = p[1]
        else:
            errores_Sem_Desc.append(f"Error semántico en la línea {p.lineno(1)-linea}: Los operadores lógicos {p[1]} requieren booleanos")
    elif p[1] == 'NOT':
        if isinstance(p[2], bool):
            p[0] = p[1]
        else:
            errores_Sem_Desc.append(f"Error semántico en la línea {p.lineno(1)-linea}: El operador lógico NOT requiere un valor booleano")
    else:
        if isinstance(p[2], (int, float)) and isinstance(p[3], (int, float)):
            p[0] = p[1]
        else:
            errores_Sem_Desc.append(f"Error semántico en la línea {p.lineno(1)-linea}: Los operadores de comparación requieren operandos numéricos (int o float)")

def p_si(p):
    """
    si : IF PARENTESIS_A expresion PARENTESIS_B bloque_codigo
       | IF PARENTESIS_A expresion PARENTESIS_B bloque_codigo ELSE bloque_codigo
    """
    L_falso = nueva_etiqueta()  # Etiqueta para el bloque falso
    L_fin = nueva_etiqueta()    # Etiqueta para el final (común a ambos bloques)

    # 1. Procesar condición
    condicion = p[3]
    cond_instr = []

    # Verificar si la condición es una expresión booleana válida
    if not isinstance(condicion, tuple) or len(condicion) != 4:
        errores_Sem_Desc.append(f"Error semántico en la línea {p.lineno(1)}: La condición del IF debe ser booleana")
        cond_temp = "0"  # Forzar un valor falso si la condición es incorrecta
    else:
        _, izq, op, der = condicion
        cond_temp = nueva_temporal()
        cond_instr = [f"{cond_temp} = {izq} {op} {der}"]  # Generar código de la condición

    # 2. Generar código intermedio para el bloque del IF
    if len(p) == 6:  # IF sin ELSE
        codigo = [
            *cond_instr,
            f"IF_NOT {cond_temp} GOTO {L_falso}",  # Si la condición es falsa, saltar al bloque falso
            *p[5],  # Bloque de código del IF
            f"GOTO {L_fin}",  # Saltar al final del IF
            f"LABEL {L_falso}",  # Etiqueta para el bloque falso
            f"LABEL {L_fin}"  # Etiqueta de fin común
        ]
    else:  # IF con ELSE
        codigo = [
            *cond_instr,
            f"IF_NOT {cond_temp} GOTO {L_falso}",  # Si la condición es falsa, saltar al bloque falso
            *p[5],  # Bloque de código del IF
            f"GOTO {L_fin}",  # Saltar al final del IF
            f"LABEL {L_falso}",  # Etiqueta para el bloque falso
            *p[7],  # Bloque de código del ELSE
            f"LABEL {L_fin}"  # Etiqueta de fin común
        ]
    
    p[0] = codigo  # Asignar el código generado al resultado

def p_siError1(p):
    """
    si : IF PARENTESIS_A expresion  bloque_codigo
       | IF PARENTESIS_A expresion  bloque_codigo ELSE bloque_codigo
    """
    errores_Sinc_Desc.append("Error semántico en la linea "+str(p.lineno(1)-linea)+
                             "\nFalta cerrar el Parentesis (')')"+
                             "\nSe espera: IF PARENTESIS_A expresion PARENTESIS_B BloqueCodigo"
                             +"\n                                    ^^^^^^^^^^^^")

def p_siError2(p):
    """
    si : IF  expresion PARENTESIS_B bloque_codigo
       | IF  expresion PARENTESIS_B bloque_codigo ELSE bloque_codigo
    """
    errores_Sinc_Desc.append("Error semántico en la linea "+str(p.lineno(1)-linea)+
                             "\nFalta abrir el Parentesis ('(')"+
                             "\nSe espera: IF PARENTESIS_A expresion PARENTESIS_B BloqueCodigo"
                             +"\n             ^^^^^^^^^^^^")    

def p_siError3(p):
    """
    si : IF PARENTESIS_A  PARENTESIS_B bloque_codigo
       | IF PARENTESIS_A  PARENTESIS_B bloque_codigo ELSE bloque_codigo
    """
    errores_Sinc_Desc.append("Error semántico en la linea "+str(p.lineno(1)-linea)+
                             "\nCondicion IF requiere mas argumentos"+
                             "\nSe espera: IF PARENTESIS_A expresion PARENTESIS_B BloqueCodigo"
                             +"\n                          ^^^^^^^^^")    

def p_While(p):
    """
    mientras : WHILE PARENTESIS_A expresion PARENTESIS_B bloque_codigo
    """
    L_inicio = nueva_etiqueta()  # Etiqueta para el inicio del ciclo
    L_fin = nueva_etiqueta()     # Etiqueta para el fin del ciclo

    # 1. Procesar la condición del while
    condicion = p[3]
    cond_instr = []

    if not isinstance(condicion, tuple) or len(condicion) != 4:
        errores_Sem_Desc.append(f"Error semántico en la línea {p.lineno(1)}: La condición del WHILE debe ser booleana")
        cond_temp = "0"  # Forzar un valor falso si la condición es incorrecta
    else:
        # Procesar la condición (izquierda, operador, derecha)
        _, izq, op, der = condicion
        cond_temp = nueva_temporal()
        cond_instr = [f"{cond_temp} = {izq} {op} {der}"]  # Generar el código para la condición

    # 2. Generar el código intermedio para el ciclo while
    codigo = [
        f"LABEL {L_inicio}",  # Iniciar el ciclo while
        *cond_instr,  # Instrucciones de la condición
        f"IF_NOT {cond_temp} GOTO {L_fin}",  # Si la condición es falsa, salir del ciclo
        *p[5],  # Instrucciones dentro del bloque del while
        f"GOTO {L_inicio}",  # Volver al inicio para evaluar la condición nuevamente
        f"LABEL {L_fin}"  # Etiqueta de fin del ciclo
    ]

    p[0] = codigo  # Asignar el código generado al resultado

    
def p_WhileError1(p):
    """
    mientras : WHILE PARENTESIS_A expresion bloque_codigo
    """
    errores_Sinc_Desc.append("Error Sintactico en la linea "+str(p.lineno(1)-linea)+
                            "\nFalta cerrar el Parentesis (')')"+
                            "\nSe espera: WHILE PARENTESIS_A expresion PARENTESIS_B BloqueCodigo"+
                            "\n                                        ^^^^^^^^^^^^")


def p_WhileError2(p):
    """
    mientras : WHILE expresion PARENTESIS_B bloque_codigo
    """
    errores_Sinc_Desc.append("Error Sintactico en la linea "+str(p.lineno(1)-linea)+
                            "\nFalta abrir el Parentesis ('(')"+
                            "\nSe espera: WHILE PARENTESIS_A expresion PARENTESIS_B BloqueCodigo"+
                            "\n                 ^^^^^^^^^^^^")
    
def p_WhileError3(p):
    """
    mientras : WHILE PARENTESIS_A PARENTESIS_B bloque_codigo
    """
    errores_Sinc_Desc.append("Error Sintactico en la linea "+str(p.lineno(1)-linea)+
                            "\nFaltan Argumentos"+
                            "\nSe espera: WHILE PARENTESIS_A expresion PARENTESIS_B BloqueCodigo"+
                            "\n                              ^^^^^^^^^")



#-----------------Import------------------------------
def p_import(p):
    '''graImport : IMPORT ID FROM CADENA PUNTOCOMA'''


#-----------------------------------------------------

#_--------------bucle for--------------------------------

def p_for_loop(p):
    """
    for_loop : FOR PARENTESIS_A for_init PUNTOCOMA expresion PUNTOCOMA for_actualizacion PARENTESIS_B bloque_codigo
    """
    L_inicio = nueva_etiqueta()  # Etiqueta para el inicio del ciclo
    L_fin = nueva_etiqueta()     # Etiqueta para el fin del ciclo
    
    # 1. Procesar la inicialización
    init_data = p[3]
    init_instr = []
    if isinstance(init_data, tuple) and init_data[0] == 'init' and 'value' in init_data[1]:
        temp = nueva_temporal()
        init_instr = [
            f"{temp} = {init_data[1]['value']}",
            f"{init_data[1]['id']} = {temp}"
        ]
    
    # 2. Procesar la condición
    condicion = p[5]
    cond_instr = []
    
    if not isinstance(condicion, tuple) or len(condicion) != 4:
        errores_Sem_Desc.append(f"Error semántico en línea {p.lineno(5)}: La condición del FOR debe ser booleana")
        cond_temp = "0"  # Forzar un valor falso si la condición es incorrecta
    else:
        _, izq, op, der = condicion
        cond_temp = nueva_temporal()
        cond_instr = [f"{cond_temp} = {izq} {op} {der}"]  # Generar código para la condición
    
    # 3. Procesar la actualización
    update_data = p[7]
    update_instr = []
    if isinstance(update_data, tuple):
        if update_data[0] == 'update' and 'value' in update_data[1]:
            temp = nueva_temporal()
            update_instr = [
                f"{temp} = {update_data[1]['value']}",
                f"{update_data[1]['id']} = {temp}"
            ]
        elif update_data[0] in ('increment', 'decrement'):
            op = '+' if update_data[0] == 'increment' else '-'
            temp = nueva_temporal()
            update_instr = [
                f"{temp} = {update_data[1]['id']} {op} 1",
                f"{update_data[1]['id']} = {temp}"
            ]
        else:
            # Añadir caso por defecto en caso de que no haya actualización válida
            errores_Sem_Desc.append(f"Error semántico en línea {p.lineno(7)}: Actualización del FOR no válida")
    
    # 4. Generar código intermedio completo
    codigo = [
        *init_instr,  # Instrucciones de inicialización
        f"LABEL {L_inicio}",  # Etiqueta de inicio del ciclo
        *cond_instr,  # Instrucciones de la condición
        f"IF_NOT {cond_temp} GOTO {L_fin}",  # Si la condición es falsa, salir del ciclo
        *p[9],  # Instrucciones dentro del bloque del FOR
        *update_instr,  # Instrucciones de actualización
        f"GOTO {L_inicio}",  # Volver al inicio del ciclo
        f"LABEL {L_fin}"  # Etiqueta de fin del ciclo
    ]
    
    p[0] = codigo  # Asignar el código generado al resultado

def p_for_init(p):
    """
    for_init : tipo ID ASIGNACION expresion
             | ID ASIGNACION expresion
    """
    if len(p) == 5:  # Con tipo explícito (int i = 0)
        tipo_var = p[1]
        id_var = p[2]
        valor = p[4]
        tipo_valor = TipoValor(str(valor))
        
        if tipo_var != tipo_valor:
            errores_Sem_Desc.append(f"Error semántico en línea {p.lineno(3)}: Tipos incompatibles")
        else:
            tabla_simbolos.insertar_variable(id_var, tipo_var, valor, 'local')
        
        p[0] = ('init', {'type': tipo_var, 'id': id_var, 'value': valor})
    else:  # Sin tipo (i = 0)
        id_var = p[1]
        valor = p[3]
        simbolo = tabla_simbolos.Buscar(id_var)
        
        if simbolo is None:
            errores_Sem_Desc.append(f"Error semántico en línea {p.lineno(1)}: Variable no declarada")
        else:
            tipo_var = simbolo['type']
            tipo_valor = TipoValor(str(valor))
            
            if tipo_var != tipo_valor:
                errores_Sem_Desc.append(f"Error semántico en línea {p.lineno(1)}: Tipos incompatibles")
        
        p[0] = ('init', {'id': id_var, 'value': valor})

def p_for_actualizacion(p):
    """
    for_actualizacion : ID ASIGNACION expresion
                      | ID MASMAS
                      | ID MENOSMENOS
    """
    simbolo = tabla_simbolos.Buscar(p[1])

    if simbolo is None:
        errores_Sem_Desc.append(f"Error semántico en línea {p.lineno(1)}: Variable no declarada")
        p[0] = ('update', {})
    else:
        tipo_var = simbolo['type']

        if len(p) == 4:  # ID = expresion
            tipo_valor = TipoValor(str(p[3]))
            if tipo_var != tipo_valor:
                errores_Sem_Desc.append(f"Error semántico en línea {p.lineno(2)}: Tipos incompatibles")

            p[0] = ('update', {'id': p[1], 'value': p[3]})
        else:  # ID++ o ID--
            if tipo_var not in ['int', 'float']:
                errores_Sem_Desc.append(f"Error semántico en línea {p.lineno(1)}: Operación no soportada para tipo '{tipo_var}'")

            if p.slice[2].type == 'MASMAS':
                op = 'increment'
            else:
                op = 'decrement'

            p[0] = (op, {'id': p[1]})

#----fin bucle for ------------------------------------
#-----------------Atributo de Objeto------------------------------
def p_AtrObjeto(p):
    '''atrObjeto : ID PUNTO ID
                 | ID CORCHETE_A NUMERO CORCHETE_B PUNTO ID'''

def p_declaracion_asignarAtrObjeto(p):
    '''declaracion : atrObjeto ASIGNACION expresion PUNTOCOMA
                    | atrObjeto ASIGNACION TRUE PUNTOCOMA
                    | atrObjeto ASIGNACION FALSE PUNTOCOMA'''

#-----------------Crear Funcion------------------------------
parametros = []
def p_param(p):
    """
    param : tipo ID COMA param
    """
    parametros.append([p[1], p[2]])
    p[0] = parametros

def p_param2(p):
    """
    param : tipo ID
    """
    parametros.append([p[1], p[2]])
    p[0] = parametros

def p_errorFaltanParametros(p):
    """
    param : ID
    """
    errores_Sinc_Desc.append("Error sintactico en la linea: "+str(p.lineno(1)-linea)+
                             "\nNo se definio el tipo de dato del parametro '"+p[1]+"'")


def p_funcion1(p):
    """
    funcion : FUN ID PARENTESIS_A PARENTESIS_B bloque_codigo_funcion
    """
    if(tabla_simbolos.insertar_funcion(p[2], [])):
        errores_Sem_Desc.append("Error semántico en la linea "+str(p.lineno(1)-linea)+": El nombre de la función "+p[2]+" ya ha sido declarado")
    p[0] = p[1]
    tabla_simbolos.cambiar_nulos(p[2])

def p_funcion(p):
    """
    funcion : FUN ID PARENTESIS_A param PARENTESIS_B bloque_codigo_funcion
    """
    global parametros
    if(tabla_simbolos.insertar_funcion(p[2], parametros)):
        errores_Sem_Desc.append("Error semántico en la linea "+str(p.lineno(1)-linea)+": El nombre de la función "+p[2]+" ya ha sido declarado")
    tabla_simbolos.cambiar_nulos(p[2])
    parametros = []

valores = []

def p_funcionError1(p):
    """
    funcion : ID PARENTESIS_A PARENTESIS_B bloque_codigo

    """
    errores_Sinc_Desc.append("Error sintactico en la linea: "+str(p.lineno(1)-linea)+
                             "\nPosible Funcion.  Se espera: FUN ID PARENTESIS_A PARENTESIS_B bloque_codigo"+
                             "\n                             ^^^"+
                             "\nIntente FUN "+p[1]+" "+p[2]+p[3]+"Su bloque de codigo")

def p_funcionError2(p):
    """
    funcion : ID PARENTESIS_A param PARENTESIS_B bloque_codigo

    """
    errores_Sinc_Desc.append("Error sintactico en la linea: "+str(p.lineno(1)-linea)+
                             "\nPosible Funcion.  Se espera: FUN ID PARENTESIS_A Parametros PARENTESIS_B bloque_codigo"+
                             "\n                             ^^^"+
                             "\nIntente FUN "+p[1]+" "+p[2]+"Sus parametros"+p[4]+"Su bloque de codigo")
    
def p_funcionError3(p):
    """
    funcion : FUN ID param PARENTESIS_B bloque_codigo

    """
    errores_Sinc_Desc.append("Error sintactico en la linea: "+str(p.lineno(1)-linea)+
                             "\nFalta Iniciar Paretensis ('(').  Se espera: FUN ID PARENTESIS_A Parametros PARENTESIS_B bloque_codigo"+
                             "\n                                                   ^^^^^^^^^^^^"+
                             "\nIntente "+p[1]+" "+p[2]+"(Sus parametros"+p[4]+"Su bloque de codigo")

    
def p_funcionError4(p):
    """
    funcion : FUN ID PARENTESIS_A param bloque_codigo

    """
    errores_Sinc_Desc.append("Error sintactico en la linea: "+str(p.lineno(1)-linea)+
                             "\nFalta Cerrar Paretensis (')').  Se espera: FUN ID PARENTESIS_A Parametros PARENTESIS_B bloque_codigo"+
                             "\n                                                                           ^^^^^^^^^^^^"+
                             "\nIntente "+p[1]+" "+p[2]+p[3]+"Sus parametros)"+" BloqueCodigo")
    
    
def p_funcionError5(p):
    """
    funcion : FUN ID PARENTESIS_A param PARENTESIS_B

    """
    errores_Sinc_Desc.append("Error sintactico en la linea: "+str(p.lineno(1)-linea)+
                             "\nNo se detecta el bloque de codigo de la funcion")
    
def p_funcionError6(p):
    """
    funcion : FUN ID PARENTESIS_B bloque_codigo

    """
    errores_Sinc_Desc.append("Error sintactico en la linea: "+str(p.lineno(1)-linea)+
                             "\nFalta iniciar Parentesis ('(')"
                             +"\nSe espera FUN ID PARENTESIS_A PARENTESIS_B BloqueCodigo"+
                             "\n                  ^^^^^^^^^^^^"+
                             "\nPruebe con: "+p[1]+" "+p[2]+"("+p[3]+" BloqueCodigo")
    
def p_funcionError7(p):
    """
    funcion : FUN ID PARENTESIS_A bloque_codigo

    """
    errores_Sinc_Desc.append("Error sintactico en la linea: "+str(p.lineno(1)-linea)+
                             "\nFalta cerrar Parentesis (')')"
                             +"\nSe espera FUN ID PARENTESIS_A PARENTESIS_B BloqueCodigo"+
                             "\n                               ^^^^^^^^^^^^"+
                             "\nPruebe con: "+p[1]+" "+p[2]+p[3]+") BloqueCodigo")
        
    
def p_valorparam(p):
    """
    valorparam : expresion COMA valorparam
               | expresion 
    """
    valores.append(p[1])

def p_llamadafunc(p):
    """
    llamadafunc : ID PARENTESIS_A valorparam PARENTESIS_B PUNTOCOMA
                | ID PARENTESIS_A PARENTESIS_B PUNTOCOMA
    """
    global valores
    funcion = tabla_simbolos.Buscar(p[1])
    
    if(funcion == None):
        errores_Sem_Desc.append("Error semántico en la linea "+str(p.lineno(1)-linea)+": La función "+p[1]+" no ha sido declarada")
    else:
        parame = funcion['parameters']
        cantidad_parametros = len(parame)
        cantidad_argumentos = len(valores)

        if cantidad_parametros != cantidad_argumentos:
            errores_Sem_Desc.append(f"Error semántico en la linea {p.lineno(1)-linea}: La función '{p[1]}' espera {cantidad_parametros} argumentos, pero se proporcionaron {cantidad_argumentos}")

        for i in range(min(cantidad_parametros, cantidad_argumentos)):
            tipo_argumento = TipoValor(str(valores[i]))
            tipo_parametro = parame[i][0]
            if tipo_argumento != tipo_parametro:
                errores_Sem_Desc.append(f"Error semántico en la linea {p.lineno(1)-linea}: Se esperaba un valor de tipo {tipo_parametro} pero se proporcionó uno de tipo {tipo_argumento}")

        if cantidad_argumentos > cantidad_parametros:
            errores_Sem_Desc.append(f"Error semántico en la linea {p.lineno(1)-linea}: La función '{p[1]}' no acepta más de {cantidad_parametros} argumentos.")

    valores = []

#-----------------Funciones------------------------------
def p_mover(p):
    """
    mover : moveTo PARENTESIS_A expresion PARENTESIS_B PUNTOCOMA
          | moveTo PARENTESIS_A atrObjeto PARENTESIS_B PUNTOCOMA
    """
    p[0] = p[1]

def p_moverError1(p):
    """
    mover : moveTo PARENTESIS_A expresion PARENTESIS_B 
          | moveTo PARENTESIS_A atrObjeto PARENTESIS_B
    """
    errores_Sinc_Desc.append("Error Sintactico en la linea "+str(p.lineno(1)-linea)+
                             "\nFalta punto y coma. Se espera: moveTo PARENTESIS_A expresion PARENTESIS_B PUNTOCOMA"+
                             "\n                                                                          ^^^^^^^^^")
                            
def p_moverError2(p):
    """
    mover : moveTo PARENTESIS_A expresion PUNTOCOMA 
          | moveTo PARENTESIS_A atrObjeto PUNTOCOMA
    """
    errores_Sinc_Desc.append("Error Sintactico en la linea "+str(p.lineno(1)-linea)+
                             "\nFalta cerrar Parentesis('('). Se espera: moveTo PARENTESIS_A expresion PARENTESIS_B PUNTOCOMA"+
                             "\n                                                                       ^^^^^^^^^")
    
def p_moverError3(p):
    """
    mover : moveTo  expresion PARENTESIS_B PUNTOCOMA 
          | moveTo atrObjeto PARENTESIS_B PUNTOCOMA
    """
    errores_Sinc_Desc.append("Error Sintactico en la linea "+str(p.lineno(1)-linea)+
                             "\nFalta abrir Parentesis('('). Se espera: moveTo PARENTESIS_A expresion PARENTESIS_B PUNTOCOMA"+
                             "\n                                               ^^^^^^^^^^^^")

def p_moverError4(p):
    """
    mover : moveTo PARENTESIS_A  PARENTESIS_B PUNTOCOMA 

    """
    errores_Sinc_Desc.append("Error Sintactico en la linea "+str(p.lineno(1)-linea)+
                             "\nFalta Se requieren Argumentos. Se espera: moveTo PARENTESIS_A expresion PARENTESIS_B PUNTOCOMA"+
                             "\n                                                               ^^^^^^^^")
            


def p_posicion(p):
    """
    posicion : glassPosition PARENTESIS_A expresion PARENTESIS_B
             | glassPosition PARENTESIS_A atrObjeto PARENTESIS_B
    """
    p[0] = 'TRUE'

def p_posicionError1(p):
    """
    posicion : glassPosition PARENTESIS_A expresion 
             | glassPosition PARENTESIS_A atrObjeto
    """
    errores_Sinc_Desc.append("Error Sintactico en la linea: "+str(p.lineno(1)-linea)+
                             "\nFalta cerrar el Parentesis (')')"+
                             "\nSe espera: glassPosition PARENTESIS_A expresion PARENTESIS_B"+
                             "\n                                                ^^^^^^^^^^^^")

def p_posicionError2(p):
    """
    posicion : glassPosition PARENTESIS_A PARENTESIS_B

    """
    errores_Sinc_Desc.append("Error Sintactico en la linea: "+str(p.lineno(1)-linea)+
                             "\nFaltan Argumentos"+
                             "\nSe espera: glassPosition PARENTESIS_A expresion PARENTESIS_B"+
                             "\n                                      ^^^^^^^^^")
def p_posicionError3(p):
    """
    posicion : glassPosition expresion PARENTESIS_B
             | glassPosition atrObjeto PARENTESIS_B

    """
    errores_Sinc_Desc.append("Error Sintactico en la linea: "+str(p.lineno(1)-linea)+
                             "\nFaltan abrir Parentesis ('(') "+
                             "\nSe espera: glassPosition PARENTESIS_A expresion PARENTESIS_B"+
                             "\n                         ^^^^^^^^^^^^")




def p_abrir(p):
    """
    abrir : gateOpen PARENTESIS_A expresion PARENTESIS_B PUNTOCOMA
          | gateOpen PARENTESIS_A atrObjeto PARENTESIS_B PUNTOCOMA
    """
    p[0] = p[1]

def p_abrirError1(p):
    """
    abrir : gateOpen PARENTESIS_A expresion PARENTESIS_B 
          | gateOpen PARENTESIS_A atrObjeto PARENTESIS_B
    """
    errores_Sinc_Desc.append("Error Sintactico en la linea: "+str(p.lineno(1)-linea)+
                             "\nFalta Punto Y Coma"+
                             "\nSe espera: gateOpen PARENTESIS_A expresion PARENTESIS_B PUNTOCOMA"+
                             "\n                                                        ^^^^^^^^^")

def p_abrirError2(p):
    """
    abrir : gateOpen PARENTESIS_A expresion PUNTOCOMA
          | gateOpen PARENTESIS_A atrObjeto PUNTOCOMA
    """
    errores_Sinc_Desc.append("Error Sintactico en la linea: "+str(p.lineno(1)-linea)+
                             "\nFalta Cerrar Parentesis (')')"+
                             "\nSe espera: gateOpen PARENTESIS_A expresion PARENTESIS_B PUNTOCOMA"+
                             "\n                                           ^^^^^^^^^^^")
    

def p_abrirError3(p):
    """
    abrir : gateOpen expresion PARENTESIS_B PUNTOCOMA
          | gateOpen atrObjeto PARENTESIS_B  PUNTOCOMA
    """
    errores_Sinc_Desc.append("Error Sintactico en la linea: "+str(p.lineno(1)-linea)+
                             "\nFalta Abrir Parentesis ('(')"+
                             "\nSe espera: gateOpen PARENTESIS_A expresion PARENTESIS_B PUNTOCOMA"+
                             "\n                    ^^^^^^^^^^^")
    
def p_abrirError4(p):
    """
    abrir : gateOpen PARENTESIS_A  PARENTESIS_B  PUNTOCOMA
          
    """
    errores_Sinc_Desc.append("Error Sintactico en la linea: "+str(p.lineno(1)-linea)+
                             "\nFuncion gateOpen Requiere argumentos"+
                             "\nSe espera: gateOpen PARENTESIS_A expresion PARENTESIS_B PUNTOCOMA"+
                             "\n                                 ^^^^^^^^^")





#-----------------Declaracion de variables errores------------------------------
def p_declaracion_asignar_error1(t):
    '''declaracion : tipo ASIGNACION expresion PUNTOCOMA'''
    errores_Sinc_Desc.append("Error sintáctico en la linea "+str(t.lineno(2)-linea)+": Falta nombre del identificador cerca de " +str("'")+ str(t[1])+str("'")+"\nSe espera: tipo ID Asignacion expresion PUNTOCOMA"+
                                                                                                      "\n                ^^"+
                                                                                                      "\nPruebe con: "+str(t[1])+" NombreEjemplo"+str(t[2])+str(t[3])+str(t[4]))
    
def p_declaracion_asignar_error2(t):
    '''declaracion : tipo ID expresion PUNTOCOMA'''
    errores_Sinc_Desc.append("Error sintáctico en la linea "+str(t.lineno(2)-linea)+": Falta simbolo de asignación (=) cerca de '"+str(t[2])+"'"+
                                                                        "\nSe espera: tipo ID ASIGNACION expresion PUNTOCOMA"+
                                                                        "\n                   ^^^^^^^^^^"+
                                                                        "\nPruebe con: "+str(t[1])+" "+str(t[2])+"="+str(t[3])+str(t[4])+"\n")

def p_declaracion_asignar_error3(t):
    '''declaracion : tipo ID ASIGNACION PUNTOCOMA'''
    errores_Sinc_Desc.append("Error sintáctico en la linea "+str(t.lineno(2)-linea)+": El valor asignado no es valido o faltante cerca de: "+str(t[3])+
                                                                                                         "\nSe espera: tipo ID Asignacion EXPRESION PUNTOCOMA"+
                                                                                                         "\n                              ^^^^^^^^^"+
                                                                                                         "\nPruebe con: "+str(t[1])+" "+str(t[2])+str(t[3]+"Expresion")+str(t[4])+"\n")
    
def p_declaracion_asignar_error4(t):
    '''declaracion : tipo ID ASIGNACION expresion'''
    errores_Sinc_Desc.append("Error sintáctico en la linea "+str(t.lineno(2)-linea)+": Falta punto y coma cerca de "+str("'")+str(t[4])+str("'")+
                                                                                        "\nSe espera: tipo ID Asignacion expresion PUNTOCOMA"+
                                                                                        "\n                                        ^^^^^^^^^"+
                                                                                        "\nPruebe con: "+str(t[1])+" "+str(t[2])+" "+str(t[3])+" "+str(t[4])+" ;\n")

def p_declaracion_asignar_error6(t):
    '''declaracion : ID ID ASIGNACION expresion PUNTOCOMA'''
    errores_Sinc_Desc.append("Error sintáctico en la linea "+str(t.lineno(2)-linea)+": No se reconoce tipo de dato: "+str(t[1])+
                                                                        "\nSe espera: tipo ID ASIGNACION expresion PUNTOCOMA"+
                                                                        "\n           ^^^^"+"\nPruebe con: "+"TipoDeDatoValido "+str(t[2])+str(t[3])+str(t[4])+str(t[5])+"\n")
    

#----------------------Error bloque de código-------------------------------------------   
def p_programaError1(t):
    """programa : bloque_codigo END"""
    errores_Sinc_Desc.append("Error sintáctico en la linea "+str(t.lineno(2)-linea)+": Falta la palabra clave 'BEGIN'")
    
def p_programaError2(t):
    """programa : BEGIN bloque_codigo """
    errores_Sinc_Desc.append("Error sintáctico en la linea "+str(t.lineno(1)-linea)+": Falta la palabra clave 'END'")

def p_error(p):
    if p:
        errores_Sinc_Desc.append(f"Error de sintaxis en '{p.value}', línea {p.lineno - linea}")
        print(f"Error de sintaxis en '{p.value}', línea {p.lineno - linea}")
    else:
        print("Error de sintaxis: expresión incompleta")
    
 
 #--------------------Error bloque de codigo-----------------------------------------
def p_bloque_codigo_error1(t):
    """
    bloque_codigo : lista_declaraciones LLAVE_C
    """
    errores_Sinc_Desc.append("Error sintáctico en la linea "+str(t.lineno(2)-linea)+": Falta la llave de apertura '{'")

def p_bloque_codigo_error2(t):
    """
    bloque_codigo : LLAVE_A lista_declaraciones
    """
    errores_Sinc_Desc.append("Error sintáctico en la linea "+str(t.lineno(1)-linea)+": Falta la llave de cierre '}'")  
    
#----------------------Error crear objeto-----------------------------
# def p_declaracion_crearObjError1(t):
#     '''declaracion : ASIGNACION SLOT NUMERO PUNTOCOMA'''
#     errores_Sinc_Desc.append("Error sintáctico en la linea "+str(t.lineno(2)-linea)+": Falta el nombre del objeto")
    
# def p_declaracion_crearObjError2(t):
#     '''declaracion : ID SLOT NUMERO PUNTOCOMA'''
#     errores_Sinc_Desc.append("Error sintáctico en la linea "+str(t.lineno(2)-linea)+": Falta simbolo de asignación (=)")

# def p_declaracion_crearObjError3(t):
#     '''declaracion : ID ASIGNACION NUMERO PUNTOCOMA'''
#     errores_Sinc_Desc.append("Error sintáctico en la linea "+str(t.lineno(2)-linea)+": Falta la palabra reserva 'SLOT'")
    
# def p_declaracion_crearObjError4(t):
#     '''declaracion : ID ASIGNACION SLOT PUNTOCOMA'''
#     errores_Sinc_Desc.append("Error sintáctico en la linea "+str(t.lineno(2)-linea)+": Falta el nombre del objeto")

# def p_declaracion_crearObjError5(t):
#     '''declaracion : ID ASIGNACION SLOT NUMERO'''
#     errores_Sinc_Desc.append("Error sintáctico en la linea "+str(t.lineno(2)-linea)+": Falta punto y coma")

# def p_declaracion_crearObjError5(t):
#     '''declaracion : ID ASIGNACION SLOT CORCHETE_A ID'''
#     errores_Sinc_Desc.append("Error sintáctico en la linea "+str(t.lineno(2)-linea)+": Falta cerrar corchetes.")
    

#----------------------Error crear arreglo-----------------------------
def p_declaracion_crearArregloError1(t):
    '''declaracion : ASIGNACION CA CORCHETE_A NUMERO CORCHETE_B PUNTOCOMA'''
    errores_Sinc_Desc.append("Error sintáctico en la linea "+str(t.lineno(2)-linea)+": Falta el nombre del arreglo")

def p_declaracion_crearArregloError2(t):
    '''declaracion : ID CA CORCHETE_A NUMERO CORCHETE_B PUNTOCOMA'''
    errores_Sinc_Desc.append("Error sintáctico en la linea "+str(t.lineno(2)-linea)+": Falta simbolo de asignación (=)")
              
def p_declaracion_crearArregloError3(t):
    '''declaracion : ID ASIGNACION CORCHETE_A NUMERO CORCHETE_B PUNTOCOMA'''
    errores_Sinc_Desc.append("Error sintáctico en la linea "+str(t.lineno(2)-linea)+"Falta la palabra reserva 'CA'")
    
def p_declaracion_crearArregloError4(t):
    '''declaracion : ID ASIGNACION CA NUMERO CORCHETE_B PUNTOCOMA'''
    errores_Sinc_Desc.append("Error sintáctico en la linea "+str(t.lineno(2)-linea)+": Falta el corchete de apertura '['")

def p_declaracion_crearArregloError5(t):
    '''declaracion : ID ASIGNACION CA CORCHETE_A CORCHETE_B PUNTOCOMA'''
    errores_Sinc_Desc.append("Error sintáctico en la linea "+str(t.lineno(2)-linea)+":Falta el número entre los corchetes")
    
def p_declaracion_crearArregloError6(t):
    '''declaracion : ID ASIGNACION CA CORCHETE_A NUMERO PUNTOCOMA'''
    errores_Sinc_Desc.append("Error sintáctico en la linea "+str(t.lineno(2)-linea)+": Falta el corchete de cierre ']'")

def p_declaracion_crearArregloError7(t):
    '''declaracion : ID ASIGNACION CA CORCHETE_A NUMERO CORCHETE_B'''
    errores_Sinc_Desc.append("Error sintáctico en la linea "+str(t.lineno(2)-linea)+": Falta punto y coma")
#ERRORES SEMANTICOS ARREGLOS
def p_declaracion_crearArregloError8(t):
    '''declaracion : ID ASIGNACION CA CORCHETE_A RESTA NUMERO CORCHETE_B PUNTOCOMA
                   | ID ASIGNACION CA CORCHETE_A REAL CORCHETE_B PUNTOCOMA'''
    errores_Sinc_Desc.append("Error semántico en la linea "+str(t.lineno(2)-linea)+": Un arreglo sólo puede tener valores enteros positivos.")
    
# Construir el analizador
parser = yacc.yacc()

def test_parser(input_string, num):
    global linea
    linea = num
    result = parser.parse(input_string)
    print(result)