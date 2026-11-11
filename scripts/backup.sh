#!/usr/bin/env bash
# Usage: backup.sh DATABASE BACKUP_DIRECTORY [KEEP_DAYS=7]
set -euo pipefail

if [[ $# -lt 2 || $# -gt 3 || ! -f "$1" || ! "${3:-7}" =~ ^[1-9][0-9]*$ ]]; then
  printf 'Uso: backup.sh BASE_SQLITE DIRECTORIO_COPIAS [DIAS_RETENCION>=1]\n' >&2
  exit 2
fi
command -v sqlite3 >/dev/null || { printf 'Falta sqlite3 CLI\n' >&2; exit 2; }

database=$1
backup_dir=$2
keep_days=${3:-7}
umask 077
mkdir -p -- "$backup_dir"
chmod 700 "$backup_dir"
temporary=$(mktemp "$backup_dir/.backup.XXXXXX")
trap 'rm -f -- "$temporary"' EXIT

# The sqlite3 dot command needs its filename quoted; reject characters that
# would break the quoting rather than interpolate an unsafe command.
if [[ "$temporary" == *"'"* || "$temporary" == *$'\n'* ]]; then
  printf 'Ruta de copia no compatible con sqlite3 CLI\n' >&2
  exit 2
fi
sqlite3 "$database" ".backup '$temporary'"
chmod 600 "$temporary"
destination="$backup_dir/proxymanager-$(date -u +%Y%m%dT%H%M%SZ)-$$.sqlite3"
mv -- "$temporary" "$destination"
trap - EXIT

# Only rotate files produced by this script, never unrelated files.
find "$backup_dir" -maxdepth 1 -type f -name 'proxymanager-*.sqlite3' -mtime +"$((keep_days - 1))" -delete
printf '%s\n' "$destination"
