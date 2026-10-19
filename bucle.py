"""
COMPONENTE 5 — EL BUCLE DE CONTROL

El corazón del harness. Repite:
  1. el modelo elige una acción
  2. el harness la ejecuta (pasando por los guardarraíles)
  3. el resultado vuelve al modelo y queda anotado en la memoria
hasta que la tarea se ACEPTA o se acaban los pasos.
"""
import shutil

import guias
import herramientas
import memoria
from config import MAX_PASOS, WORKSPACE
from tarea import ARCHIVO_TESTS, TAREA, TESTS


def preparar_entorno():
    """Paso inicial: carpeta limpia, tests en su lugar y memoria en blanco."""
    if WORKSPACE.exists():
        shutil.rmtree(WORKSPACE)
    WORKSPACE.mkdir()
    (WORKSPACE / ARCHIVO_TESTS).write_text(TESTS, encoding="utf-8")
    memoria.iniciar()


def resumir(argumentos):
    """Versión corta de los argumentos, para que la traza se lea fácil."""
    return ", ".join(
        f"{clave}={valor[:30] + '…' if isinstance(valor, str) and len(valor) > 30 else valor!r}"
        for clave, valor in argumentos.items())


def ejecutar_agente(modelo):
    preparar_entorno()
    modelo.iniciar(guias.instrucciones_del_sistema(), TAREA, herramientas.CATALOGO)

    resultado, hubo_error = None, False
    for paso in range(1, MAX_PASOS + 1):
        nombre, argumentos = modelo.siguiente_accion(resultado, hubo_error)
        print(f"\n[{paso}] 🤖 modelo  → {nombre}({resumir(argumentos)})")

        resultado, hubo_error = herramientas.ejecutar(nombre, argumentos)
        icono = "⛔" if hubo_error else "🛠️ "
        print(f"    {icono} harness → " + resultado.replace("\n", "\n                 "))

        memoria.anotar_paso(paso, nombre, resultado)

        if nombre == "terminar" and resultado == "ACEPTADO":
            print(f"\n✅ Tarea completada y verificada en {paso} pasos.")
            return True

    print(f"\n⛔ Se alcanzó el límite de {MAX_PASOS} pasos sin terminar.")
    return False
