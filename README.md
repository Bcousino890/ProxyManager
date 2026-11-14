# ProxyManager

## Descripción

ProxyManager es una plataforma de Web Scraping API que permite extraer contenido de páginas web mediante HTTP o JavaScript (Playwright). Ofrece funcionalidades avanzadas como manejo de proxies, extracción estructurada de datos, y un panel interactivo para pruebas.

## Características

- Extracción HTTP/JavaScript
- Soporte para proxies ISP
- Panel de prueba interactivo (Playground)
- API RESTful con documentación OpenAPI
- Extracción estructurada de datos inmobiliarios
- Gestión de trabajos masivos
- Métricas y estadísticas

## Estructura del Proyecto

```
.
├── README.md
├── pyproject.toml
├── src/
│   └── proxymanager/
│       ├── __init__.py
│       ├── api/
│       │   ├── main.py
│       │   ├── routes/
│       │   │   ├── scrape.py
│       │   │   ├── jobs.py
│       │   │   ├── proxies.py
│       │   │   └── metrics.py
│       ├── scraping/
│       │   ├── fetch.py
│       │   └── property_extractor.py
│       └── utils/
│           └── proxy_manager.py
├── tools/
│   └── scraping-panel/
│       ├── server.py
│       ├── static/
│       │   ├── index.html
│       │   └── style.css
│       └── templates/
└── tests/
    └── fixtures/
```

## Servicios

- API de scraping: `http://127.0.0.1:8000`
- Playground: `http://127.0.0.1:8002`
- Agente Qwen: `http://127.0.0.1:8787`

## Instalación

```bash
# Clonar el repositorio
git clone https://github.com/Bcousino890/ProxyManager.git
cd ProxyManager

# Crear entorno virtual
python -m venv .venv
source .venv/bin/activate

# Instalar dependencias
pip install -e .
```

## Ejecución

```bash
# Iniciar el servidor de scraping
uvicorn src.proxymanager.api.main:app --host 0.0.0.0 --port 8000 --reload

# Iniciar el panel de scraping
cd tools/scraping-panel && python server.py
```

## Pruebas

```bash
# Ejecutar pruebas unitarias
pytest tests/
```

## API Endpoints

- `GET /health` - Verificar estado del servicio
- `POST /scrape` - Iniciar extracción
- `GET /jobs/{id}` - Obtener estado de trabajo
- `GET /proxies/status` - Estado de proxies
- `GET /docs` - Documentación OpenAPI

## Uso del Playground

1. Acceder al panel en `http://127.0.0.1:8002`
2. Ingresar una URL
3. Seleccionar método (HTTP o JavaScript)
4. Hacer clic en "Ejecutar"
5. Ver resultados en las pestañas: Body, Preview, Headers, Text, JSON, Metadata

## Extracción de Datos Inmobiliarios

El sistema incluye un extractor especializado para datos inmobiliarios basado en el HTML de páginas como Idealista. Puede extraer información estructurada como:

- Referencia del anuncio
- Operación (venta/alquiler)
- Título
- Ubicación
- Precio
- Superficie
- Habitaciones
- Baños
- Planta
- Anunciante
- Descripción
- Imágenes

## Seguridad

- Protección SSRF
- Validación de redirecciones
- Límites de recursos
- Timeouts configurables
- Aislamiento de HTML