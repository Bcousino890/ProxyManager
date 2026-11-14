import asyncio
from typing import Optional, Dict, Any
from datetime import datetime
import logging

from .manager import JobManager, Job
from ..engines.http_engine import HttpEngine
from ..extractors.generic import GenericExtractor
from ..diagnostics.response_classifier import ResponseClassifier

logger = logging.getLogger(__name__)

class ScrapingWorker:
    """Trabajador de scraping."""
    
    def __init__(self, job_manager: JobManager):
        self.job_manager = job_manager
        self.http_engine = HttpEngine()
        self.extractor = GenericExtractor()
        self.classifier = ResponseClassifier()
        
    async def process_job(self, job_id: str) -> bool:
        """Procesa un trabajo de scraping."""
        try:
            # Obtener el trabajo
            job = await self.job_manager.get_job(job_id)
            if not job:
                logger.error(f"Trabajo no encontrado: {job_id}")
                return False
                
            # Actualizar estado a processing
            await self.job_manager.update_job(job_id, status="processing")
            
            # Realizar la solicitud HTTP
            response = await self.http_engine.get(job.url)
            
            # Clasificar la respuesta
            classification = self.classifier.classify(response)
            
            # Extraer datos
            extracted_data = self.extractor.extract(response.text)
            
            # Combinar resultados
            result = {
                "url": job.url,
                "timestamp": datetime.now().isoformat(),
                "classification": classification.__dict__,
                "extracted_data": extracted_data
            }
            
            # Actualizar el trabajo con resultados
            await self.job_manager.update_job(
                job_id, 
                status="completed", 
                result=result,
                updated_at=datetime.now()
            )
            
            logger.info(f"Trabajo completado: {job_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error procesando trabajo {job_id}: {str(e)}")
            await self.job_manager.update_job(
                job_id, 
                status="failed", 
                error=str(e),
                updated_at=datetime.now()
            )
            return False