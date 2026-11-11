FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml ./
COPY src ./src
RUN pip install --no-cache-dir .
RUN useradd --create-home --uid 10001 appuser && mkdir /data && chown appuser:appuser /data
ENV PROXYMANAGER_DB_PATH=/data/proxymanager.db PYTHONUNBUFFERED=1
VOLUME ["/data"]
USER appuser
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=4).status == 200 else 1)"
# Un solo proceso: la cola, el límite de solicitudes y la carga en vuelo viven en memoria/SQLite de un proceso.
CMD ["uvicorn", "proxymanager.app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--proxy-headers", "--no-server-header"]
