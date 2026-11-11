# VPS Lite de Netcup frente a AWS — 11 noviembre 2026

Objetivo: minimizar el gasto total de ProxyManager. Esta es una decisión provisional; los precios y requisitos pueden cambiar. No se ha contratado ni creado ningún servidor.

| Uso | Candidato | Precio publicado | Condición principal |
| --- | --- | --- | --- |
| Prueba local | Mac actual | Sin coste de VPS | No valida la red ni el despliegue remoto |
| Prueba remota de pocas horas | AWS Lightsail Linux 4 GB con IPv4 | 24 USD/mes como tope, facturación por horas | Hay que borrar la instancia para detener el cobro; snapshots y otros recursos pueden costar más |
| Servicio continuo | Netcup VPS Lite 1 G12.5s, 4 GB, 80 GB SSD, IPv4/IPv6 | 5,86 €/mes con 19 % IVA alemán | Contrato **mínimo de 6 meses** y facturación semestral: 35,16 € por seis meses al precio publicado |

El precio de Netcup es una equivalencia mensual, no una compra de un solo mes a 5,86 €. Para pruebas de días su compromiso de seis meses hace que Lightsail sea más flexible. Para un servicio que se mantenga seis meses, Netcup es mucho más barato que seis meses de Lightsail 4 GB a precio completo (144 USD), aunque las monedas, impuestos y prestaciones no son idénticos. Netcup ofrece SSD e interfaz de red inferiores a sus VPS normales; hay que medir el desempeño de la aplicación antes de consolidar la elección.

Plan económico: desarrollar y probar localmente; usar Lightsail solo para pruebas remotas breves cuando sean necesarias, con copia de datos antes de eliminar la instancia; contratar Netcup cuando la aplicación esté lista para mantenerse activa. Si durante las pruebas ya se sabe que el servidor va a permanecer seis meses, se puede ir directamente a Netcup. No contratar hasta revisar el importe final, IVA aplicable en España, disponibilidad y plazo de cancelación en el carrito.

Fuentes oficiales: [VPS Lite de Netcup](https://www.netcup.com/en/server/vps-lite), [ficha VPS Lite 1 G12.5s](https://www.netcup.com/en/server/vps/vps-lite-1-g12.5s-iv-6m), [tarifas Lightsail](https://aws.amazon.com/lightsail/pricing/), [facturación Lightsail](https://docs.aws.amazon.com/lightsail/latest/userguide/amazon-lightsail-frequently-asked-questions-faq-billing-and-account-management.html).
