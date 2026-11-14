# Instrucciones de Instalación

## Requisitos Previos

- Python 3.11+
- Docker y docker-compose (opcional, para despliegue)
- Acceso a endpoints Decodo (para proxies)

## Instalación Local

### 1. Clonar el Repositorio

```bash
git clone https://github.com/Bcousino890/ProxyManager.git
cd ProxyManager/pod-work/scraping_engine
```

### 2. Crear Entorno Virtual

```bash
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Instalar Chromium (para Playwright)

```bash
playwright install chromium
```

## Configuración

### Variables de Entorno

Crear un archivo `.env` en la raíz del proyecto:

```env
# Proxy Manager
PROXY_MANAGER_URL=http://localhost:8001

# Base de datos
DATABASE_URL=sqlite:///./scraping.db

# API Keys
API_KEY=your_api_key_here

# Proxy Decodo
DECODO_USER=your_decodo_user
DECODO_PASS=your_decodo_pass
```

### Configuración de Proxies

Los endpoints Decodo se configuran en el archivo `src/scraping_engine/proxies/config.py`:

```python
DECODO_ENDPOINTS = [
    "isp.decodo.com:10001",
    "isp.decodo.com:10002",
    # ... más endpoints
]
```

## Ejecución

### Servidor API

```bash
uvicorn scraping_engine.api.main:app --host 0.0.0.0 --port 8000
```

### Pruebas Unitarias

```bash
pytest tests/unit/
```

### Pruebas de Integración

```bash
pytest tests/integration/
```

## Despliegue con Docker

### Construir Imagen

```bash
docker build -t scraping-engine .
```

### Ejecutar Contenedor

```bash
docker run -p 8000:8000 scraping-engine
```

### Usar docker-compose

```bash
docker-compose up -d
```

## Verificación de Funcionamiento

1. Acceder a `/health` para verificar disponibilidad
2. Ejecutar una prueba de scraping simple
3. Verificar que los trabajos se almacenen correctamente