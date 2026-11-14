import asyncio
import pytest
from scraping_engine.engine import WebScraper

@pytest.mark.asyncio
async def test_scrape_with_javascript():
    scraper = WebScraper()
    
    # Prueba con una página simple que no requiere JavaScript
    result = await scraper.scrape("https://httpbin.org/html", method="http")
    assert result["status_code"] == 200
    assert "html" in result
    
    # Prueba con JavaScript (usando una página que muestra contenido dinámico)
    result = await scraper.scrape("https://httpbin.org/redirect-to?url=https%3A%2F%2Fexample.com", method="javascript")
    assert result["status_code"] == 200
    assert "html" in result

if __name__ == "__main__":
    asyncio.run(test_scrape_with_javascript())