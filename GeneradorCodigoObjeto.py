import re

class GeneradorCodigoObjeto:
    def __init__(self, codigo_fuente):
        self.codigo_fuente = codigo_fuente.splitlines()
        self.output = []
        self.funciones = []
        self.gate_pin = 8
        self.en_funcion = False
        self.vars_declaradas = set()  # Evita declarar variables duplicadas
        self.vars_declaradas_linea = {}  # NUEVO: Guarda la línea de declaración
        self.vars_usadas = set()         # NUEVO: Guarda variables usadas
        self.vars_constantes = {}        # NUEVO: Guarda valores constantes de variables
        self.estado_gate = None  # Estado actual del gate (HIGH o LOW)
        self.advertencias = []  # Para posibles mensajes de error o warning
        self.usa_serial = False

    def generar(self):
        self._agregar_encabezado()

        self.output.append("void setup() {")
        self.output.append("  pinMode(GATE_PIN, OUTPUT);")
        self.output.append("Serial.begin(9600);") # Inicializa la comunicación serial si se usa SMS
        self.output.append("}")

        self.output.append("void loop() {")

        i = 0
        while i < len(self.codigo_fuente):
            linea = self.codigo_fuente[i]
            # Detectar y eliminar bucles muertos
            salto = self._eliminar_bloque_muerto(i)
            if salto > 0:
                # Comentar la línea del bucle
                self.output.append(f"  // [Eliminado: bucle nunca ejecutado] {self.codigo_fuente[i].strip()}")
                i += salto
                continue
            self._traducir_linea(linea)
            i += 1

        self.output.append("  while(1);")  # Evita que loop() termine
        self.output.append("}")

        # --- Eliminación de código muerto: variables no usadas ---
        for var in self.vars_declaradas:
            if var not in self.vars_usadas and var in self.vars_declaradas_linea:
                idx = self.vars_declaradas_linea[var]
                if idx < len(self.output):
                    self.output[idx] = f"  // [Eliminado: variable no usada] {self.output[idx].strip()}"

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

    def _eliminar_bloque_muerto(self, idx):
        # Detecta si la línea en idx es un bucle muerto y retorna cuántas líneas saltar (0 si no aplica)
        linea = self.codigo_fuente[idx].strip()
        # FOR: FOR(int i = 0; i < num; i++) o FOR(int i = 0; i > num; i--)
        match_for = re.match(r"FOR\s*\(([^;]*);([^;]*);([^)]*)\)\s*{", linea)
        if match_for:
            init, cond, inc = match_for.groups()
            # Detectar casos como FOR(int i=0; i > 5; i++)
            m_gt = re.match(r"(\w+)\s*>\s*(\d+)", cond.strip())
            if m_gt:
                var, limite = m_gt.groups()
                # Si el valor inicial es menor o igual al límite, nunca entra
                m_init = re.match(r"int\s+%s\s*=\s*(\d+)" % var, init.strip())
                if m_init:
                    valor_init = int(m_init.group(1))
                    if valor_init <= int(limite):
                        return self._contar_bloque(idx)
            # Detectar casos como FOR(int i=0; i < 0; i++)
            m_lt = re.match(r"(\w+)\s*<\s*(\d+)", cond.strip())
            if m_lt:
                var, limite = m_lt.groups()
                m_init = re.match(r"int\s+%s\s*=\s*(\d+)" % var, init.strip())
                if m_init:
                    valor_init = int(m_init.group(1))
                    if valor_init >= int(limite):
                        return self._contar_bloque(idx)
            # También soporta for (int i = 0; i > num; i--) con num=0
            m2 = re.match(r"(\w+)\s*[>]\s*(\w+)", cond.strip())
            if m2:
                var, limite = m2.groups()
                if limite in self.vars_constantes and str(self.vars_constantes[limite]) in ["0", "FALSE", "false"]:
                    return self._contar_bloque(idx)
            m3 = re.match(r"(\w+)\s*[<|<=]\s*(\w+)", cond.strip())
            if m3:
                var, limite = m3.groups()
                if limite in self.vars_constantes and str(self.vars_constantes[limite]) in ["0", "FALSE", "false"]:
                    return self._contar_bloque(idx)
        # WHILE: WHILE(cond == TRUE) o WHILE(cond == FALSE)
        match_while = re.match(r"WHILE\s*\(([^)]*)\)\s*{", linea)
        if match_while:
            cond = match_while.group(1).strip()
            # cond == TRUE
            m = re.match(r"(\w+)\s*==\s*TRUE", cond)
            if m:
                var = m.group(1)
                if var in self.vars_constantes and str(self.vars_constantes[var]).lower() in ["false", "0"]:
                    return self._contar_bloque(idx)
            # cond == FALSE
            m2 = re.match(r"(\w+)\s*==\s*FALSE", cond)
            if m2:
                var = m2.group(1)
                if var in self.vars_constantes and str(self.vars_constantes[var]).lower() in ["true", "1"]:
                    return self._contar_bloque(idx)
        return 0

    def _contar_bloque(self, idx):
        # Cuenta cuántas líneas ocupa el bloque { ... } a partir de idx
        contador = 0
        started = False
        for i in range(idx, len(self.codigo_fuente)):
            linea = self.codigo_fuente[i]
            if '{' in linea:
                contador += 1
                started = True
            if '}' in linea and started:
                contador -= 1
                if contador == 0:
                    return i - idx + 1  # Saltar desde idx hasta i inclusive
        return 1  # Por si no encuentra cierre

    def _traducir_linea(self, linea):
        # Limpiar comentarios inline y espacios
        linea = re.sub(r"//.*", "", linea).strip()
        if not linea:
            return

        destino = self.funciones if self.en_funcion else self.output

        # --- Detectar variables usadas ---
        for var in self.vars_declaradas:
            if re.search(rf'\b{var}\b', linea):
                self.vars_usadas.add(var)

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
        
        # WAIT(n); → Traducido a delay(n);
        if match := re.match(r"WAIT\s*\(\s*(\d+)\s*\)\s*;", linea):
            valor = int(match.group(1))
            if valor <= 0:
                destino.append(f"  // Error: WAIT con valor no válido ({valor})")
            else:
                destino.append(f"  delay({valor});")
            return

        # Guardar valores constantes de variables
        if match := re.match(r"int\s+(\w+)\s*=\s*(\d+)\s*;", linea):
            nombre, valor = match.groups()
            self.vars_constantes[nombre] = int(valor)
        if match := re.match(r"bool\s+(\w+)\s*=\s*(TRUE|FALSE|true|false)\s*;", linea):
            nombre, valor = match.groups()
            self.vars_constantes[nombre] = valor.upper() == "TRUE"

        # Llamada tipo SMS(#TEXTO#); → convierte en string
        if match := re.match(r'SMS\s*\(\s*(.+)\)\s*;', linea):
            self.usa_serial = True
            expr = match.group(1)
            partes = [p.strip() for p in expr.split('+')]
            salida = '"'
            for parte in partes:
                if parte.startswith('#') and parte.endswith('#'):
                    salida += parte.strip('#')
                else:
                    salida += f'" + String({parte}) + "'
            salida += '"'
            destino.append(f"  Serial.println({salida});")
            return

        # GATE BE_OPEN
        if linea == "GATE.BE_OPEN;":
            if self.estado_gate != "HIGH":
                destino.append("  digitalWrite(GATE_PIN, HIGH);")
                self.estado_gate = "HIGH"
            return

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
                self.vars_declaradas_linea[var] = len(destino) - 1  # NUEVO
            return

        # Asignación a arreglo
        if match := re.match(r"(\w+)\[(\d+)\]\s*=\s*(.+);", linea):
            var, index, value = match.groups()
            destino.append(f"  {var}[{index}] = {value.strip()};")
            return

        # Control de flujo IF, WHILE, FOR con apertura de bloque
        if re.match(r"(IF|WHILE|FOR)\s*\(.*\)\s*{", linea):
            linea = linea.replace("IF", "if").replace("WHILE", "while").replace("FOR", "for")
            linea = linea.strip()
            if linea.endswith("{"):
                linea = linea[:-1].strip()
            destino.append(f"  {linea} {{")
            return

        # ELSE con bloque
        # Manejar patrón especial: } ELSE {
        if re.match(r"^\}\s*ELSE\s*\{\s*$", linea):
            destino.append("  } else {")
            return

        if re.match(r"^\s*ELSE\s*{\s*$", linea):
            destino.append("  else {")
            return

        if linea == "}":
            if self.en_funcion:
                self.funciones.append("}")
                self.en_funcion = False
            else:
                destino.append("  }")
            return
        
        # Declaración de variable con asignación
        if match := re.match(r"(int|bool)\s+(\w+)\s*=\s*(.*);", linea):
            tipo, nombre, valor = match.groups()
            if nombre not in self.vars_declaradas:
                destino.append(f"  {tipo} {nombre} = {valor};")
                self.vars_declaradas.add(nombre)
                self.vars_declaradas_linea[nombre] = len(destino) - 1  # NUEVO
            else:
                destino.append(f"  {nombre} = {valor};")
            return

        # Declaración de variable tipo stg (string personalizada)
        if match := re.match(r"stg\s+(\w+)\s*=\s*#([^#]+)#\s*;", linea):
            nombre, valor = match.groups()
            if nombre not in self.vars_declaradas:
                destino.append(f'  String {nombre} = "{valor}";')
                self.vars_declaradas.add(nombre)
                self.vars_declaradas_linea[nombre] = len(destino) - 1  # NUEVO
            else:
                destino.append(f'  {nombre} = "{valor}";')
            return

        # Declaración simple sin asignación (ej: int x;)
        if match := re.match(r"(int|bool)\s+(\w+)\s*;", linea):
            tipo, nombre = match.groups()
            if nombre not in self.vars_declaradas:
                destino.append(f"  {tipo} {nombre};")
                self.vars_declaradas.add(nombre)
                self.vars_declaradas_linea[nombre] = len(destino) - 1  # NUEVO
            return

        # Llamada a función
        if re.match(r"\w+\s*\(.*\);", linea):
            destino.append(f"  {linea}")
            return

        # Línea no traducida
        destino.append(f"  // [No traducido] {linea}")
        
        # Asignación simple (ej: i = i + 1; o i = i - 1;)
        if match := re.match(r"(\w+)\s*=\s*(.+);", linea):
            nombre, valor = match.groups()
            destino.append(f"  {nombre} = {valor};")
            return

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