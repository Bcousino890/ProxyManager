FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml ./
COPY src ./src
RUN pip install --no-cache-dir .
RUN useradd --create-home --uid 10001 appuser && mkdir /data && chown appuser:appuser /data
ENV PROXYMANAGER_DB_PATH=/data/proxymanager.db
VOLUME ["/data"]
USER appuser
EXPOSE 8000
CMD ["uvicorn", "proxymanager.app:app", "--host", "0.0.0.0", "--port", "8000"]
