# Harness básico: un agente que programa con supervisión

**Agente = Modelo + Harness.** El modelo solo decide "qué hago ahora".
El harness es todo lo demás: las reglas, las herramientas, los controles y la memoria.

## Los componentes, un archivo cada uno

| # | Componente | Archivo | Qué hace |
|---|---|---|---|
| 1 | Guías (antes de actuar) | `AGENTS.md`, `guias.py` | Reglas que el modelo lee antes de empezar |
| 2 | Herramientas + guardarraíles | `herramientas.py` | Lo único que el modelo puede hacer, y lo que tiene prohibido |
| 3 | Sensores (después de actuar) | `sensores.py` | Tests + linter que le dicen qué falló y cómo corregirlo |
| 4 | Memoria | `memoria.py` | Guarda el progreso en `workspace/progreso.json` |
| 5 | Bucle de control | `bucle.py` | Modelo decide → harness ejecuta → resultado vuelve al modelo |
| — | El modelo (no es harness) | `modelos.py` | Simulado o Claude real; se pueden intercambiar |
| — | La tarea | `tarea.py` | El pedido y los tests que definen "terminado" |
| — | Ajustes / arranque | `config.py`, `main.py` | Carpeta de trabajo, límite de pasos, elegir modelo |

```
            AGENTS.md (guías)
                  │
                  ▼
  ┌────────► MODELO ── pide una herramienta ──┐
  │                                           ▼
  │                                  GUARDARRAÍLES ── ¿permitido? ── no ──► BLOQUEADO
  │                                           │ sí
  │                                           ▼
  │                                     HERRAMIENTA
  │                                           │
  └──── resultado + SENSORES ◄────────────────┘
                  │
                  ▼
           MEMORIA (progreso.json)
```

## Requisitos

Python 3.9 o superior. El modo simulado no necesita nada más.

## Prueba 1: modo simulado (sin llave, sin costo)

```bash
python main.py
```

Un modelo de mentira comete errores a propósito: escribe fuera de su carpeta, dice
"¡Listo!" sin verificar, intenta borrar los tests. Verás cómo el harness lo frena
y lo guía hasta la solución correcta.

## Prueba 2: con Claude real

1. Instala el SDK:
   ```bash
   pip install anthropic
   ```
2. Crea tu llave en https://platform.claude.com (sección **API Keys**).
3. En **esta misma carpeta**, copia `.env.example` como `.env`:
   - Mac / Linux: `cp .env.example .env`
   - Windows: `copy .env.example .env`
4. Abre `.env` y reemplaza `pega-aqui-tu-llave` por tu llave:
   ```
   ANTHROPIC_API_KEY=sk-ant-...
   ```
5. Ejecuta:
   ```bash
   python main.py --claude
   ```

El archivo `.env` está en `.gitignore`: nunca lo subas a GitHub ni lo compartas.
Para gastar menos, cambia `MODELO_CLAUDE=claude-haiku-5-5` en `.env`.

## Experimentos sugeridos

- Borra una regla de `AGENTS.md` y mira si Claude la sigue igual (sin guía).
- Quita el linter de `sensores.py` y revisa si aparecen `print()` en la solución (sin sensor).
- Cambia la tarea y los tests en `tarea.py`: el resto del harness no cambia.
