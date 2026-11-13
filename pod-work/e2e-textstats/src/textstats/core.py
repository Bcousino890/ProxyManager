def word_count(text: str) -> int:
    if not text:
        return 0
    # Usar split() sin argumentos para manejar múltiples espacios y saltos de línea
    return len(text.split())