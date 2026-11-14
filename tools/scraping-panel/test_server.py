#!/usr/bin/env python3
"""
Script de prueba para el servidor de scraping.
"""

import requests
import json

def test_health():
    """Prueba el endpoint de salud."""
    try:
        response = requests.get('http://localhost:8080/health')
        print(f"Estado del servidor: {response.status_code}")
        print(f"Respuesta: {response.json()}")
        return True
    except Exception as e:
        print(f"Error en la prueba de salud: {e}")
        return False

def test_scrape():
    """Prueba el endpoint de scraping."""
    try:
        # Usar la clave API correcta que se define en el servidor
        headers = {
            'X-API-Key': 'default_api_key_12345',
            'Content-Type': 'application/json'
        }
        
        data = {
            'url': 'https://httpbin.org/html'
        }
        
        response = requests.post('http://localhost:8080/scrape', 
                               headers=headers, 
                               json=data)
        
        print(f"Estado del scraping: {response.status_code}")
        print(f"Respuesta: {response.json()}")
        return True
    except Exception as e:
        print(f"Error en la prueba de scraping: {e}")
        return False

if __name__ == '__main__':
    print("=== Pruebas del servidor de scraping ===")
    
    print("\n1. Probando endpoint de salud:")
    test_health()
    
    print("\n2. Probando endpoint de scraping:")
    test_scrape()
    
    print("\n=== Fin de pruebas ===")