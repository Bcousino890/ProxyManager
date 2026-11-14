# Motor de Scraping

Este proyecto implementa un motor de scraping modular, robusto y portable para ejecutarse en cualquier VPS.

## Características

- Motores HTTP y Playwright
- Gestión de proxies Decodo
- Sesiones autorizadas
- Diagnóstico de protección (DataDome)
- Extractores genéricos e inmobiliarios
- API REST con FastAPI
- Cola de trabajos y persistencia
- Dockerización para portabilidad

## Estructura del Proyecto

```
scraping_engine/
  api/
    main.py
    routes/
    schemas/
    dependencies/
  core/
    config.py
    security.py
    errors.py
    logging.py
  engines/
    base.py
    http_engine.py
    browser_engine.py
  proxies/
    manager.py
    models.py
    health.py
  sessions/
    manager.py
    cookies.py
  diagnostics/
    response_classifier.py
    protection_detector.py
    evidence.py
  extractors/
    base.py
    generic.py
    idealista_html.py
  jobs/
    manager.py
    worker.py
    storage.py
  storage/
    database.py
    models.py
  integrations/
    base.py
    authorized_providers.py
  tests/
    unit/
    integration/
    e2e/
    fixtures/
  scripts/
  docs/
```

## Requisitos

- Python 3.10+
- Docker (para despliegue)
- Chromium (instalado automáticamente en Docker)

## Instalación

```bash
pip install -e .
```

## Ejecución

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

## Pruebas

```bash
pytest tests/
```