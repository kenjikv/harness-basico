"""
COMPONENTE 4 — MEMORIA (estado persistente)

El modelo "olvida" todo entre sesiones. El harness guarda en disco:
  - qué funcionalidades pasan y cuáles no
  - si el último código fue verificado
  - una bitácora de cada paso
Así cualquier persona (u otro agente) puede ver qué pasó y retomar el trabajo.
"""
import json

from config import WORKSPACE
from tarea import FUNCIONALIDADES, TAREA

ARCHIVO = WORKSPACE / "progreso.json"


def iniciar():
    """Crea el archivo de progreso desde cero."""
    guardar({
        "tarea": TAREA,
        "funcionalidades": {nombre: False for nombre in FUNCIONALIDADES},
        "verificado": False,
        "bitacora": [],
    })


def leer():
    """Lee el estado actual."""
    return json.loads(ARCHIVO.read_text(encoding="utf-8"))


def guardar(estado):
    """Escribe el estado en disco."""
    ARCHIVO.write_text(json.dumps(estado, indent=2, ensure_ascii=False), encoding="utf-8")


def marcar_verificacion(todo_ok, funcionalidades):
    """Registra el resultado de la última verificación."""
    estado = leer()
    estado["verificado"] = todo_ok
    estado["funcionalidades"] = funcionalidades
    guardar(estado)


def invalidar_verificacion():
    """Cualquier cambio en el código anula la verificación anterior."""
    estado = leer()
    estado["verificado"] = False
    guardar(estado)


def anotar_paso(numero, herramienta, resultado):
    """Añade una línea a la bitácora."""
    estado = leer()
    estado["bitacora"].append({
        "paso": numero,
        "herramienta": herramienta,
        "resultado": resultado.splitlines()[0] if resultado else "",
    })
    guardar(estado)
