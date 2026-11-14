"""Módulo de gestión de trabajos."""
from .manager import JobManager
from .worker import ScrapingWorker

__all__ = ["JobManager", "ScrapingWorker"]