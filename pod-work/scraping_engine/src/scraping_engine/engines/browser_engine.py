"""
Motor de navegador para scraping asíncrono basado en Playwright.
"""
import asyncio
import time
from typing import Optional, Dict, Any
from dataclasses import dataclass
from playwright.async_api import async_playwright, Page, BrowserContext
from .base import BaseEngine, ScrapingResult


@dataclass
class BrowserConfig:
    """Configuración del motor de navegador."""
    timeout: int = 30000  # 30 segundos
    headless: bool = True
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    viewport: Dict[str, int] = None
    proxy: Optional[str] = None
    extra_http_headers: Optional[Dict[str, str]] = None
    ignore_https_errors: bool = False


class BrowserEngine(BaseEngine):
    """Motor de navegador para scraping asíncrono."""
    
    def __init__(self, config: BrowserConfig = None):
        self.config = config or BrowserConfig()
        self.playwright = None
        self.browser = None
        self.context = None
        
    async def __aenter__(self):
        """Inicializa el navegador."""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=self.config.headless,
            proxy={"server": self.config.proxy} if self.config.proxy else None
        )
        
        # Crear contexto con configuración
        self.context = await self.browser.new_context(
            user_agent=self.config.user_agent,
            viewport=self.config.viewport,
            ignore_https_errors=self.config.ignore_https_errors,
            extra_http_headers=self.config.extra_http_headers or {}
        )
        
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Cierra el navegador."""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
            
    async def navigate(self, url: str) -> Page:
        """Navega a una URL y devuelve la página."""
        page = await self.context.new_page()
        await page.goto(url, timeout=self.config.timeout)
        return page
        
    async def get(self, url: str) -> ScrapingResult:
        """Realiza una solicitud GET usando el navegador."""
        start_time = time.time()
        
        try:
            page = await self.context.new_page()
            await page.goto(url, timeout=self.config.timeout)
            
            # Obtener contenido HTML
            content = await page.content()
            
            # Obtener encabezados (no disponibles directamente en Playwright)
            headers = {}
            
            # Calcular tiempo de respuesta
            response_time = time.time() - start_time
            
            # Obtener información de la página
            status_code = 200  # En este caso, asumimos éxito
            
            return ScrapingResult(
                url=url,
                status_code=status_code,
                headers=headers,
                content=content,
                response_time=response_time,
                content_length=len(content),
                error=None
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            return ScrapingResult(
                url=url,
                status_code=0,
                headers={},
                content="",
                response_time=response_time,
                content_length=0,
                error=str(e)
            )
            
    async def post(self, url: str, data: Optional[Dict] = None, json: Optional[Dict] = None) -> ScrapingResult:
        """Realiza una solicitud POST usando el navegador."""
        # Para POST en Playwright, se puede usar page.evaluate o form submission
        start_time = time.time()
        
        try:
            page = await self.context.new_page()
            
            # Navegar a la URL
            await page.goto(url, timeout=self.config.timeout)
            
            # Si hay datos para enviar, hacer un formulario submit o usar JS
            if data or json:
                # Usar JavaScript para enviar datos (ejemplo simple)
                await page.evaluate("""
                    (data) => {
                        const form = document.createElement('form');
                        form.method = 'POST';
                        form.action = window.location.href;
                        
                        for (const key in data) {
                            const input = document.createElement('input');
                            input.type = 'hidden';
                            input.name = key;
                            input.value = data[key];
                            form.appendChild(input);
                        }
                        
                        document.body.appendChild(form);
                        form.submit();
                    }
                """, data or json)
                
                # Esperar un poco para que se cargue la nueva página
                await page.wait_for_timeout(1000)
            
            # Obtener contenido HTML
            content = await page.content()
            
            # Calcular tiempo de respuesta
            response_time = time.time() - start_time
            
            # Obtener información de la página
            status_code = 200  # En este caso, asumimos éxito
            
            return ScrapingResult(
                url=url,
                status_code=status_code,
                headers={},
                content=content,
                response_time=response_time,
                content_length=len(content),
                error=None
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            return ScrapingResult(
                url=url,
                status_code=0,
                headers={},
                content="",
                response_time=response_time,
                content_length=0,
                error=str(e)
            )