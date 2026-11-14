"""
Extractor genérico para HTML.
"""
import re
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup
from .base import BaseExtractor, ExtractionResult


class GenericExtractor(BaseExtractor):
    """Extractor genérico para contenido HTML."""
    
    def extract(self, content: str, **kwargs) -> ExtractionResult:
        """
        Extrae datos genéricos del contenido HTML.
        
        Args:
            content (str): Contenido HTML
            **kwargs: Parámetros adicionales
            
        Returns:
            ExtractionResult: Resultado de la extracción
        """
        soup = BeautifulSoup(content, 'html.parser')
        errors = []
        data = {}
        metadata = {}
        
        # Extraer título
        title_tag = soup.find('title')
        data['title'] = title_tag.get_text().strip() if title_tag else ''
        
        # Extraer metaetiquetas
        meta_tags = soup.find_all('meta')
        data['meta'] = {}
        for tag in meta_tags:
            name = tag.get('name') or tag.get('property')
            content = tag.get('content')
            if name and content:
                data['meta'][name] = content
        
        # Extraer enlaces
        links = soup.find_all('a', href=True)
        data['links'] = [link['href'] for link in links]
        
        # Extraer imágenes
        images = soup.find_all('img', src=True)
        data['images'] = [img['src'] for img in images]
        
        # Extraer texto plano
        text_content = soup.get_text()
        data['text'] = re.sub(r'\s+', ' ', text_content).strip()
        
        # Extraer encabezados
        headers = []
        for i in range(1, 7):
            header_tag = f'h{i}'
            headers.extend([h.get_text().strip() for h in soup.find_all(header_tag)])
        data['headers'] = headers
        
        # Extraer datos estructurados (JSON-LD)
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        data['structured_data'] = []
        for script in json_ld_scripts:
            try:
                import json
                data['structured_data'].append(json.loads(script.string))
            except Exception as e:
                errors.append(f"Error al parsear JSON-LD: {str(e)}")
        
        # Extraer atributos de elementos
        data['attributes'] = {}
        for tag in soup.find_all():
            if tag.attrs:
                tag_name = tag.name
                if tag_name not in data['attributes']:
                    data['attributes'][tag_name] = []
                data['attributes'][tag_name].append(tag.attrs)
        
        metadata['content_length'] = len(content)
        metadata['extracted_at'] = '2026-11-14T03:45:00Z'
        
        return ExtractionResult(data=data, metadata=metadata, errors=errors)
    
    def validate(self, data: Dict[str, Any]) -> bool:
        """
        Valida los datos extraídos.
        
        Args:
            data (Dict[str, Any]): Datos a validar
            
        Returns:
            bool: True si los datos son válidos
        """
        if not isinstance(data, dict):
            return False
        
        # Verificar que se extrajeron elementos esenciales
        required_fields = ['title', 'text']
        for field in required_fields:
            if field not in data:
                return False
                
        return True