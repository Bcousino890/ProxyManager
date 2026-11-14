"""
Módulo de registro para el motor de scraping.
"""
import logging
import os
from typing import Optional

from .config import ScraperConfig

def setup_logging(config: Optional[ScraperConfig] = None) -> logging.Logger:
    """Configura el logger del motor."""
    
    if config is None:
        config = ScraperConfig()
        
    # Configurar el logger raíz
    logger = logging.getLogger("scraping_engine")
    logger.setLevel(getattr(logging, config.LOG_LEVEL))
    
    # Evitar duplicados si ya está configurado
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
    return logger