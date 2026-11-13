import textstats.core

def test_word_count_double_space():
    assert textstats.core.word_count("hola  mundo") == 2

def test_word_count_empty():
    assert textstats.core.word_count("") == 0

def test_word_count_three_words():
    assert textstats.core.word_count("uno dos tres") == 3