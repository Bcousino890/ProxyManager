# AWS temporal: EC2 frente a Lightsail — 11 noviembre 2026

Escenario: servidor Linux x86 de 2 vCPU, 4 GB RAM, IPv4 pública y 80 GB de disco, en **Europa (España), eu-south-2**. Crear, probar, guardar los datos necesarios y eliminar. No se creó ningún recurso. Cifras en USD, sin descuentos ni créditos gratuitos.

| Concepto | Lightsail 4 GB | EC2 t3.medium |
| --- | ---: | ---: |
| Cómputo | 0,03225 USD/h; tope del plan 24 USD/mes | 0,04560 USD/h |
| IPv4 pública | Incluida en el plan | 0,00500 USD/h |
| Disco de 80 GB | Incluido | EBS gp3: 0,088 USD/GB-mes = 7,04 USD/mes |
| CPU sostenida | 20 % de base, con ráfagas | 20 % de base por vCPU; créditos adicionales pueden generar cargos en modo Unlimited |
| Datos transferidos | 4 TB/mes incluidos en España | Tarifas EC2; primeros 100 GB/mes salientes gratuitos a nivel de cuenta, sujetos a condiciones AWS |

El precio de la EC2 **t3a.medium de us-east-1** que se usó en una comparación anterior no corresponde a esta región. La lista pública de precios de AWS para eu-south-2 contiene t3.medium, no t3a.medium. EC2 t4g.medium cuesta 0,03680 USD/h en esta región, pero usa ARM64, por lo que no es una comparación directa con el entorno x86.

Los importes siguientes suponen una sola instancia, el volumen EBS conservado solo durante las horas indicadas, un mes de referencia de 730 horas para prorratear EBS y uso de red dentro de las franquicias. No incluyen snapshots, extras de CPU, otros servicios ni impuestos.

| Tiempo total de pruebas | Lightsail | EC2: máquina + IPv4 + EBS | Diferencia |
| --- | ---: | ---: | ---: |
| 24 h | 0,77 USD | 1,45 USD | 0,67 USD |
| 72 h | 2,32 USD | 4,34 USD | 2,02 USD |
| 120 h | 3,87 USD | 7,23 USD | 3,36 USD |
| 730 h | 23,54 USD | 43,98 USD | 20,44 USD |

Con un **IVA hipotético del 21 %** para una cuenta particular española, 72 horas serían aproximadamente **2,81 USD Lightsail** o **5,25 USD EC2**. Cinco jornadas de 24 horas serían **4,68 USD** o **8,75 USD**. Un snapshot Lightsail de 10 GB conservado un mes suma 0,50 USD antes de IVA. El importe en euros depende del cambio y de la fiscalidad real de la cuenta.

Lightsail sigue facturando incluso apagado hasta borrar la instancia. EC2 detiene el cargo de cómputo al pararla, pero EBS y una IPv4 retenida pueden continuar facturando. Para este plan de pruebas se eliminaría la instancia después de exportar y verificar los datos. Si se decide mantener un entorno apagado entre sesiones, se debe recalcular la comparación.

## Región y precio Spot en vivo

La región no tiene que ser España. En la [tabla oficial de Spot](https://aws.amazon.com/es/ec2/spot/pricing/), consultada el 11 de noviembre de 2026, el **precio más bajo dentro de la región** para Linux era 0,0136 USD/h para EC2 `t3.medium` en España, 0,0210 USD/h para `t3a.medium` en Irlanda y 0,0141 USD/h para `t3a.medium` en Norte de Virginia. El precio depende de zona, capacidad y momento; no es una cotización fija ni garantiza que se pueda lanzar la instancia. El plan Lightsail de 4 GB mantiene 0,03225 USD/h en la lista para España.

Para Spot `t3.medium` en España y el mismo disco de 80 GB, el coste estimado es 0,0136 USD/h de máquina + 0,005 USD/h de IPv4 + 7,04 USD/mes de EBS gp3 prorrateados. Con 730 h/mes como divisor, esto da 0,02824 USD/h en total: 0,68 USD por 24 h, 2,03 USD por 72 h y 3,39 USD por 120 h. Lightsail costaría respectivamente 0,77, 2,32 y 3,87 USD. La diferencia en cinco jornadas de prueba es aproximadamente **0,48 USD antes de impuestos**.

Spot puede ser interrumpido, normalmente con un aviso de dos minutos. La página oficial advierte además que T3 Spot se lanza por defecto en modo Unlimited y que una prueba intensiva de CPU puede generar cargos por créditos; se debe elegir modo Standard si se quiere un coste más previsible. La IPv4, EBS, snapshots y transferencia no están incluidos en la tarifa Spot. Para pruebas descartables y recuperables Spot puede ser ligeramente más barato; para pruebas funcionales continuas y un presupuesto sencillo, se mantiene Lightsail como opción principal. Si cambia la duración, el tráfico o el precio Spot, se recalculará antes de contratar.

**Resultado:** entre EC2 bajo demanda y Lightsail, Lightsail es claramente más barato. EC2 Spot puede costar algo menos bajo las condiciones medidas, con interrupciones y cargos adicionales posibles. Esta comparación no valida el rendimiento exacto del futuro VPS de Netcup ni sustituye el acceso autorizado a DataDome.

Fuentes oficiales: [lista AWS Lightsail eu-south-2](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonLightsail/current/eu-south-2/index.json), [lista AWS EC2 y EBS eu-south-2](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonEC2/current/eu-south-2/index.json), [tabla Spot en vivo](https://aws.amazon.com/es/ec2/spot/pricing/), [interrupciones Spot](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/spot-instance-termination-notices.html), [planes Lightsail](https://docs.aws.amazon.com/lightsail/latest/userguide/amazon-lightsail-bundles.html), [cobro Lightsail y snapshots](https://docs.aws.amazon.com/lightsail/latest/userguide/amazon-lightsail-frequently-asked-questions-faq-billing-and-account-management.html), [CPU Lightsail](https://docs.aws.amazon.com/lightsail/latest/userguide/baseline-cpu-performance.html), [IPv4 EC2](https://aws.amazon.com/vpc/pricing/), [ciclo de vida EC2](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-instance-lifecycle.html), [transferencia EC2](https://aws.amazon.com/ec2/pricing/on-demand/).
