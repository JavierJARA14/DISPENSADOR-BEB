class SymbolTable:
    def __init__(self):
        self.table = {}

    def insertar_variable(self, name, data_type, value):
        if name in self.table:
            return True
        else:
            self.table[name] = {'type': data_type, 'value': value}
            return False

    def insertar_funcion(self, name, parameters):
        if name in self.table:
            return True
        else:
            self.table[name] = {'type': 'funcion', 'parameters': parameters}
            return False
        
    def insertar_arreglo(self, name, size):
        return none 

    def Buscar(self, name):
        if name in self.table:
            return self.table[name]
        else:
            return None
        
    def get_value(self, name):
        variable = self.Buscar(name)
        if variable is not None:
            return variable.get('value', None)
        return None

    def display(self):
        print("Symbol Table:")
        for name, info in self.table.items():
            if info['type'] == 'funcion':
                print("Function: {} | Type: {} | Parameters: {}".format(name, info['type'], info['parameters']))
            else:
                print("Variable: {} | Type: {} | Value: {}".format(name, info['type'], info['value']))

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

