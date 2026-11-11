# Plan de pruebas AWS por horas — 11 noviembre 2026

Decisión del propietario: usar AWS por horas para las pruebas y comparar VPS mensuales cuando el sistema esté listo. No se ha creado instancia ni autorizado un cargo concreto.

## Opción de partida

Amazon Lightsail Linux, 2 vCPU y 4 GB RAM con IPv4. AWS anuncia 24 USD/mes de máximo para ese plan; la facturación es por horas hasta el máximo mensual. La región, el precio efectivo por hora, impuestos y disponibilidad se verifican en la consola antes de contratar. No usar el plan de 2 GB para validar la capacidad final sin mediciones.

- [Tarifas oficiales Lightsail](https://aws.amazon.com/lightsail/pricing/)
- [Reglas de facturación, apagado y eliminación](https://docs.aws.amazon.com/lightsail/latest/userguide/amazon-lightsail-frequently-asked-questions-faq-billing-and-account-management.html)

Lightsail sigue facturando mientras la instancia existe, aunque esté apagada. Para detener el cargo hay que eliminarla; antes se debe exportar la base de datos y evidencias o hacer snapshot, cuyo almacenamiento puede generar cargos. Una IP estática separada puede facturarse si queda sin instancia. Establecer alarma de presupuesto AWS antes de crear recursos.

## Secuencia

1. Completar y probar localmente los módulos que no requieren VPS.
2. Elegir región europea y confirmar en el checkout plan, precio/hora, IVA, IPv4, transferencia y extras. Solicitar autorización específica de compra.
3. Crear una instancia temporal, desplegar versión restringida, ejecutar pruebas funcionales 100/1000/10000 solo en destinos propios o autorizados y medir CPU, RAM, red, errores y coste.
4. Exportar resultados, revisar facturación y eliminar instancia si hay una pausa larga. Registrar hora de creación y eliminación.
5. Cuando la plataforma esté lista, verificar el precio final y las condiciones vigentes de Netcup VPS Lite 1 G12.5s (4 GB), actualmente el candidato económico para uso continuo. Comparar de nuevo con las alternativas antes de contratar. Véase `2026-11-11-netcup-lite-vs-aws.md`.

AWS EC2 permite detener el cómputo sin pagar instancia mientras está apagada, pero siguen cobrándose almacenamiento EBS y posiblemente IPv4 y otros recursos; la comparación completa se hará si Lightsail no cubre las pruebas. [Ciclo de vida EC2](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-instance-lifecycle.html), [precio IPv4](https://aws.amazon.com/vpc/pricing/).
