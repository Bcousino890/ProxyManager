"""
Módulo de extractores.
"""
from .base import BaseExtractor, ExtractionResult
from .generic import GenericExtractor
from .idealista_html import IdealistaExtractor

__all__ = [
    'BaseExtractor',
    'ExtractionResult',
    'GenericExtractor',
    'IdealistaExtractor'
]