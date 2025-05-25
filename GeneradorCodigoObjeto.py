import re

class GeneradorCodigoObjeto:
    def __init__(self, codigo_fuente):
        self.codigo_fuente = codigo_fuente.splitlines()
        self.output = []
        self.funciones = []
        self.gate_pin = 8
        self.en_funcion = False
        self.vars_declaradas = set()  # Evita declarar variables duplicadas
        self.estado_gate = None  # Estado actual del gate (HIGH o LOW)
        self.advertencias = []  # Para posibles mensajes de error o warning

    def generar(self):
        self._agregar_encabezado()

        self.output.append("void setup() {")
        self.output.append("  pinMode(GATE_PIN, OUTPUT);")
        self.output.append("}")

        self.output.append("void loop() {")

        for linea in self.codigo_fuente:
            self._traducir_linea(linea)

        self.output.append("  while(1);")  # Evita que loop() termine
        self.output.append("}")

        return '\n'.join(self.output + ["\n"] + self.funciones)

    def _agregar_encabezado(self):
        self.output.append("#include <Arduino.h>")
        self.output.append("#define TRUE true")
        self.output.append("#define FALSE false")
        self.output.append(f"#define GATE_PIN {self.gate_pin}\n")

    def _actualizar_define_gate(self):
        for i, linea in enumerate(self.output):
            if linea.startswith("#define GATE_PIN"):
                self.output[i] = f"#define GATE_PIN {self.gate_pin}"
                break

    def _traducir_linea(self, linea):
        # Limpiar comentarios inline y espacios
        linea = re.sub(r"//.*", "", linea).strip()
        if not linea:
            return

        destino = self.funciones if self.en_funcion else self.output

        # SETGATE
        if linea.startswith("GATE SETGATE"):
            partes = linea.split()
            try:
                pin = int(partes[2].strip(';'))
                if 0 <= pin <= 13:
                    self.gate_pin = pin
                    self._actualizar_define_gate()
                    destino.append(f"  // GATE SETGATE configurado al pin {self.gate_pin}")
                else:
                    destino.append(f"  // Error: pin fuera de rango ({pin})")
            except Exception:
                destino.append(f"  // Error al interpretar SETGATE")
            return

        # GATE BE_OPEN
        if linea == "GATE.BE_OPEN;":
            if self.estado_gate != "HIGH":
                destino.append("  digitalWrite(GATE_PIN, HIGH);")
                self.estado_gate = "HIGH"
            return

        # GATE BE_CLOSE
        if linea == "GATE.BE_CLOSE;":
            if self.estado_gate != "LOW":
                destino.append("  digitalWrite(GATE_PIN, LOW);")
                self.estado_gate = "LOW"
            return

        # Ignorar BEGIN{ y }END
        if linea.startswith("BEGIN{") or linea == "}END":
            destino.append(f"  // {linea} ignorado")
            return

        # Funciones
        if linea.startswith("FUN"):
            match = re.match(r"FUN\s+(\w+)\(([^)]*)\)\s*{", linea)
            if match:
                nombre, parametros = match.groups()
                params_convertidos = self._convertir_parametros(parametros)
                self.en_funcion = True
                self.funciones.append(f"void {nombre}({params_convertidos}) {{")
            return

        # Cierre de bloque
        if linea == "}":
            if self.en_funcion:
                self.funciones.append("}")
                self.en_funcion = False
            else:
                destino.append("}")
            return

        # Declaración de arreglo con CA[n]
        if match := re.match(r"(int\s+)?(\w+)\s*=\s*CA\[(\d+)\];", linea):
            _, var, size = match.groups()
            if var not in self.vars_declaradas:
                destino.append(f"  int {var}[{size}];")
                self.vars_declaradas.add(var)
            return

        # Asignación a arreglo
        if match := re.match(r"(\w+)\[(\d+)\]\s*=\s*(.+);", linea):
            var, index, value = match.groups()
            destino.append(f"  {var}[{index}] = {value.strip()};")
            return

        # Control de flujo IF, WHILE, FOR
        if linea.startswith("IF(") or linea.startswith("WHILE(") or linea.startswith("FOR("):
            linea = linea.replace("IF", "if").replace("WHILE", "while").replace("FOR", "for")
            destino.append(f"  {linea}")
            return

        # Declaración de variable con asignación
        if match := re.match(r"(int|bool)\s+(\w+)\s*=\s*(.*);", linea):
            tipo, nombre, valor = match.groups()
            if nombre not in self.vars_declaradas:
                destino.append(f"  {tipo} {nombre} = {valor};")
                self.vars_declaradas.add(nombre)
            else:
                destino.append(f"  {nombre} = {valor};")
            return

        # Declaración simple sin asignación (ej: int x;)
        if match := re.match(r"(int|bool)\s+(\w+)\s*;", linea):
            tipo, nombre = match.groups()
            if nombre not in self.vars_declaradas:
                destino.append(f"  {tipo} {nombre};")
                self.vars_declaradas.add(nombre)
            return

        # Llamada a función
        if re.match(r"\w+\s*\(.*\);", linea):
            destino.append(f"  {linea}")
            return

        # Línea no traducida
        destino.append(f"  // [No traducido] {linea}")

    def _convertir_parametros(self, parametros):
        if not parametros.strip():
            return ""
        partes = [p.strip() for p in parametros.split(',')]
        convertidos = []
        for parte in partes:
            if parte.startswith("int ") or parte.startswith("bool "):
                nombre = parte.split()[1]
                if nombre not in self.vars_declaradas:
                    self.vars_declaradas.add(nombre)
                convertidos.append(parte)
            else:
                if parte not in self.vars_declaradas:
                    self.vars_declaradas.add(parte)
                convertidos.append(f"int {parte}")  # Asume int por defecto
        return ', '.join(convertidos)