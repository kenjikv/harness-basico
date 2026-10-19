"""
COMPONENTE 1 — GUÍAS (feedforward)

Lo que el agente sabe ANTES de actuar. Aquí son las reglas de AGENTS.md.
Si el agente comete un error que se repite, la mejora suele empezar aquí:
añadir una regla clara que lo prevenga.
"""
from config import CARPETA


def instrucciones_del_sistema():
    """Devuelve las reglas del proyecto que el modelo recibe como prompt de sistema."""
    return (CARPETA / "AGENTS.md").read_text(encoding="utf-8")
