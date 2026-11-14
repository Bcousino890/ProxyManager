import asyncio
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import uuid

@dataclass
class Job:
    id: str
    url: str
    status: str = "pending"
    created_at: datetime = None
    updated_at: datetime = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()

class JobManager:
    """Gestor de trabajos de scraping."""
    
    def __init__(self):
        self.jobs: Dict[str, Job] = {}
        self._lock = asyncio.Lock()
        
    async def create_job(self, url: str) -> Job:
        """Crea un nuevo trabajo."""
        job_id = str(uuid.uuid4())
        job = Job(id=job_id, url=url)
        async with self._lock:
            self.jobs[job_id] = job
        return job
        
    async def get_job(self, job_id: str) -> Optional[Job]:
        """Obtiene un trabajo por ID."""
        async with self._lock:
            return self.jobs.get(job_id)
            
    async def update_job(self, job_id: str, **kwargs) -> bool:
        """Actualiza un trabajo."""
        async with self._lock:
            if job_id not in self.jobs:
                return False
            job = self.jobs[job_id]
            for key, value in kwargs.items():
                if hasattr(job, key):
                    setattr(job, key, value)
            job.updated_at = datetime.now()
            return True
            
    async def delete_job(self, job_id: str) -> bool:
        """Elimina un trabajo."""
        async with self._lock:
            if job_id in self.jobs:
                del self.jobs[job_id]
                return True
            return False
            
    async def list_jobs(self) -> Dict[str, Job]:
        """Lista todos los trabajos."""
        async with self._lock:
            return self.jobs.copy()