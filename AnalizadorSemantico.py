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
 
def verificar_ambito(tabla_simbolos, identificador, numero_linea):
    simbolo = tabla_simbolos.Buscar(identificador)
    if simbolo['scope'] != 'global':
        raise Exception(f"Error semántico en la linea '{numero_linea}': La variable '{identificador}' no es global")

    
def verificar_asignacion(tabla_simbolos, identificador, valor, numero_linea):
    simbolo = tabla_simbolos.Buscar(identificador)
    if simbolo is None:
        raise Exception(f"Error semántico en la linea {numero_linea}: La variable '{identificador}' no ha sido declarada")
    
    if simbolo['type'] == 'funcion':
        raise Exception(f"Error semántico en la linea {numero_linea}: No se puede asignar un valor a una función '{identificador}'")
    
    if 'value' not in simbolo:
        raise Exception(f"Error semántico en la linea {numero_linea}: La variable '{identificador}' no tiene un valor asignado")
    
    tipo_variable = simbolo['type']
    tipo_valor = TipoValor(valor)
    
    if tipo_variable != tipo_valor:
        raise Exception(f"Error semántico en la linea {numero_linea}: Asignación de un valor de tipo {tipo_valor} a una variable de tipo {tipo_variable}")

def verificar_asignacion_arreglo2(tabla_simbolos, identificador, valor, posicion, numero_linea):
    simbolo = tabla_simbolos.Buscar(identificador)
    if simbolo is None:
        raise Exception(f"Error semántico en la linea {numero_linea}: La variable '{identificador}' no ha sido declarada")
    if 'size' not in simbolo:
        raise Exception(f"Error semántico en la linea {numero_linea}: La variable '{identificador}' no es un arreglo")
    else:
        size = simbolo['size']
        if int(size) <= int(posicion):
            raise Exception(f"Error semántico en la linea {numero_linea}: El indice es mayor al tamaño del arreglo")
    if simbolo['type'] == 'funcion':
        raise Exception(f"Error semántico en la linea {numero_linea}: No se puede asignar un valor a una función '{identificador}'")
    tipo_variable = simbolo['type']
    tipo_valor = TipoValor(valor)
    if tipo_variable != tipo_valor:
        raise Exception(f"Error semántico en la linea {numero_linea}: Asignación de un valor de tipo {tipo_valor} a una variable de tipo {tipo_variable}")
    
def verificar_asignacion_arreglo3(tabla_simbolos, identificador, posicion, numero_linea):
    simbolo = tabla_simbolos.Buscar(identificador)
    identificador2 = identificador + '[' + str(posicion) + ']'
    simbolo2 = tabla_simbolos.Buscar(identificador2)
    if simbolo is None:
        raise Exception(f"Error semántico en la linea {numero_linea}: La variable '{identificador}' no ha sido declarada")
    elif 'size' not in simbolo:
        raise Exception(f"Error semántico en la linea {numero_linea}: La variable '{identificador}' no es un arreglo")
    elif 'position' not  in simbolo2:
        raise Exception(f"Error semántico en la linea {numero_linea}: La variable '{identificador}', Posicion '{posicion}' no tiene un valor asignado")

def valor_identificador(tabla_simbolos, identificador):
    simbolo = tabla_simbolos.Buscar(identificador)
    return simbolo['value']

def verificar_asignacion_arreglo(tabla_simbolos, identificador, tipo, numero_linea):
    if tipo == 'ID':
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
                valuest = str(simbolo['value'])
                print(valuest)
                esNegativo = valuest.find('-')
                if esNegativo != -1:
                    raise Exception(f"Error semántico en la linea {numero_linea}: la variable '{identificador}' no es un número entero positivo.")
    else:
        tipo = TipoValor(identificador)
        if tipo != 'int':
            raise Exception(f"Error semántico en la linea {numero_linea}: la variable '{identificador}' no es un número entero positivo.")
        else:
            esNegati = str(identificador).find("-")
            print(esNegati)
            if esNegati != -1:
                raise Exception(f"Error semántico en la linea {numero_linea}: el valor '{identificador}' no es un número entero positivo.")
