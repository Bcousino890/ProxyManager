import pytest
import asyncio
from scraping_engine.engine import ScrapingEngine

@pytest.mark.asyncio
async def test_health_endpoint():
    engine = ScrapingEngine()
    # Simular una solicitud GET a /health
    from fastapi.testclient import TestClient
    client = TestClient(engine.app)
    
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

@pytest.mark.asyncio
async def test_scrape_endpoint():
    engine = ScrapingEngine()
    from fastapi.testclient import TestClient
    client = TestClient(engine.app)
    
    # Prueba con una URL válida (página de prueba)
    response = client.post("/scrape", json={"url": "https://httpbin.org/get"})
    assert response.status_code == 200