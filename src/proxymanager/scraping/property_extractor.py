import re
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup
from dataclasses import dataclass

@dataclass
class PropertyData:
    source: str
    listing_id: Optional[str] = None
    operation: Optional[str] = None
    property_type: Optional[str] = None
    title: Optional[str] = None
    location: Optional[Dict[str, str]] = None
    price: Optional[Dict[str, Any]] = None
    area_built_m2: Optional[int] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    floor: Optional[int] = None
    exterior: Optional[bool] = None
    elevator: Optional[bool] = None
    advertiser: Optional[str] = None
    description: Optional[str] = None
    images: List[str] = None

def extract_property_data(html_content: str, source: str = "unknown") -> PropertyData:
    """
    Extrae datos estructurados de un anuncio inmobiliario a partir de HTML.
    
    Args:
        html_content (str): HTML del anuncio
        source (str): Fuente original del contenido
        
    Returns:
        PropertyData: Objeto con los datos extraídos
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Inicializar datos
    data = PropertyData(source=source)
    
    # Extraer título
    title_elem = soup.find('h1') or soup.find('title')
    if title_elem:
        data.title = title_elem.get_text(strip=True)
    
    # Extraer referencia (ID)
    ref_elem = soup.find(string=re.compile(r'Referencia.*\d+'))
    if ref_elem:
        match = re.search(r'Referencia:\s*(\d+)', ref_elem)
        if match:
            data.listing_id = match.group(1)
    
    # Extraer operación
    operation_elem = soup.find(string=re.compile(r'Operación.*alquiler|venta', re.IGNORECASE))
    if operation_elem:
        if 'alquiler' in operation_elem.lower():
            data.operation = 'rent'
        elif 'venta' in operation_elem.lower():
            data.operation = 'sale'
    
    # Extraer precio
    price_elem = soup.find(string=re.compile(r'\d+.*€'))
    if price_elem:
        match = re.search(r'(\d+(?:\.\d+)?)\s*€', price_elem)
        if match:
            amount = int(float(match.group(1).replace('.', '')))
            data.price = {
                'amount': amount,
                'currency': 'EUR',
                'period': 'month' if 'mes' in price_elem.lower() else 'total'
            }
    
    # Extraer ubicación
    location_elem = soup.find(string=re.compile(r'Ubicación.*Madrid|Salamanca', re.IGNORECASE))
    if location_elem:
        data.location = {
            'district': location_elem.split(',')[0].replace('Ubicación:', '').strip() if ',' in location_elem else location_elem.replace('Ubicación:', '').strip(),
            'city': 'Madrid'
        }
    
    # Extraer superficie
    area_elem = soup.find(string=re.compile(r'\d+\s*m²'))
    if area_elem:
        match = re.search(r'(\d+)\s*m²', area_elem)
        if match:
            data.area_built_m2 = int(match.group(1))
    
    # Extraer habitaciones
    bedroom_elem = soup.find(string=re.compile(r'\d+\s*habitaciones?'))
    if bedroom_elem:
        match = re.search(r'(\d+)\s*hab', bedroom_elem)
        if match:
            data.bedrooms = int(match.group(1))
    
    # Extraer baños
    bathroom_elem = soup.find(string=re.compile(r'\d+\s*baños?'))
    if bathroom_elem:
        match = re.search(r'(\d+)\s*bañ', bathroom_elem)
        if match:
            data.bathrooms = int(match.group(1))
    
    # Extraer planta
    floor_elem = soup.find(string=re.compile(r'planta.*\d+'))
    if floor_elem:
        match = re.search(r'planta.*?(\d+)', floor_elem, re.IGNORECASE)
        if match:
            data.floor = int(match.group(1))
    
    # Extraer anunciante
    advertiser_elem = soup.find(string=re.compile(r'Anunciante.*'))
    if advertiser_elem:
        data.advertiser = advertiser_elem.replace('Anunciante:', '').strip()
    
    # Extraer descripción
    desc_elem = soup.find(class_='description')
    if desc_elem:
        data.description = desc_elem.get_text(strip=True)
    
    # Extraer imágenes
    images = []
    img_tags = soup.find_all('img')
    for img in img_tags:
        src = img.get('src')
        if src:
            images.append(src)
    data.images = images
    
    return data

# Ejemplo de uso:
if __name__ == "__main__":
    # Cargar el HTML de prueba
    with open('/ProxyManager/tests/fixtures/crawio_idealista_reference.html', 'r') as f:
        html_content = f.read()
    
    # Extraer datos
    result = extract_property_data(html_content, "crawio_reference_fixture")
    print(result)