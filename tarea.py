"""
tarea.py — QUÉ debe hacer el agente y CÓMO sabremos que lo logró.

La tarea es el pedido. Los tests son la definición de "terminado":
no basta con que el agente diga "listo", los tests tienen que pasar.
"""

TAREA = (
    "Crea la función es_palindromo(texto) en palindromo.py. Debe devolver True si el "
    "texto se lee igual al derecho y al revés, ignorando espacios y mayúsculas. "
    "Ejemplo: 'Anita lava la tina' -> True; 'hola' -> False."
)

ARCHIVO_SOLUCION = "palindromo.py"
ARCHIVO_TESTS = "test_palindromo.py"

TESTS = '''import unittest
from palindromo import es_palindromo


class TestPalindromo(unittest.TestCase):
    def test_palabra_simple(self):
        self.assertTrue(es_palindromo("radar"))

    def test_no_es_palindromo(self):
        self.assertFalse(es_palindromo("hola"))

    def test_frase_con_espacios_y_mayusculas(self):
        self.assertTrue(es_palindromo("Anita lava la tina"))
'''

# Cada funcionalidad se comprueba con un test concreto (la "lista de pendientes").
FUNCIONALIDADES = {
    "palabra simple": "test_palabra_simple",
    "detecta lo que NO es palíndromo": "test_no_es_palindromo",
    "ignora espacios y mayúsculas": "test_frase_con_espacios_y_mayusculas",
}
