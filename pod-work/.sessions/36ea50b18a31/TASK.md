# Tarea

Para la URL HTTPS pública usa la que da RunPod, no .sslip.io. Así no pierdes tiempo con el agente.

La IP del pod: sale como 80.15.7.37. 80-15-7-37.sslip.io apunta a esa IP, pero solo funciona si RunPod te asigna un puerto TCP público. Además, tener HTTPS ahí exige abrir los puertos 80 y 443, y en RunPod normalmente no se puede.
La opción fiable: https://<POD_ID>-<PUERTO>.proxy.runpod.net. Ya trae HTTPS, y el POD_ID sale en la consola de RunPod. Ahora el agente está buscando en internet cómo hacerlo con sslip.io, y eso es tiempo y dinero perdidos.
