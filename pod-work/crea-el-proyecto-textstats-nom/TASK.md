# Tarea

Crea el proyecto "textstats" (nombre de carpeta: e2e-textstats). Haz esto paso a paso con herramientas reales y verifica cada paso:
1. Define un plan con plan(action=set) y crea el proyecto con project_init.
2. Crea un venv .venv dentro del proyecto e instala con pip las dependencias `pytest` y `tabulate`.
3. Escribe src/textstats/__init__.py vacío y src/textstats/core.py con exactamente esta función (tiene un fallo conocido que debes detectar con las pruebas, NO lo corrijas todavía):
def word_count(text: str) -> int:
    return len(text.split(" "))
4. Escribe run.py (en la raíz del proyecto) que importe textstats.core y use tabulate para imprimir una tabla con el conteo de palabras de "hola  mundo" y de "uno dos tres". Ejecútalo.
5. Escribe tests/test_core.py con pytest: word_count("hola  mundo") debe ser 2 (dos espacios seguidos), word_count("") debe ser 0 y word_count("uno dos tres") debe ser 3. Crea pyproject.toml mínimo con pythonpath de pytest en src. Ejecuta run_tests.
6. Si las pruebas fallan, diagnostica la causa y corrige core.py, y vuelve a ejecutar run_tests hasta que pasen.
7. Haz git_commit con un mensaje descriptivo y luego git_push a la rama configurada; comprueba el estado con git_status.
Al final marca cada tarea del plan como done con evidencia y resume qué comprobaste.
