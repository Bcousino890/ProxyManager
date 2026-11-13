# Investigación: Competencia con Capsolver y 2Captcha

## Resumen Ejecutivo
Capsolver y 2Captcha son líderes en resolución de CAPTCHA con enfoques distintos: Capsolver prioriza IA y integración con agentes de IA (MCP), mientras que 2Captcha ofrece mayor variedad de CAPTCHA y un plan gratuito. Para competir con **crawio.com**, se recomienda: 1) mejorar precios en CAPTCHA v2 (ej. €0.7/k), 2) integrar soluciones para CAPTCHA complejos (Arkose Labs), 3) ofrecer un plan gratuito generoso, y 4) optimizar API para frameworks como Playwright/Selenium.

## Hallazgos

### 1. Precios y modelos de negocio
- **Capsolver**: Precios desde €0.8/k para reCAPTCHA v2 (ej. €0.8/k en plan estándar, €0.4/k para imágenes) [1]. Sin plan gratuito.
- **2Captcha**: Precios desde €0.99/k para reCAPTCHA v2, con **12.000 CAPTCHA gratuitos/min** para Image Captcha [2]. Ofrece planes por uso y paquetes.
- **Conclusión**: Crawio debe ofrecer precios **inferiores** a €0.8/k para reCAPTCHA v2 y un plan gratuito atractivo.

### 2. CAPTCHA soportados y desafíos
- **Capsolver**: Enfocado en IA para resolver reCAPTCHA v2/v3, Cloudflare Turnstile, y Arkose Labs (precio alto: €50/k) [1].
- **2Captcha**: Soporta **25+ CAPTCHA** (incluyendo DataDome, GeeTest, Arkose Labs) [2]. Precios para Arkose Labs: €1.4–50/k.
- **Conclusión**: Crawio debe priorizar soporte para **Arkose Labs** y **DataDome** a precios competitivos.

### 3. Integración y herramientas
- **Capsolver**: Integración con MCP (Agentes de IA), SDKs para Python/Node.js, y enfoque en agentes de IA [1].
- **2Captcha**: Browser API, Scraper API, y herramientas para Selenium/Playwright/Puppeteer [2].
- **Conclusión**: Crawio debe crear **SDKs especializados** para frameworks de scraping (ej. Playwright) y ofrecer integración con MCP.

### 4. Ventajas de los competidores
- **Capsolver**: Velocidad <5s para reCAPTCHA v2 y enfoque en IA [1].
- **2Captcha**: Plan gratuito y mayor variedad de CAPTCHA [2].
- **Conclusión**: Crawio debe **combinar ambas ventajas**: velocidad + plan gratuito + soporte para CAPTCHA complejos.

## Recomendación
1. **Precios**: Ofrecer reCAPTCHA v2 a **€0.7/k** (vs. €0.8/k de Capsolver) y **10.000 CAPTCHA gratis/mes** (vs. 12.000/min de 2Captcha).
2. **CAPTCHA complejos**: Reducir precios para Arkose Labs a **€30/k** (vs. €50/k en 2Captcha).
3. **Integración**: Crear SDKs para **Playwright/Selenium** y documentación clara en GitHub.
4. **Marketing**: Destacar enfoque en **agentes de IA** (como Capsolver) y **web scraping** (como 2Captcha).

## Límites
- No se encontraron datos de precios históricos o comparaciones de éxito en CAPTCHA complejos.
- 2Captcha menciona 99.9% de disponibilidad, pero no hay datos independientes.

## Fuentes
1. [Capsolver Pricing & Features](https://www.capsolver.com/es)
2. [2Captcha API & Pricing](https://2captcha.com/es)
