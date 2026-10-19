"""
COMPONENTE 2 — HERRAMIENTAS con GUARDARRAÍLES

El modelo no toca el disco directamente: pide usar una herramienta y el
harness decide si la ejecuta. Los guardarraíles son las reglas que el
harness HACE CUMPLIR, aunque el modelo intente saltárselas:
  - solo puede leer/escribir dentro de workspace/
  - no puede modificar los tests ni la memoria
  - no puede declarar "terminado" si la verificación no pasó
"""
import memoria
import sensores
from config import WORKSPACE
from tarea import ARCHIVO_TESTS


class Bloqueado(Exception):
    """Un guardarraíl impidió la acción."""


PROTEGIDOS = {ARCHIVO_TESTS, memoria.ARCHIVO.name}


# ── Guardarraíl central ─────────────────────────────────────────────
def ruta_segura(ruta):
    """Convierte la ruta pedida en una ruta dentro de workspace/ o la bloquea."""
    destino = (WORKSPACE / ruta).resolve()
    if not destino.is_relative_to(WORKSPACE.resolve()):
        raise Bloqueado(f"'{ruta}' está fuera de tu carpeta de trabajo.")
    return destino


# ── Las herramientas ────────────────────────────────────────────────
def leer_archivo(ruta):
    destino = ruta_segura(ruta)
    if not destino.exists():
        return f"El archivo '{ruta}' no existe."
    return destino.read_text(encoding="utf-8")


def escribir_archivo(ruta, contenido):
    destino = ruta_segura(ruta)
    if destino.name in PROTEGIDOS:
        raise Bloqueado(f"'{destino.name}' está protegido; no puedes modificarlo.")
    destino.write_text(contenido, encoding="utf-8")
    memoria.invalidar_verificacion()
    return f"Guardado '{ruta}' ({len(contenido)} caracteres). Recuerda usar verificar."


def verificar():
    todo_ok, informe, funcionalidades = sensores.verificar_todo()
    memoria.marcar_verificacion(todo_ok, funcionalidades)
    return informe


def terminar(resumen):
    if not memoria.leer()["verificado"]:
        raise Bloqueado("No puedes terminar todavía: la última verificación no pasó "
                        "o hay cambios sin verificar. Usa verificar y corrige lo que falle.")
    return "ACEPTADO"


# ── Catálogo: lo que el modelo "ve" de cada herramienta ─────────────
CATALOGO = {
    "leer_archivo": {
        "funcion": leer_archivo,
        "descripcion": "Lee un archivo de tu carpeta de trabajo (por ejemplo, los tests).",
        "parametros": {"type": "object",
                       "properties": {"ruta": {"type": "string"}},
                       "required": ["ruta"]},
    },
    "escribir_archivo": {
        "funcion": escribir_archivo,
        "descripcion": "Crea o reemplaza un archivo en tu carpeta de trabajo.",
        "parametros": {"type": "object",
                       "properties": {"ruta": {"type": "string"},
                                      "contenido": {"type": "string"}},
                       "required": ["ruta", "contenido"]},
    },
    "verificar": {
        "funcion": verificar,
        "descripcion": "Ejecuta los tests y el linter y te dice qué falla y cómo corregirlo.",
        "parametros": {"type": "object", "properties": {}},
    },
    "terminar": {
        "funcion": terminar,
        "descripcion": "Declara la tarea terminada. Solo se acepta si la verificación pasó.",
        "parametros": {"type": "object",
                       "properties": {"resumen": {"type": "string"}},
                       "required": ["resumen"]},
    },
}


def ejecutar(nombre, argumentos):
    """Ejecuta una herramienta. Devuelve (texto_resultado, hubo_error)."""
    if nombre not in CATALOGO:
        return f"No existe la herramienta '{nombre}'.", True
    try:
        return CATALOGO[nombre]["funcion"](**argumentos), False
    except Bloqueado as motivo:
        return f"BLOQUEADO: {motivo}", True
    except Exception as error:   # el error vuelve al modelo como información útil
        return f"ERROR: {type(error).__name__}: {error}", True
