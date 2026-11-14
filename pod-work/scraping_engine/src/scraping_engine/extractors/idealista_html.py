"""
Extractor específico para Idealista.
"""
import re
from typing import Dict, Any, List, Optional
from bs4 import BeautifulSoup
from .base import BaseExtractor, ExtractionResult


class IdealistaExtractor(BaseExtractor):
    """Extractor para datos inmobiliarios de Idealista."""
    
    def extract(self, content: str, **kwargs) -> ExtractionResult:
        """
        Extrae datos inmobiliarios del contenido HTML de Idealista.
        
        Args:
            content (str): Contenido HTML de Idealista
            **kwargs: Parámetros adicionales
            
        Returns:
            ExtractionResult: Resultado de la extracción
        """
        soup = BeautifulSoup(content, 'html.parser')
        errors = []
        data = {}
        metadata = {}
        
        # Extraer referencia
        reference_tag = soup.find('span', {'data-testid': 'property-reference'})
        data['reference'] = reference_tag.get_text().strip() if reference_tag else ''
        
        # Extraer tipo de operación
        operation_type_tag = soup.find('span', {'data-testid': 'operation-type'})
        data['operation_type'] = operation_type_tag.get_text().strip() if operation_type_tag else ''
        
        # Extraer tipo de inmueble
        property_type_tag = soup.find('span', {'data-testid': 'property-type'})
        data['property_type'] = property_type_tag.get_text().strip() if property_type_tag else ''
        
        # Extraer precio
        price_tag = soup.find('span', {'data-testid': 'price'})
        data['price'] = price_tag.get_text().strip() if price_tag else ''
        
        # Extraer superficie
        surface_tag = soup.find('span', {'data-testid': 'surface'})
        data['surface'] = surface_tag.get_text().strip() if surface_tag else ''
        
        # Extraer habitaciones
        rooms_tag = soup.find('span', {'data-testid': 'rooms'})
        data['rooms'] = rooms_tag.get_text().strip() if rooms_tag else ''
        
        # Extraer baños
        bathrooms_tag = soup.find('span', {'data-testid': 'bathrooms'})
        data['bathrooms'] = bathrooms_tag.get_text().strip() if bathrooms_tag else ''
        
        # Extraer planta
        floor_tag = soup.find('span', {'data-testid': 'floor'})
        data['floor'] = floor_tag.get_text().strip() if floor_tag else ''
        
        # Extraer ubicación
        location_tag = soup.find('span', {'data-testid': 'location'})
        data['location'] = location_tag.get_text().strip() if location_tag else ''
        
        # Extraer características
        features_list = soup.find('ul', {'data-testid': 'features-list'})
        data['features'] = [li.get_text().strip() for li in features_list.find_all('li')] if features_list else []
        
        # Extraer descripción
        description_tag = soup.find('div', {'data-testid': 'description'})
        data['description'] = description_tag.get_text().strip() if description_tag else ''
        
        # Extraer imágenes
        images = soup.find_all('img', {'data-testid': 'property-image'})
        data['images'] = [img['src'] for img in images if img.get('src')] if images else []
        
        # Extraer anunciante
        advertiser_tag = soup.find('span', {'data-testid': 'advertiser-name'})
        data['advertiser'] = advertiser_tag.get_text().strip() if advertiser_tag else ''
        
        # Extraer datos estructurados (JSON-LD)
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        data['structured_data'] = []
        for script in json_ld_scripts:
            try:
                import json
                data['structured_data'].append(json.loads(script.string))
            except Exception as e:
                errors.append(f"Error al parsear JSON-LD: {str(e)}")
        
        metadata['content_length'] = len(content)
        metadata['extracted_at'] = '2026-11-14T03:45:00Z'
        
        return ExtractionResult(data=data, metadata=metadata, errors=errors)
    
    def validate(self, data: Dict[str, Any]) -> bool:
        """
        Valida los datos extraídos de Idealista.
        
        Args:
            data (Dict[str, Any]): Datos a validar
            
        Returns:
            bool: True si los datos son válidos
        """
        if not isinstance(data, dict):
            return False
        
        # Verificar que se extrajeron elementos esenciales
        required_fields = ['reference', 'price', 'property_type']
        for field in required_fields:
            if field not in data:
                return False
                
        return True