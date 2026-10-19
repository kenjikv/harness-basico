"""
EL MODELO (lo único que NO es harness)

Agente = Modelo + Harness. El modelo solo decide la siguiente acción.
Todo lo demás lo pone el harness. Por eso el modelo es intercambiable:

  - ModeloSimulado: un guion fijo que comete errores a propósito.
    No necesita internet ni llave. Sirve para ver el harness en acción.
  - ModeloClaude:   Claude real, vía la API de Anthropic (necesita llave).

Ambos ofrecen lo mismo:
  iniciar(instrucciones, tarea, catalogo)
  siguiente_accion(resultado_anterior, hubo_error) -> (herramienta, argumentos)
"""


class ModeloSimulado:
    """Imita los errores típicos de un agente real, siempre en el mismo orden."""

    VERSION_INGENUA = (
        "def es_palindromo(texto):\n"
        "    return texto == texto[::-1]\n"
    )
    VERSION_CORREGIDA = (
        "def es_palindromo(texto):\n"
        '    """Indica si el texto se lee igual al derecho y al revés."""\n'
        '    limpio = "".join(c.lower() for c in texto if c.isalnum())\n'
        "    return limpio == limpio[::-1]\n"
    )
    GUION = [
        ("escribir_archivo", {"ruta": "../palindromo.py", "contenido": VERSION_INGENUA}),
        ("escribir_archivo", {"ruta": "palindromo.py", "contenido": VERSION_INGENUA}),
        ("terminar", {"resumen": "¡Listo!"}),
        ("verificar", {}),
        ("escribir_archivo", {"ruta": "test_palindromo.py", "contenido": "# sin tests"}),
        ("escribir_archivo", {"ruta": "palindromo.py", "contenido": VERSION_CORREGIDA}),
        ("verificar", {}),
        ("terminar", {"resumen": "es_palindromo lista; tests y linter en verde."}),
    ]

    def iniciar(self, instrucciones, tarea, catalogo):
        self.paso = 0

    def siguiente_accion(self, resultado_anterior, hubo_error):
        accion = self.GUION[min(self.paso, len(self.GUION) - 1)]
        self.paso += 1
        return accion


class ModeloClaude:
    """Claude real. Sigue el formato de tool use de la documentación oficial:
    https://platform.claude.com/docs/en/agents-and-tools/tool-use/handle-tool-calls"""

    def __init__(self, api_key, modelo="claude-sonnet-5-5"):
        try:
            import anthropic
        except ImportError:
            raise SystemExit("Falta el SDK de Anthropic. Instálalo con:  pip install anthropic")
        self.cliente = anthropic.Anthropic(api_key=api_key)
        self.modelo = modelo

    def iniciar(self, instrucciones, tarea, catalogo):
        self.instrucciones = instrucciones
        self.herramientas = [
            {"name": nombre, "description": h["descripcion"], "input_schema": h["parametros"]}
            for nombre, h in catalogo.items()
        ]
        self.mensajes = [{"role": "user", "content": tarea}]
        self.pendientes = []   # ids de tool_use que aún esperan respuesta

    def siguiente_accion(self, resultado_anterior, hubo_error):
        # 1) Devolver a Claude el resultado de la herramienta que pidió.
        if resultado_anterior is not None:
            if self.pendientes:
                bloques = [{"type": "tool_result", "tool_use_id": self.pendientes[0],
                            "content": resultado_anterior, "is_error": hubo_error}]
                # Si pidió varias a la vez, el harness ejecuta solo la primera.
                bloques += [{"type": "tool_result", "tool_use_id": id_extra,
                             "content": "No ejecutada: usa una herramienta por turno.",
                             "is_error": True} for id_extra in self.pendientes[1:]]
                self.mensajes.append({"role": "user", "content": bloques})
            else:
                self.mensajes.append({"role": "user", "content": resultado_anterior})

        # 2) Pedirle a Claude su siguiente decisión.
        respuesta = self.cliente.messages.create(
            model=self.modelo,
            max_tokens=4096,
            system=self.instrucciones,
            tools=self.herramientas,
            messages=self.mensajes,
        )
        self.mensajes.append({"role": "assistant", "content": respuesta.content})

        # 3) Traducir su respuesta a (herramienta, argumentos).
        usos = [bloque for bloque in respuesta.content if bloque.type == "tool_use"]
        self.pendientes = [uso.id for uso in usos]
        if usos:
            return usos[0].name, usos[0].input
        texto = "".join(b.text for b in respuesta.content if b.type == "text")
        return "terminar", {"resumen": texto}   # respondió sin herramienta: lo tomamos como "terminé"
