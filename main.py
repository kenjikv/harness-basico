"""
main.py — Punto de entrada.

  python main.py            -> modelo simulado (sin llave, sin internet)
  python main.py --claude   -> Claude real (lee la llave del archivo .env)
"""
import os
import sys

from bucle import ejecutar_agente
from config import CARPETA
from modelos import ModeloClaude, ModeloSimulado


def cargar_env():
    """Lee el archivo .env (líneas CLAVE=valor) sin librerías extra."""
    archivo = CARPETA / ".env"
    if archivo.exists():
        for linea in archivo.read_text(encoding="utf-8").splitlines():
            linea = linea.strip()
            if linea and not linea.startswith("#") and "=" in linea:
                clave, valor = linea.split("=", 1)
                os.environ.setdefault(clave.strip(), valor.strip().strip('"').strip("'"))


def elegir_modelo():
    if "--claude" not in sys.argv:
        print("Modo: MODELO SIMULADO (guion fijo, no usa la API)")
        return ModeloSimulado()

    cargar_env()
    llave = os.environ.get("ANTHROPIC_API_KEY", "")
    if not llave or llave.startswith("pega-aqui"):
        sys.exit("Falta la llave. Copia .env.example como .env y pega tu ANTHROPIC_API_KEY.")
    nombre_modelo = os.environ.get("MODELO_CLAUDE", "claude-sonnet-5-5")
    print(f"Modo: CLAUDE REAL ({nombre_modelo})")
    return ModeloClaude(api_key=llave, modelo=nombre_modelo)


if __name__ == "__main__":
    ejecutar_agente(elegir_modelo())
