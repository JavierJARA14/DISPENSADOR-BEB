from TablaSimbolos import SymbolTable
import re

def TipoValor(valor):
    tipoInt =  r'\d+'
    tipoReal = r'(\d+\.\d+|\.\d+)'
    tipoStg = r'\#.*?\#'
    
    if re.match(tipoReal, valor):
        return 'real'
    elif re.match(tipoInt, valor):
        return 'int'
    elif re.match(tipoStg, valor):
        return 'stg'
    elif valor=='True' or valor=='False':
        return 'bool'
    elif valor=='None':
        return None
    else:
        return None
 
def verificar_asignacion(tabla_simbolos, identificador, valor, numero_linea):
    simbolo = tabla_simbolos.Buscar(identificador)
    if simbolo is None:
        raise Exception(f"Error semántico en la linea {numero_linea}: La variable '{identificador}' no ha sido declarada")
    if(valor != 'funcion'):
        tipo = TipoValor(valor)
    else:
        tipo = 'funcion'

    if tipo != simbolo['type']:
        raise Exception(f"Error semántico en la linea {numero_linea}: Asignación de un valor de tipo {tipo} a una variable de tipo {simbolo['type']}")


