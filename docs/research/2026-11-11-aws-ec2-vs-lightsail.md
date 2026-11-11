# AWS temporal: EC2 frente a Lightsail — 11 noviembre 2026

Escenario del propietario: crear instancia para pruebas, guardar base de datos y evidencias, eliminarla, repetir cuando haga falta. Se observó consola EC2 abierta en us-east-1 sin instancias en esa región. No se creó ningún recurso.

| Concepto | Lightsail Linux 4 GB + IPv4 | EC2 t3a.medium us-east-1 |
|---|---|---|
| CPU/RAM | 2 vCPU, 4 GB | 2 vCPU, 4 GiB |
| Cómputo | Tarifa por horas con tope de 24 USD/mes, según plan | 0,0376 USD/h, sin tope mensual del paquete |
| Disco | 80 GB SSD incluido | EBS gp3 aparte; referencia 0,08 USD/GB-mes en us-east-1 |
| IPv4 | Incluida mientras está asociada | 0,005 USD/h adicional |
| Transferencia | 4 TB incluidos, varía según región | Se factura según reglas EC2 y destino |
| Al apagar | Sigue facturando hasta eliminar | Cómputo se detiene; EBS e IPv4 pueden seguir facturando |
| Al eliminar | Se pierde disco; snapshots persisten con cargo | Se pierde volumen raíz salvo retención; snapshots persisten con cargo |

Para una prueba corta con recursos equivalentes, Lightsail resulta más sencillo y probablemente más barato. El cómputo y la IPv4 de EC2 t3a.medium suman 0,0426 USD por hora **antes** del disco, snapshots, transferencia e impuestos. Diez horas serían al menos 0,426 USD más esos conceptos. La [lista pública de precios de AWS para España](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonLightsail/current/eu-south-2/index.json) indica 0,03225 USD/h para Lightsail Linux de 4 GB con IPv4 (SKU de `BundleUsage:4GB`, no el plan optimizado de cómputo), con tope de 24 USD/mes. Sin extras, 24 horas cuestan 0,774 USD y 72 horas 2,322 USD antes de impuestos. Un snapshot de 10 GB conservado durante un mes añade 0,50 USD; por tanto, tres sesiones de 24 horas más ese snapshot serían 2,822 USD antes de impuestos, o aproximadamente 3,41 USD si se aplica un IVA del 21 %. El importe en euros dependerá de la conversión de la tarjeta y del tratamiento fiscal de la cuenta.

Guardar solo datos necesarios, preferiblemente exportación cifrada de SQLite, informes y configuración sin secretos en un almacén con coste medido, es más económico que conservar una imagen completa durante pausas largas. Antes de eliminar, verificar que la copia se puede restaurar; borrar snapshots y direcciones IP que ya no se necesiten. Los créditos gratuitos de la cuenta podrían cambiar el coste efectivo y deben comprobarse en Billing.

Fuentes oficiales: [plan Lightsail](https://aws.amazon.com/lightsail/pricing/), [cobro Lightsail al apagar](https://docs.aws.amazon.com/lightsail/latest/userguide/amazon-lightsail-frequently-asked-questions-faq-billing-and-account-management.html), [t3a.medium](https://aws.amazon.com/ec2/instance-types/t3/), [EBS](https://aws.amazon.com/ebs/pricing/), [IPv4](https://aws.amazon.com/vpc/pricing/), [ciclo EC2](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-instance-lifecycle.html).
