from TablaSimbolos import SymbolTable
import re

def TipoValor(valor):
    tipoInt =  r'-?\d+'
    tipoReal = r'-?(\d+\.\d+|\.\d+)'
    tipoStg = r'\#.*?\#'
    if isinstance(valor, float):
        valor = str(valor)
    if isinstance(valor, int):
        valor = str(valor)
    if isinstance(valor, bool):
        valor = str(valor)
    if re.match(tipoReal, valor):
        return 'real'
    elif re.match(tipoInt, valor):
        return 'int'
    elif re.match(tipoStg, valor):
        return 'stg'
    elif valor=='TRUE' or valor=='FALSE':
        return 'bool'
    elif valor=='None':
        return None
    else:
        return None
 
def verificar_asignacion(tabla_simbolos, identificador, valor, numero_linea):
    simbolo = tabla_simbolos.Buscar(identificador)
    if simbolo is None:
        raise Exception(f"Error semántico en la linea {numero_linea}: La variable '{identificador}' no ha sido declarada")
    if simbolo['type'] == 'funcion':
            tipo = 'funcion'
    else:
        tipo = TipoValor(simbolo['value'])
        if 'value' not in simbolo:
            raise Exception(f"Error semántico en la linea {numero_linea}: La variable '{identificador}' no tiene un valor asignado")
    if tipo != simbolo['type']:
        raise Exception(f"Error semántico en la linea {numero_linea}: Asignación de un valor de tipo {tipo} a una variable de tipo {simbolo['type']}")

def verificar_asignacion_arreglo(tabla_simbolos, identificador, numero_linea):
    simbolo = tabla_simbolos.Buscar(identificador)
    if simbolo is None:
        raise Exception(f"Error semántico en la linea {numero_linea}: La variable '{identificador}' no ha sido declarada")
    else: 
        if simbolo['type'] == 'funcion':
            tipo = 'funcion'
        else:
            if 'value' not in simbolo:
                raise Exception(f"Error semántico en la linea {numero_linea}: La variable '{identificador}' no tiene un valor asignado")
        tipo = TipoValor(simbolo['value'])
        if tipo != 'int':
            raise Exception(f"Error semántico en la linea {numero_linea}: la variable '{identificador}' no es un número entero positivo.")
        else:
            simbolo['value'] = str(simbolo['value'])
            esNegativo = simbolo['value'].find('-')
            if esNegativo != -1:
                raise Exception(f"Error semántico en la linea {numero_linea}: la variable '{identificador}' no es un número entero positivo.")
