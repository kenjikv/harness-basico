"""
config.py — Ajustes generales del harness.
"""
from pathlib import Path

CARPETA = Path(__file__).parent          # carpeta del proyecto
WORKSPACE = CARPETA / "workspace"        # único lugar donde el agente puede escribir
MAX_PASOS = 15                           # freno de seguridad: el agente no puede girar para siempre
