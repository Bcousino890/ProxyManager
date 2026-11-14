"""
Motor HTTP asíncrono basado en httpx para scraping.
"""
import asyncio
import time
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from httpx import AsyncClient, Response, TimeoutException, ConnectError, ReadTimeout
import httpx

@dataclass
class ScrapingResult:
    """Resultado de una solicitud HTTP."""
    url: str
    status_code: int
    headers: Dict[str, str]
    content: str
    response_time: float
    error: Optional[str] = None
    proxy_used: Optional[str] = None
    cookies: Optional[Dict[str, str]] = None

class HTTPEngine:
    """Motor HTTP para scraping asíncrono."""
    
    def __init__(self, 
                 timeout: int = 30,
                 max_retries: int = 3,
                 concurrency_limit: int = 10,
                 follow_redirects: bool = True):
        self.timeout = timeout
        self.max_retries = max_retries
        self.concurrency_limit = concurrency_limit
        self.follow_redirects = follow_redirects
        self.client = None
        
    async def __aenter__(self):
        """Inicia el cliente HTTP."""
        limits = httpx.Limits(max_connections=self.concurrency_limit, max_keepalive_connections=self.concurrency_limit)
        timeout = httpx.Timeout(self.timeout)
        
        self.client = AsyncClient(
            limits=limits,
            timeout=timeout,
            follow_redirects=self.follow_redirects
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Cierra el cliente HTTP."""
        if self.client:
            await self.client.aclose()
            
    async def get(self, 
                  url: str,
                  headers: Optional[Dict[str, str]] = None,
                  cookies: Optional[Dict[str, str]] = None,
                  proxy: Optional[str] = None) -> ScrapingResult:
        """Realiza una solicitud GET."""
        return await self._request('GET', url, headers=headers, cookies=cookies, proxy=proxy)
        
    async def post(self, 
                   url: str,
                   data: Optional[Dict[str, Any]] = None,
                   headers: Optional[Dict[str, str]] = None,
                   cookies: Optional[Dict[str, str]] = None,
                   proxy: Optional[str] = None) -> ScrapingResult:
        """Realiza una solicitud POST."""
        return await self._request('POST', url, data=data, headers=headers, cookies=cookies, proxy=proxy)
        
    async def _request(self, 
                       method: str,
                       url: str,
                       data: Optional[Dict[str, Any]] = None,
                       headers: Optional[Dict[str, str]] = None,
                       cookies: Optional[Dict[str, str]] = None,
                       proxy: Optional[str] = None) -> ScrapingResult:
        """Realiza una solicitud HTTP con reintentos."""
        start_time = time.time()
        error = None
        response = None
        
        # Configurar proxy
        proxies = {"http://": proxy, "https://": proxy} if proxy else None
        
        for attempt in range(self.max_retries):
            try:
                if method == 'GET':
                    response = await self.client.get(
                        url,
                        headers=headers,
                        cookies=cookies,
                        proxies=proxies
                    )
                elif method == 'POST':
                    response = await self.client.post(
                        url,
                        data=data,
                        headers=headers,
                        cookies=cookies,
                        proxies=proxies
                    )
                
                # Verificar si la respuesta es válida
                if response is not None:
                    content = response.text
                    return ScrapingResult(
                        url=url,
                        status_code=response.status_code,
                        headers=dict(response.headers),
                        content=content,
                        response_time=time.time() - start_time,
                        proxy_used=proxy,
                        cookies=dict(response.cookies)
                    )
                    
            except (TimeoutException, ConnectError, ReadTimeout) as e:
                error = str(e)
                if attempt < self.max_retries - 1:  # No esperar si es el último intento
                    await asyncio.sleep(2 ** attempt)  # Retraso exponencial
                continue
            except Exception as e:
                error = str(e)
                break
                
        return ScrapingResult(
            url=url,
            status_code=0,
            headers={},
            content="",
            response_time=time.time() - start_time,
            error=error,
            proxy_used=proxy
        )