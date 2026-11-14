import pytest
from scraping_engine.core.base import BaseEngine, ScrapingResult


def test_scraping_result():
    """Prueba la clase ScrapingResult."""
    result = ScrapingResult(
        success=True,
        content="test content",
        metadata={"key": "value"},
        error=None,
        response_time=0.5
    )
    
    assert result.success is True
    assert result.content == "test content"
    assert result.metadata == {"key": "value"}
    assert result.error is None
    assert result.response_time == 0.5


def test_scraping_result_default():
    """Prueba la clase ScrapingResult con valores por defecto."""
    result = ScrapingResult(success=False)
    
    assert result.success is False
    assert result.content is None
    assert result.metadata is None
    assert result.error is None
    assert result.response_time is None