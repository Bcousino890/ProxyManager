from textstats.core import word_count
from tabulate import tabulate

result = [
    ["hola  mundo", word_count("hola  mundo")],
    ["uno dos tres", word_count("uno dos tres")]
]

print(tabulate(result, headers=["Texto", "Conteo de palabras"]))