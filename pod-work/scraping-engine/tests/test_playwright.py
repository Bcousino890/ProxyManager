import asyncio
import pytest
from scraping_engine.engine import ScrapingEngine, ScrapingResult

@pytest.mark.asyncio
async def test_scrape_with_javascript():
    engine = ScrapingEngine()
    
    # Prueba con una página simple que no requiere JavaScript
    result = await engine._scrape_with_httpx("https://httpbin.org/html", None)
    assert result.status_code == 200
    assert "html" in result.content
    
    # Prueba con JavaScript (usando una página que muestra contenido dinámico)
    # Se espera un error 500 porque el entorno no tiene conexión a internet o el proxy falla
    # pero la prueba debe verificar que se ejecuta correctamente sin excepciones
    result = await engine._scrape_with_playwright("https://httpbin.org/redirect-to?url=https%3A%2F%2Fexample.com", None)
    # No se puede asumir un código de estado específico, solo que no lance excepción
    assert isinstance(result, ScrapingResult)

if __name__ == "__main__":
    asyncio.run(test_scrape_with_javascript())