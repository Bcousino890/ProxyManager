import os
from typing import List, Optional
import httpx
import asyncio

PROXY_FILE = "proxies.txt"

class ProxyManager:
    def __init__(self):
        self.proxies: List[str] = []
        self._load_proxies()
    
    def _load_proxies(self):
        """Carga los proxies desde el archivo PROXY_FILE."""
        if not os.path.exists(PROXY_FILE):
            print(f"Advertencia: No se encontró {PROXY_FILE}")
            return
        
        with open(PROXY_FILE, 'r') as f:
            self.proxies = [line.strip() for line in f if line.strip()]
    
    def get_proxies(self) -> List[str]:
        """Devuelve la lista de proxies cargados."""
        return self.proxies
    
    async def test_proxy(self, proxy_url: str, test_url: str = "https://httpbin.org/ip") -> dict:
        """Verifica conectividad y autenticación del proxy."""
        try:
            async with httpx.AsyncClient(proxies=proxy_url, timeout=10.0) as client:
                response = await client.get(test_url)
                return {
                    'proxy': proxy_url,
                    'status': 'active',
                    'ip': response.json().get('origin', 'unknown'),
                    'latency_ms': response.elapsed.total_seconds() * 1000,
                    'error': None
                }
        except Exception as e:
            return {
                'proxy': proxy_url,
                'status': 'inactive',
                'ip': 'unknown',
                'latency_ms': 0,
                'error': str(e)
            }

    async def test_all_proxies(self, test_url: str = "https://httpbin.org/ip") -> List[dict]:
        """Prueba todos los proxies y devuelve un listado con resultados."""
        tasks = [self.test_proxy(proxy, test_url) for proxy in self.proxies]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filtrar excepciones
        clean_results = []
        for result in results:
            if isinstance(result, dict):
                clean_results.append(result)
            else:
                print(f"Error al probar proxy: {result}")
        
        return clean_results