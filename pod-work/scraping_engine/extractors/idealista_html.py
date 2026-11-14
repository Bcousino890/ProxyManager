"""
Extractor específico para Idealista.
"""

from typing import Dict, Any, List
from bs4 import BeautifulSoup
from .base import BaseExtractor, ExtractionResult


class IdealistaExtractor(BaseExtractor):
    """Extractor para datos inmobiliarios de Idealista."""

    def extract(self, content: str, **kwargs) -> ExtractionResult:
        """
        Extrae datos inmobiliarios del HTML de Idealista.

        Args:
            content (str): Contenido HTML de Idealista.
            **kwargs: Parámetros adicionales.

        Returns:
            ExtractionResult: Resultado con datos extraídos.
        """
        soup = BeautifulSoup(content, 'html.parser')

        # Extraer referencia
        reference = None
        ref_elem = soup.find('span', class_='re-ads-reference')
        if ref_elem:
            reference = ref_elem.get_text(strip=True)

        # Extraer tipo de operación
        operation_type = None
        op_elem = soup.find('span', class_='re-ads-operation-type')
        if op_elem:
            operation_type = op_elem.get_text(strip=True)

        # Extraer tipo de inmueble
        property_type = None
        prop_elem = soup.find('span', class_='re-ads-property-type')
        if prop_elem:
            property_type = prop_elem.get_text(strip=True)

        # Extraer precio
        price = None
        price_elem = soup.find('span', class_='re-ads-price')
        if price_elem:
            price = price_elem.get_text(strip=True)

        # Extraer superficie
        surface = None
        surface_elem = soup.find('span', class_='re-ads-surface')
        if surface_elem:
            surface = surface_elem.get_text(strip=True)

        # Extraer habitaciones
        rooms = None
        rooms_elem = soup.find('span', class_='re-ads-rooms')
        if rooms_elem:
            rooms = rooms_elem.get_text(strip=True)

        # Extraer baños
        bathrooms = None
        baths_elem = soup.find('span', class_='re-ads-bathrooms')
        if baths_elem:
            bathrooms = baths_elem.get_text(strip=True)

        # Extraer ubicación
        location = None
        loc_elem = soup.find('span', class_='re-ads-location')
        if loc_elem:
            location = loc_elem.get_text(strip=True)

        # Extraer características
        features = []
        feature_list = soup.find('ul', class_='re-ads-features-list')
        if feature_list:
            for li in feature_list.find_all('li'):
                features.append(li.get_text(strip=True))

        # Extraer descripción
        description = None
        desc_elem = soup.find('div', class_='re-ads-description')
        if desc_elem:
            description = desc_elem.get_text(strip=True)

        # Extraer imágenes
        images = []
        img_list = soup.find('div', class_='re-ads-images-list')
        if img_list:
            for img in img_list.find_all('img', src=True):
                images.append(img['src'])

        return ExtractionResult(
            data={
                'reference': reference,
                'operation_type': operation_type,
                'property_type': property_type,
                'price': price,
                'surface': surface,
                'rooms': rooms,
                'bathrooms': bathrooms,
                'location': location,
                'features': features,
                'description': description,
                'images': images
            },
            metadata={
                'content_length': len(content),
                'extracted_at': '2026-11-14T03:40:00Z'
            }
        )