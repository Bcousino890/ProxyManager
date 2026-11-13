import textstats.core
from tabulate import tabulate

data = [
    ["hola  mundo", textstats.core.word_count("hola  mundo")],
    ["uno dos tres", textstats.core.word_count("uno dos tres")]
]
print(tabulate(data, headers=["Text", "Word Count"]))