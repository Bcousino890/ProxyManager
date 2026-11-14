import asyncio
import sys
from .engine import ScrapingEngine
from .proxy_manager import ProxyManager

def main():
    engine = ScrapingEngine()
    
    # Iniciar el motor en un puerto específico
    print("Iniciando motor de scraping en http://127.0.0.1:8000")
    engine.start(host="127.0.0.1", port=8000)

if __name__ == "__main__":
    main()