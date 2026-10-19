"""
COMPONENTE 3 — SENSORES (feedback)

Revisan el trabajo DESPUÉS de que el agente actúa y le devuelven mensajes
claros para que se corrija solo. Aquí hay dos sensores computacionales
(rápidos y deterministas):
  - tests:  ¿el código hace lo que debe?
  - linter: ¿el código respeta las reglas del proyecto?
"""
import ast
import subprocess
import sys

from config import WORKSPACE
from tarea import ARCHIVO_SOLUCION, ARCHIVO_TESTS, FUNCIONALIDADES


def sensor_tests():
    """Ejecuta los tests. Devuelve {nombre_test: 'ok' | 'FAIL' | 'ERROR'} y un detalle corto."""
    modulo = ARCHIVO_TESTS.removesuffix(".py")
    proceso = subprocess.run(
        [sys.executable, "-m", "unittest", "-v", modulo],
        cwd=WORKSPACE, capture_output=True, text=True, timeout=30,
    )
    salida = proceso.stdout + proceso.stderr
    resultados = {}
    for linea in salida.splitlines():
        if linea.startswith("test_") and " ... " in linea:
            resultados[linea.split()[0]] = linea.rsplit("... ", 1)[1].strip()
    detalle = salida[-500:]   # recortamos: el modelo no necesita 300 líneas de log
    return resultados, detalle


def sensor_linter():
    """Revisa las reglas de AGENTS.md y propone la corrección en cada mensaje."""
    archivo = WORKSPACE / ARCHIVO_SOLUCION
    if not archivo.exists():
        return [f"No existe {ARCHIVO_SOLUCION}. Créalo con escribir_archivo."]
    try:
        arbol = ast.parse(archivo.read_text(encoding="utf-8"))
    except SyntaxError as error:
        return [f"Error de sintaxis en la línea {error.lineno}: {error.msg}."]

    problemas = []
    for nodo in ast.walk(arbol):
        es_funcion_publica = isinstance(nodo, ast.FunctionDef) and not nodo.name.startswith("_")
        if es_funcion_publica and ast.get_docstring(nodo) is None:
            problemas.append(
                f"Línea {nodo.lineno}: '{nodo.name}' no tiene docstring. "
                "Corrección: agrega un docstring de una línea debajo del def.")
        es_print = (isinstance(nodo, ast.Call) and isinstance(nodo.func, ast.Name)
                    and nodo.func.id == "print")
        if es_print:
            problemas.append(f"Línea {nodo.lineno}: hay un print(). Corrección: elimínalo.")
    return problemas


def verificar_todo():
    """Corre ambos sensores. Devuelve (todo_ok, informe_para_el_modelo, funcionalidades)."""
    resultados, detalle = sensor_tests()
    problemas = sensor_linter()

    funcionalidades = {nombre: resultados.get(test) == "ok"
                       for nombre, test in FUNCIONALIDADES.items()}
    todo_ok = all(funcionalidades.values()) and not problemas

    lineas = ["TESTS:"]
    lineas += [f"  {'✔' if estado == 'ok' else '✘'} {test}: {estado}"
               for test, estado in resultados.items()]
    if not resultados or any(estado != "ok" for estado in resultados.values()):
        lineas.append("  Detalle del fallo:\n" + detalle)
    lineas.append("LINTER:" + ("  sin problemas" if not problemas else ""))
    lineas += [f"  - {problema}" for problema in problemas]
    lineas.append("RESULTADO: " + ("TODO PASA" if todo_ok else "HAY PROBLEMAS, corrígelos"))
    return todo_ok, "\n".join(lineas), funcionalidades
