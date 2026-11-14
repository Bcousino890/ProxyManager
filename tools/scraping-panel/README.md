# Panel de Scraping

Panel web para la gestión del scraping con proxies Decodo.

## Características

- Interfaz web para ingresar URLs a scrapear
- Autenticación mediante API Key
- Uso de proxies Decodo para evitar bloqueos
- Manejo de CAPTCHA y desafíos DataDome
- Resultados en tiempo real
- Descarga de resultados

## Requisitos

- Python 3.8+
- Bibliotecas del proyecto ProxyManager

## Instalación

1. Clona el repositorio:
   ```bash
   git clone <url-del-repositorio>
   ```

2. Crea un entorno virtual:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

3. Instala las dependencias:
   ```bash
   pip install -e .
   ```

4. Copia el archivo de ejemplo de configuración:
   ```bash
   cp .env.example .env
   ```

5. Rellena las credenciales en `.env` con tus proxies Decodo.

## Uso

1. Inicia el servidor:
   ```bash
   python server.py
   ```

2. Accede al panel en `http://localhost:8080`

3. Ingresa la URL a scrapear y tu API Key

4. Haz clic en "Iniciar Scraping"

## Endpoints

- `GET /` - Página principal del panel
- `POST /scrape` - Inicia el scraping de una URL
- `GET /health` - Verifica el estado del servidor

## Configuración

El archivo `.env` contiene las siguientes variables:

- `SCRAPING_API_KEY`: Clave API para autenticación
- `SCRAPING_SERVER_HOST`: Dirección del servidor
- `SCRAPING_SERVER_PORT`: Puerto del servidor
- `MAX_CONCURRENT`: Número máximo de scrapings concurrentes
- `SCRAPING_TIMEOUT`: Tiempo de espera en segundos
- `SCRAPING_RETRY_ATTEMPTS`: Número de intentos de reintentar

## Proxy Configuration

El archivo `proxies.txt` contiene las credenciales de los proxies Decodo en el formato:
```
protocol://user:pass@host:port
```

## Seguridad

- El panel requiere autenticación mediante API Key
- Las credenciales de los proxies se almacenan en variables de entorno
- Se implementa manejo de errores para evitar filtración de información sensible

## Licencia

MIT