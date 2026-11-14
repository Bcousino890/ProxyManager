"""
Extractor genérico para HTML.
"""

from typing import Dict, Any, List
from bs4 import BeautifulSoup
from .base import BaseExtractor, ExtractionResult


class GenericExtractor(BaseExtractor):
    """Extractor genérico para contenido HTML."""

    def extract(self, content: str, **kwargs) -> ExtractionResult:
        """
        Extrae elementos básicos del HTML.

        Args:
            content (str): Contenido HTML.
            **kwargs: Parámetros adicionales.

        Returns:
            ExtractionResult: Resultado con datos extraídos.
        """
        soup = BeautifulSoup(content, 'html.parser')

        # Extraer título
        title = soup.title.string if soup.title else None

        # Extraer metaetiquetas
        meta_tags = {}
        for meta in soup.find_all('meta'):
            name = meta.get('name') or meta.get('property')
            content = meta.get('content')
            if name and content:
                meta_tags[name] = content

        # Extraer enlaces
        links = []
        for link in soup.find_all('a', href=True):
            links.append({
                'text': link.get_text(strip=True),
                'href': link['href']
            })

        # Extraer imágenes
        images = []
        for img in soup.find_all('img', src=True):
            images.append({
                'src': img['src'],
                'alt': img.get('alt', '')
            })

        # Extraer texto plano
        text_content = soup.get_text(strip=True)

        # Extraer etiquetas h1-h6
        headings = {}
        for i in range(1, 7):
            tag = f'h{i}'
            elements = soup.find_all(tag)
            if elements:
                headings[tag] = [elem.get_text(strip=True) for elem in elements]

        return ExtractionResult(
            data={
                'title': title,
                'meta_tags': meta_tags,
                'links': links,
                'images': images,
                'text_content': text_content,
                'headings': headings
            },
            metadata={
                'content_length': len(content),
                'extracted_at': '2026-11-14T03:40:00Z'
            }
        )