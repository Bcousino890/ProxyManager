"""Pruebas unitarias para el módulo de diagnóstico."""

import pytest
from unittest.mock import Mock

# Importar directamente desde el directorio src para evitar errores de importación
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from scraping_engine.diagnostics.response_classifier import (
    ResponseClassifier, 
    ResponseClassification,
    ProtectionType,
    ResponseStatus
)
from scraping_engine.diagnostics.protection_detector import ProtectionDetector, DetectionResult
from scraping_engine.diagnostics.evidence import Evidence


def test_response_classifier_success():
    """Prueba la clasificación de una respuesta exitosa."""
    
    classifier = ResponseClassifier()
    
    # Simular una respuesta HTTP exitosa
    classification = classifier.classify_response(
        http_status_code=200,
        headers={'content-type': 'text/html'},
        content='<html><head></head><body><h1>Test</h1></body></html>'
    )
    
    assert classification.http_status_code == 200
    assert classification.status == ResponseStatus.SUCCESS
    assert classification.protection_type == ProtectionType.NONE
    
    assert classification.status == ResponseStatus.SUCCESS
    assert classification.protection_type == ProtectionType.NONE
    assert classification.http_status_code == 200
    assert classification.is_accessible is True
    assert classification.is_content_valid is True


def test_response_classifier_datadome():
    """Prueba la clasificación de una respuesta con protección DataDome."""
    
    classifier = ResponseClassifier()
    
    # Simular encabezados con protección DataDome
    headers = {
        'content-type': 'text/html',
        'server': 'Datadome',
        'x-datadome': 'test'
    }
    
    classification = classifier.classify_response(
        http_status_code=403,
        headers=headers,
        content='<html><head></head><body><h1>Access Denied</h1></body></html>'
    )
    
    assert classification.status == ResponseStatus.DATA_DOME_CHALLENGE
    assert classification.protection_type == ProtectionType.DATADOME
    assert classification.http_status_code == 403
    assert classification.is_accessible is False


def test_response_classifier_empty_content():
    """Prueba la clasificación de contenido vacío."""
    
    classifier = ResponseClassifier()
    
    classification = classifier.classify_response(
        http_status_code=200,
        headers={'content-type': 'text/html'},
        content=''
    )
    
    assert classification.is_content_valid is False
    assert len(classification.evidence) > 0


def test_protection_detector_detection():
    """Prueba la detección de protección."""
    
    detector = ProtectionDetector()
    
    # Simular una respuesta con protección DataDome en encabezados
    classification = ResponseClassification(
        status=ResponseStatus.CLIENT_ERROR,
        protection_type=ProtectionType.NONE,
        http_status_code=403,
        headers={'server': 'Datadome'},
        content='<html><head></head><body><h1>Access Denied</h1></body></html>'
    )
    
    result = detector.detect(classification, classification.headers.get('content-type'))
    
    assert result.is_protected is True
    assert result.protection_type == ProtectionType.ACCESS_DENIED
    assert result.confidence > 0.0


def test_protection_detector_no_protection():
    """Prueba la detección cuando no hay protección."""
    
    detector = ProtectionDetector()
    
    classification = ResponseClassification(
        status=ResponseStatus.SUCCESS,
        protection_type=ProtectionType.NONE,
        http_status_code=200,
        headers={'content-type': 'text/html'},
        content='<html><head></head><body><h1>Test</h1></body></html>'
    )
    
    result = detector.detect(classification)
    
    assert result.is_protected is False
    assert result.protection_type == ProtectionType.NONE


def test_evidence_creation():
    """Prueba la creación de evidencia."""
    
    evidence = Evidence(
        indicator='datadome_header',
        description='Encabezado de protección DataDome detectado',
        confidence=0.95,
        source='header'
    )
    
    assert evidence.indicator == 'datadome_header'
    assert evidence.description == 'Encabezado de protección DataDome detectado'
    assert evidence.confidence == 0.95
    assert evidence.source == 'header'


def test_response_classifier_with_evidence():
    """Prueba la clasificación con evidencia."""
    
    classifier = ResponseClassifier()
    
    classification = classifier.classify(
        http_status_code=403,
        headers={'server': 'Datadome'},
        content='<html><head></head><body><h1>Access Denied</h1></body></html>'
    )
    
    assert len(classification.evidence) > 0
    assert any(e.indicator == 'datadome_header' for e in classification.evidence)


def test_protection_detector_get_info():
    """Prueba la obtención de información sobre protección."""
    
    detector = ProtectionDetector()
    
    info = detector.get_protection_info(ProtectionType.DATADOME)
    
    assert info['name'] == 'DataDome'
    assert 'protección anti-bot' in info['description']