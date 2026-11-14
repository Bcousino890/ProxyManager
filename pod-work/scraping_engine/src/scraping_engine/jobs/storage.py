"""
Almacén de trabajos para persistencia.
"""
import sqlite3
from typing import Optional, List
from dataclasses import dataclass
from datetime import datetime

@dataclass
class JobRecord:
    id: str
    url: str
    status: str
    created_at: datetime
    updated_at: datetime
    result: Optional[str] = None

class JobStorage:
    def __init__(self, db_path: str = "jobs.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY,
                url TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL,
                updated_at TIMESTAMP NOT NULL,
                result TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def save_job(self, job: JobRecord):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO jobs (id, url, status, created_at, updated_at, result)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            job.id,
            job.url,
            job.status,
            job.created_at,
            job.updated_at,
            job.result
        ))
        conn.commit()
        conn.close()

    def get_job(self, job_id: str) -> Optional[JobRecord]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM jobs WHERE id = ?', (job_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return JobRecord(
                id=row[0],
                url=row[1],
                status=row[2],
                created_at=datetime.fromisoformat(row[3]),
                updated_at=datetime.fromisoformat(row[4]),
                result=row[5]
            )
        return None

    def get_all_jobs(self) -> List[JobRecord]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM jobs')
        rows = cursor.fetchall()
        conn.close()
        
        jobs = []
        for row in rows:
            jobs.append(JobRecord(
                id=row[0],
                url=row[1],
                status=row[2],
                created_at=datetime.fromisoformat(row[3]),
                updated_at=datetime.fromisoformat(row[4]),
                result=row[5]
            ))
        return jobs

    def update_job_status(self, job_id: str, status: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE jobs SET status = ?, updated_at = ? WHERE id = ?
        ''', (status, datetime.now(), job_id))
        conn.commit()
        conn.close()