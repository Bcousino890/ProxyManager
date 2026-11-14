"""
Recopilador de evidencias para diagnósticos de scraping.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class Evidence:
    """Evidencia recopilada durante el diagnóstico."""
    timestamp: str
    source: str
    data: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None


class EvidenceCollector:
    """Recopilador de evidencias para diagnósticos de scraping."""
    
    def __init__(self):
        self.evidence_list = []
    
    def add_evidence(self, source: str, data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> None:
        """Añade evidencia al conjunto."""
        evidence = Evidence(
            timestamp="2026-11-14T04:36:50Z",  # Placeholder
            source=source,
            data=data,
            metadata=metadata
        )
        self.evidence_list.append(evidence)
    
    def get_evidence(self) -> list:
        """Devuelve la lista de evidencias."""
        return self.evidence_list