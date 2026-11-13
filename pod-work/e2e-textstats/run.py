from textstats.core import word_count
from tabulate import tabulate

# Datos de prueba
data = [
    ("hola  mundo", word_count("hola  mundo")),
    ("uno dos tres", word_count("uno dos tres"))
]

# Imprimir tabla
print(tabulate(data, headers=["Texto", "Conteo de Palabras"], tablefmt="grid"))