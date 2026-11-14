#!/bin/bash

# Script para ejecutar el servidor de scraping

# Crear directorio de logs si no existe
mkdir -p logs

# Establecer variables de entorno
export SCRAPING_API_KEY="${SCRAPING_API_KEY:?Define SCRAPING_API_KEY en el entorno (nunca en este archivo)}"
export SCRAPING_SERVER_HOST="0.0.0.0"
export SCRAPING_SERVER_PORT="8080"

# Ejecutar el servidor en segundo plano
nohup python server.py > logs/server.log 2>&1 &

echo "Servidor de scraping iniciado en segundo plano (PID: $!)"

# Mostrar los últimos logs
tail -f logs/server.log