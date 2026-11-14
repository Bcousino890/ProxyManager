FROM python:3.11-slim

# Instalar Chromium para Playwright
RUN apt-get update && apt-get install -y \
    chromium-browser \
    libnss3-dev \
    libatk-bridge2.0-dev \
    libdrm-dev \
    libxcomposite-dev \
    libxdamage-dev \
    libxfixes-dev \
    libxrandr-dev \
    libxss-dev \
    libxtst-dev \
    libasound2 \
    libatk1.0-0 \
    libgtk-3-0 \
    libpango-1.0-0 \
    libcairo2 \
    libglib2.0-0 \
    libx11-xcb1 \
    libxrandr2 \
    libxss1 \
    libxtst6 \
    libgomp1 \
    libgbm1 \
    libxshmfence-dev \
    libgl1-mesa-glx \
    libgl1-mesa-dri \
    && rm -rf /var/lib/apt/lists/*

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar archivos de dependencias
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY . .

# Exponer puertos
EXPOSE 8000

# Comando por defecto
CMD ["uvicorn", "scraping_engine.api.main:app", "--host", "0.0.0.0", "--port", "8000"]