import pytest
from textstats.core import word_count

def test_word_count():
    assert word_count("hola  mundo") == 2  # Dos espacios seguidos, debe ser 2 palabras
    assert word_count("") == 0
    assert word_count("uno dos tres") == 3