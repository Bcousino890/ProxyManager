"""
Pruebas unitarias para extractores.
"""
import pytest
from scraping_engine.extractors import GenericExtractor, IdealistaExtractor, ExtractionResult


def test_generic_extractor():
    """Prueba el extractor genérico."""
    # Contenido HTML de ejemplo
    html_content = """
    <html>
        <head>
            <title>Ejemplo de página</title>
            <meta name="description" content="Página de ejemplo">
        </head>
        <body>
            <h1>Título principal</h1>
            <a href="/link1">Enlace 1</a>
            <img src="/image1.jpg" alt="Imagen 1">
            <p>Texto de ejemplo</p>
        </body>
    </html>
    """
    
    extractor = GenericExtractor()
    result = extractor.extract(html_content)
    
    assert isinstance(result, ExtractionResult)
    assert 'title' in result.data
    assert 'text' in result.data
    assert 'links' in result.data
    assert 'images' in result.data
    assert len(result.data['links']) == 1
    assert len(result.data['images']) == 1
    assert extractor.validate(result.data) is True


def test_idealista_extractor():
    """Prueba el extractor de Idealista."""
    # Contenido HTML de ejemplo (simulado)
    html_content = """
    <html>
        <body>
            <span data-testid="property-reference">REF-12345</span>
            <span data-testid="price">250.000 €</span>
            <span data-testid="property-type">Piso</span>
            <div data-testid="description">Descripción del inmueble</div>
        </body>
    </html>
    """
    
    extractor = IdealistaExtractor()
    result = extractor.extract(html_content)
    
    assert isinstance(result, ExtractionResult)
    assert 'reference' in result.data
    assert 'price' in result.data
    assert 'property_type' in result.data
    assert 'description' in result.data
    assert extractor.validate(result.data) is True


def test_extraction_result():
    """Prueba la clase ExtractionResult."""
    data = {'key': 'value'}
    metadata = {'source': 'test'}
    errors = ['error1']
    
    result = ExtractionResult(data=data, metadata=metadata, errors=errors)
    
    assert result.data == data
    assert result.metadata == metadata
    assert result.errors == errors