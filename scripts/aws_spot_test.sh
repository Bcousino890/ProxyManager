#!/usr/bin/env bash
# Prueba real de ProxyManager en una instancia EC2 Spot efímera (AWS CloudShell, región eu-south-2).
#
# Cómo usarlo: abre AWS CloudShell con TU sesión de la consola (no necesita claves), región España
# (eu-south-2), y ejecuta:   curl -fsSL https://raw.githubusercontent.com/Bcousino890/ProxyManager/claude/amazing-darwin-rvk1xf/scripts/aws_spot_test.sh -o t.sh && bash t.sh
#
# Qué hace: muestra la cuenta y el precio Spot, pide confirmación, pide el archivo de proxies
# (host:puerto:usuario:contraseña, se pega en la terminal sin eco), crea UNA t3.medium Spot (CPU Standard,
# IMDSv2, sin ninguna regla de entrada) y un security group, ejecuta scripts/live_check.py allí, imprime
# solo resultados y elimina todo (instancia, security group, archivos temporales). Nada de credenciales
# se guarda en el repositorio ni se imprime. Las credenciales de proxies viajan en el user-data de una
# instancia que vive pocos minutos en TU cuenta y se destruye al final.
#
# Variables opcionales: PM_BRANCH, PM_TIMEOUT_MIN (25), PM_REGION (eu-south-2).
set -euo pipefail

REGION="${PM_REGION:-eu-south-2}"
BRANCH="${PM_BRANCH:-claude/amazing-darwin-rvk1xf}"
TIMEOUT_MIN="${PM_TIMEOUT_MIN:-25}"
[[ "$BRANCH" =~ ^[A-Za-z0-9._/-]+$ && "$REGION" =~ ^[a-z0-9-]+$ ]] || { echo "Rama o región inválidas" >&2; exit 1; }
RUN="pm-$(date +%s)"
export AWS_DEFAULT_REGION="$REGION" AWS_PAGER=""
WORK="$(mktemp -d)"; chmod 700 "$WORK"
INSTANCE=""; SG=""

say() { printf '%s\n' "$*"; }
die() { say "ERROR: $*" >&2; exit 1; }

cleanup() {
  trap - EXIT INT TERM
  set +e
  stty echo 2>/dev/null
  say ""; say "== Limpieza =="
  if [[ -n "$INSTANCE" ]]; then
    aws ec2 terminate-instances --instance-ids "$INSTANCE" >/dev/null 2>&1
    aws ec2 wait instance-terminated --instance-ids "$INSTANCE" 2>/dev/null
    say "Instancia $INSTANCE terminada."
  fi
  if [[ -n "$SG" ]]; then
    for _ in 1 2 3 4 5 6; do aws ec2 delete-security-group --group-id "$SG" >/dev/null 2>&1 && break; sleep 10; done
    say "Security group $SG eliminado."
  fi
  command -v shred >/dev/null && find "$WORK" -type f -exec shred -u {} + 2>/dev/null
  rm -rf "$WORK"
  left=$(aws ec2 describe-instances --filters "Name=tag:pm-run,Values=$RUN" "Name=instance-state-name,Values=pending,running,stopping,stopped" --query 'length(Reservations[].Instances[])' --output text 2>/dev/null)
  say "Instancias de esta prueba que siguen vivas: ${left:-desconocido} (debe ser 0)."
}
trap cleanup EXIT INT TERM

command -v aws >/dev/null || die "No se encuentra la CLI de AWS (usa CloudShell)."
say "== Cuenta y región =="
aws sts get-caller-identity --query '[Account,Arn]' --output text || die "Sin sesión de AWS."
aws ec2 describe-availability-zones --query 'AvailabilityZones[0].ZoneName' --output text >/dev/null 2>&1 \
  || die "La región $REGION no está habilitada en tu cuenta (Account → AWS Regions → Enable) o no tienes permisos EC2."

say; say "== Precio Spot t3.medium (Linux) en $REGION =="
read -r AZ PRICE < <(aws ec2 describe-spot-price-history --instance-types t3.medium --product-descriptions "Linux/UNIX" \
  --start-time "$(date -u +%Y-%m-%dT%H:%M:%S)" --query 'SpotPriceHistory[].[AvailabilityZone,SpotPrice]' --output text \
  | awk '!seen[$1]++' | sort -k2 -g | head -1)
[[ -n "${AZ:-}" && -n "${PRICE:-}" ]] || die "No se pudo leer el precio Spot."
MAXP=$(awk -v p="$PRICE" 'BEGIN{printf "%.4f", p*2}')
EST=$(awk -v p="$PRICE" 'BEGIN{printf "%.3f", (p+0.005+0.002)*0.5}')   # ~30 min: Spot + IPv4 + 16 GB gp3
say "Zona más barata: $AZ a $PRICE USD/h (precio máximo que aceptarás: $MAXP USD/h)."
say "Coste estimado para ~30 min con IPv4 y disco de 16 GB: ≈ $EST USD, sin impuestos."
say "Se crea: 1 instancia t3.medium Spot (CPU Standard, sin reglas de entrada) + 1 security group. Se elimina todo al terminar."
read -r -p "¿Crear y ejecutar? Escribe SI para continuar: " OK
[[ "$OK" == "SI" ]] || die "Cancelado; no se creó nada."

read -r -p "URL de destino PROPIA o autorizada [https://zinto.app/robots.txt]: " URL; URL="${URL:-https://zinto.app/robots.txt}"
read -r -p "Texto esperado en la respuesta [User-agent]: " EXPECTED; EXPECTED="${EXPECTED:-User-agent}"
[[ "$URL" =~ ^https://[A-Za-z0-9.-]+(/[^[:space:]\'\"\$\`\\]*)?$ ]] || die "URL no válida (solo https, sin comillas ni espacios)."
[[ "$EXPECTED" =~ ^[A-Za-z0-9\ ._:-]+$ ]] || die "Texto esperado: solo letras, números, espacio y . _ : -"

say; say "Pega ahora el contenido del archivo de proxies (host:puerto:usuario:contraseña, uno por línea)."
say "No se mostrará en pantalla. Termina con Ctrl-D en una línea vacía."
stty -echo 2>/dev/null || true; cat > "$WORK/data.txt"; stty echo 2>/dev/null || true
chmod 600 "$WORK/data.txt"
LINES=$(grep -c . "$WORK/data.txt" || true)
[[ -s "$WORK/data.txt" ]] || die "No se recibió ningún dato."
if grep -Ev '^$|^[^:[:space:]]+:[0-9]{2,5}:[^:]+:.+$' "$WORK/data.txt" >/dev/null; then die "Formato inválido; se esperaba host:puerto:usuario:contraseña por línea."; fi
say "Leídas $LINES conexiones (no se muestran)."

say; say "== Creando recursos =="
AMI=$(aws ssm get-parameter --name /aws/service/canonical/ubuntu/server/24.04/stable/current/amd64/hvm/ebs-gp3/ami-id --query Parameter.Value --output text)
VPC=$(aws ec2 describe-vpcs --filters Name=isDefault,Values=true --query 'Vpcs[0].VpcId' --output text)
[[ "$VPC" != "None" ]] || die "No hay VPC por defecto en $REGION; créala o elige otra región."
SUBNET=$(aws ec2 describe-subnets --filters Name=vpc-id,Values="$VPC" Name=availability-zone,Values="$AZ" Name=default-for-az,Values=true --query 'Subnets[0].SubnetId' --output text)
[[ "$SUBNET" != "None" ]] || die "No hay subred por defecto en $AZ."
SG=$(aws ec2 create-security-group --group-name "$RUN" --description "ProxyManager prueba efimera (sin entrada)" --vpc-id "$VPC" \
  --tag-specifications "ResourceType=security-group,Tags=[{Key=pm-run,Value=$RUN}]" --query GroupId --output text)
say "Security group $SG creado (sin reglas de entrada)."

B64=$(base64 -w0 "$WORK/data.txt")
cat > "$WORK/userdata.sh" <<EOF
#!/bin/bash
# Solo estas líneas con prefijo PM| llegan a la consola; nada con credenciales se imprime.
say() { echo "PM| \$*" > /dev/console; }
say START
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq >/dev/null 2>&1 && apt-get install -y -qq git python3-venv >/dev/null 2>&1 || { say "FALLO instalando paquetes"; shutdown -h now; }
git clone -q --depth 1 -b "$BRANCH" https://github.com/Bcousino890/ProxyManager /opt/pm >/dev/null 2>&1 || { say "FALLO clonando repo"; shutdown -h now; }
cd /opt/pm && python3 -m venv .venv && .venv/bin/pip install -q -e . >/dev/null 2>&1 || { say "FALLO instalando dependencias"; shutdown -h now; }
umask 077
echo '$B64' | base64 -d > /root/data.txt
export PROXYMANAGER_DB_PATH=/root/pm.db
export PROXYMANAGER_CREDENTIAL_KEY=\$(.venv/bin/python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
export PROXYMANAGER_LIVE_URL='$URL' PROXYMANAGER_LIVE_EXPECTED='$EXPECTED'
.venv/bin/python -m proxymanager.importer /root/data.txt --provider aws-test >/dev/null 2>&1 || say "importador: fallo"
say "IP de salida: \$(curl -s --max-time 10 https://checkip.amazonaws.com)"
.venv/bin/python scripts/live_check.py 2>/dev/null | while IFS= read -r l; do say "\$l"; done
shred -u /root/data.txt /root/pm.db 2>/dev/null
say DONE
shutdown -h now
EOF

INSTANCE=$(aws ec2 run-instances --image-id "$AMI" --instance-type t3.medium --subnet-id "$SUBNET" --security-group-ids "$SG" \
  --credit-specification CpuCredits=standard --metadata-options HttpTokens=required,HttpEndpoint=enabled \
  --instance-market-options "MarketType=spot,SpotOptions={MaxPrice=$MAXP,SpotInstanceType=one-time,InstanceInterruptionBehavior=terminate}" \
  --instance-initiated-shutdown-behavior terminate \
  --block-device-mappings 'DeviceName=/dev/sda1,Ebs={VolumeSize=16,VolumeType=gp3,DeleteOnTermination=true}' \
  --user-data "file://$WORK/userdata.sh" \
  --tag-specifications "ResourceType=instance,Tags=[{Key=pm-run,Value=$RUN},{Key=Name,Value=proxymanager-test}]" \
  --query 'Instances[0].InstanceId' --output text)
shred -u "$WORK/userdata.sh" "$WORK/data.txt" 2>/dev/null || rm -f "$WORK/userdata.sh" "$WORK/data.txt"
say "Instancia $INSTANCE lanzada. Esperando resultados (máx. $TIMEOUT_MIN min; la consola de AWS tarda unos minutos en actualizarse)..."

END=$(( $(date +%s) + TIMEOUT_MIN*60 ))
while (( $(date +%s) < END )); do
  sleep 30
  OUT=$(aws ec2 get-console-output --instance-id "$INSTANCE" --latest --query Output --output text 2>/dev/null | grep '^PM|' || true)
  state=$(aws ec2 describe-instances --instance-ids "$INSTANCE" --query 'Reservations[0].Instances[0].State.Name' --output text 2>/dev/null || echo unknown)
  if grep -q 'PM| DONE' <<<"$OUT" || grep -q 'PM| FALLO' <<<"$OUT"; then break; fi
  [[ "$state" == "terminated" || "$state" == "shutting-down" ]] && { say "La instancia terminó (¿interrupción Spot?)."; break; }
done
say; say "== Resultados =="
sed 's/^PM| //' <<<"${OUT:-}"
grep -q 'PM| DONE' <<<"${OUT:-}" || say "(Sin DONE: la prueba no terminó; revisa mensajes anteriores o repite.)"
