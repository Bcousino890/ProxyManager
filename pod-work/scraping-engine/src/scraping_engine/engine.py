import asyncio
import time
from typing import Optional, Dict, Any
from fastapi import FastAPI
from pydantic import BaseModel
import httpx
from playwright.async_api import async_playwright

class ScrapingRequest(BaseModel):
    url: str
    use_javascript: bool = False
    proxy_url: Optional[str] = None

class ScrapingResult(BaseModel):
    url: str
    status_code: int
    content_type: str
    content: str
    duration_ms: float
    is_datadome_blocked: bool
    error: Optional[str] = None

class ScrapingEngine:
    def __init__(self):
        self.app = FastAPI()
        self.setup_routes()

    def setup_routes(self):
        @self.app.get("/health")
        async def health():
            return {"status": "healthy"}

        @self.app.post("/scrape", response_model=ScrapingResult)
        async def scrape(request: ScrapingRequest):
            start_time = time.time()
            
            try:
                if request.use_javascript:
                    result = await self._scrape_with_playwright(request.url, request.proxy_url)
                else:
                    result = await self._scrape_with_httpx(request.url, request.proxy_url)
                
                duration = (time.time() - start_time) * 1000
                result.duration_ms = duration
                
                return result
            except Exception as e:
                duration = (time.time() - start_time) * 1000
                return ScrapingResult(
                    url=request.url,
                    status_code=500,
                    content_type="",
                    content="",
                    duration_ms=duration,
                    is_datadome_blocked=False,
                    error=str(e)
                )

    async def _scrape_with_httpx(self, url: str, proxy_url: Optional[str]) -> ScrapingResult:
        try:
            # Configurar el cliente httpx con proxy si se proporciona
            if proxy_url:
                # Para httpx, los proxies se pasan como un diccionario con claves 'http' y 'https'
                proxies = {
                    "http": proxy_url,
                    "https": proxy_url
                }
                async with httpx.AsyncClient(proxies=proxies) as client:
                    response = await client.get(url)
            else:
                async with httpx.AsyncClient() as client:
                    response = await client.get(url)
                    
            is_datadome = 'datadome' in response.headers.get('server', '').lower() or \
                          'datadome' in response.headers.get('x-datadome', '').lower()
            
            return ScrapingResult(
                url=url,
                status_code=response.status_code,
                content_type=response.headers.get('content-type', ''),
                content=response.text,
                duration_ms=0,
                is_datadome_blocked=is_datadome
            )
        except Exception as e:
            return ScrapingResult(
                url=url,
                status_code=500,
                content_type="",
                content="",
                duration_ms=0,
                is_datadome_blocked=False,
                error=str(e)
            )

    async def _scrape_with_playwright(self, url: str, proxy_url: Optional[str]) -> ScrapingResult:
        try:
            async with async_playwright() as p:
                # Usar el proxy si se proporciona
                launch_options = {"headless": True}
                if proxy_url:
                    launch_options["proxy"] = {"server": proxy_url}
                
                browser = await p.chromium.launch(**launch_options)
                page = await browser.new_page()
                response = await page.goto(url)
                
                content = await page.content()
                # Verificar si es bloqueado por DataDome
                is_datadome = False  # La verificación de DataDome en Playwright es compleja, se puede mejorar más adelante
                
                await browser.close()
                
                return ScrapingResult(
                    url=url,
                    status_code=response.status,
                    content_type="text/html",
                    content=content,
                    duration_ms=0,
                    is_datadome_blocked=is_datadome
                )
        except Exception as e:
            # Registrar el error para depuración
            print(f"Error en _scrape_with_playwright: {e}")
            return ScrapingResult(
                url=url,
                status_code=500,
                content_type="",
                content="",
                duration_ms=0,
                is_datadome_blocked=False,
                error=str(e)
            )

    def start(self, host: str = "127.0.0.1", port: int = 8000):
        import uvicorn
        uvicorn.run(self.app, host=host, port=port)