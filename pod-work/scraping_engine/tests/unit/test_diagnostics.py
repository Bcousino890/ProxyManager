"""
Pruebas unitarias para el módulo de diagnóstico.
"""

import pytest
from unittest.mock import patch, MagicMock

from scraping_engine.diagnostics.response_classifier import (
    ResponseClassifier,
    ResponseClassification,
    ResponseStatus,
    ProtectionType
)
from scraping_engine.diagnostics.protection_detector import (
    ProtectionDetector,
    DetectionResult
)


def test_response_classifier_basic():
    """Prueba la clasificación básica de respuestas."""
    
    classifier = ResponseClassifier()
    
    # Simular una respuesta HTTP 200 con contenido
    response = {
        'http_status_code': 200,
        'headers': {'content-type': 'text/html'},
        'content': '<html><body>Test</body></html>',
        'response_time': 1.0
    }
    
    classification = classifier.classify_response(**response)
    
    assert classification.status == ResponseStatus.SUCCESS
    assert classification.protection_type == ProtectionType.NONE
    assert classification.http_status_code == 200
    assert classification.content_length == 34


def test_response_classifier_data_dome():
    """Prueba la clasificación de respuestas con protección DataDome."""
    
    classifier = ResponseClassifier()
    
    # Simular una respuesta con protección DataDome en encabezados
    response = {
        'status_code': 403,
        'headers': {'server': 'Datadome'},
        'content': '<html><body>DataDome challenge</body></html>',
        'response_time': 1.5
    }
    
    classification = classifier.classify_response(**response)
    
    assert classification.status == ResponseStatus.CLIENT_ERROR
    assert classification.protection_type == ProtectionType.DATADOME
    assert classification.http_status_code == 403


def test_protection_detector_no_protection():
    """Prueba la detección de protección sin protección."""
    
    detector = ProtectionDetector()
    
    # Simular una respuesta sin protección
    result = detector.detect_protection(
        http_status_code=200,
        headers={},
        content=b'<html><body>Test</body></html>',
        response_time=1.0
    )
    
    assert result.is_protected is False
    assert result.protection_type == ProtectionType.NONE


def test_response_classifier_empty_content():
    """Prueba la clasificación con contenido vacío."""
    
    classifier = ResponseClassifier()
    
    # Simular una respuesta HTTP 200 sin contenido
    response = {
        'status_code': 200,
        'headers': {'content-type': 'text/html'},
        'content': '',
        'response_time': 1.0
    }
    
    classification = classifier.classify_response(**response)
    
    assert classification.content_length == 0


def test_response_classifier_timeout():
    """Prueba la clasificación de timeout."""
    
    classifier = ResponseClassifier()
    
    # Simular un timeout
    response = {
        'status_code': 0,
        'headers': {},
        'content': '',
        'response_time': 30.0
    }
    
    classification = classifier.classify_response(**response)
    
    assert classification.status == ResponseStatus.TIMEOUT


def test_detection_result_repr():
    """Prueba la representación del resultado de detección."""
    
    result = DetectionResult(
        is_protected=True,
        protection_type=ProtectionType.DATADOME,
        evidence=[],
        detection_time=1.0
    )
    
    repr_str = repr(result)
    assert 'DetectionResult' in repr_str
    assert 'DATADOME' in repr_str
