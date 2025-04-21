class SymbolTable:
    def __init__(self):
        self.table = {}
        self.current_scope = "global"

    def insertar_variable(self, name, data_type, value, scope):
        if name in self.table:
            return True
        else:
            # Asignar un valor a la clave 'value' cuando insertas una variable
            self.table[name] = {'type': data_type, 'value': value, 'scope': scope}
            return False


    def insertar_funcion(self, name, parameters):
        if name in self.table:
            return True
        else:
            self.table[name] = {'type': 'funcion', 'parameters': parameters}
            return False
        
    def declarar_arreglo(self, name, data_type, size, scope):
        if name in self.table:
            return True
        else:
            self.table[name] = {'type': data_type, 'size': size, 'scope': scope}
            return False
        
    # def valor_arreglo(self, name, position, value):
    #     name = name + '[' +  str(position) + ']'
    #     self.table[name] = {'position': position, 'value': value}
    #     return False

    def valor_arreglo(self, name, position, value, scope):
        simbolo = self.Buscar(name)
        if simbolo is None:
            return False  # La variable no existe
        if 'size' not in simbolo:
            return False  # No es un arreglo
        # Si el arreglo no tiene valores guardados, inicializarlo
        if 'values' not in simbolo:
            simbolo['values'] = {}
            # Guardar el valor en la posición correspondiente
        simbolo['values'][position] = value
        simbolo['scope'] = scope
        return True


    def cambiar_nulos(self, funcion):
        for name, value in self.table.items():  # Iterar sobre claves y valores
            if value.get('scope') == 'nulo':  # Usar .get() para evitar KeyError
                value['scope'] = funcion  # Modificar el valor

    def Buscar(self, name):
        if name in self.table:
            return self.table[name]
        else:
            return None
        
    def buscar_tipo(self, name):
        simbolo = self.Buscar(name)
        return simbolo['type']

    def get_value(self, name, index=None):
        # Obtener el símbolo correspondiente
        variable = self.Buscar(name)
        
        if variable is not None:
            # Si es un arreglo y se especifica un índice, devuelve el valor en esa posición
            if variable['type'] == 'array' and index is not None:
                return variable['value'][index] if index < len(variable['value']) else None
            return variable.get('value', None)
        
        return None


    def limpiar(self):
        """Limpia la tabla de símbolos completamente."""
        self.table.clear()

    def display(self):
        print("Symbol Table:")
        for name, info in self.table.items():
            if info.get('type') == 'funcion':  # Usar .get() para evitar KeyError
                print("Function: {} | Type: {} | Parameters: {}".format(name, info['type'], info.get('parameters', 'N/A')))
            elif info.get('type') == 'arreglo':  # Si es un arreglo
                # Verificar si el arreglo tiene elementos almacenados
                arreglo_valores = info.get('value', {})
                print(f"Array: {name} | Type: {info.get('type', 'N/A')} | Scope: {info.get('scope', 'N/A')}")
                if arreglo_valores:  # Si el arreglo tiene valores
                    for index, valor in arreglo_valores.items():
                        print(f"  Index {index}: {valor}")
                else:
                    print(f"  No values assigned yet.")
            else:
                print("Variable: {} | Type: {} | Value: {} | Scope: {}".format(
                    name,
                    info.get('type', 'N/A'),  # Usar .get() para evitar KeyError
                    info.get('value', 'N/A'),  # Usar .get() para evitar KeyError
                    info.get('scope', 'N/A')   # Usar .get() para evitar KeyError
                ))

    def obtener(self):
            simbolos = []
            for name, info in self.table.items():
                # Extraemos los datos relevantes y los agregamos a la lista
                if info.get('type') == 'funcion':  # Si es una función
                    simbolos.append({
                        'id': name,
                        'tipo': info['type'],
                        'valor': 'N/A',  # Las funciones no tienen valor asignado
                        'alcance': info.get('scope', 'global'),
                    })
                elif info.get('type') == 'arreglo':  # Si es un arreglo
                    simbolos.append({
                        'id': name,
                        'tipo': info.get('type', 'N/A'),
                        'valor': 'Valores: ' + ', '.join([f'[{k}]: {v}' for k, v in info.get('values', {}).items()]),
                        'alcance': info.get('scope', 'N/A'),
                    })
                else:  # Si es una variable
                    simbolos.append({
                        'id': name,
                        'tipo': info.get('type', 'N/A'),
                        'valor': info.get('value', 'N/A'),
                        'alcance': info.get('scope', 'N/A'),
                    })
            return simbolos

"""
# Ejemplo de uso
sym_table = SymbolTable()

# Insertar variables
sym_table.insertar_variable('x', 'int', 5)
sym_table.insertar_variable('y', 'float', 3.14)
sym_table.insertar_variable('z', 'string', 'hello')

# Insertar una función
sym_table.insertar_funcion('sumar', ['a', 'b'])

# Mostrar la tabla de símbolos
sym_table.display()

# Buscar una variable
variable_info = sym_table.Buscar('sumar')
if variable_info:
    print("Información de la variable 'sumar':", variable_info['parameters'])
else:
    print("Variable 'x' no encontrada en la tabla de símbolos")
"""

