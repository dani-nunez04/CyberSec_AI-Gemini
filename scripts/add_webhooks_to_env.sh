#!/usr/bin/env bash
# Script para crear o borrar el archivo .env con las URLs de Discord
# Uso:
#   ./add_webhooks_to_env.sh          # crea/actualiza .env preguntando por valores
#   ./add_webhooks_to_env.sh --delete # elimina el archivo .env (se pide confirmación)

set -euo pipefail

ENV_FILE=".env"

function delete_env() {
  if [ -f "$ENV_FILE" ]; then
    read -p "Estás seguro de que quieres BORRAR $ENV_FILE? (s/n): " CONF
    if [[ "$CONF" == "s" || "$CONF" == "S" ]]; then
      rm -f "$ENV_FILE"
      echo "✅ $ENV_FILE eliminado"
    else
      echo "Cancelado"
    fi
  else
    echo "No existe $ENV_FILE"
  fi
}

if [[ ${1:-} == "--delete" ]]; then
  delete_env
  exit 0
fi

echo "Este script te ayuda a crear un archivo $ENV_FILE con tus webhooks de Discord (no subas $ENV_FILE a Git)."
echo "Pulsa Enter para continuar..."
read -r

function read_or_prompt() {
  local VAR_NAME="$1"
  local PROMPT="$2"
  local DEFAULT_VALUE="$3"
  local VAL
  read -p "$PROMPT (deja vacío para usar placeholder): " VAL
  if [ -z "$VAL" ]; then
    VAL="$DEFAULT_VALUE"
  fi
  echo "$VAL"
}

LOGS_WEBHOOK=$(read_or_prompt "DISCORD_WEBHOOK_LOGS_ANALISIS" "Webhook para #logs-analisis" "https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_TOKEN")
ERRORS_WEBHOOK=$(read_or_prompt "DISCORD_WEBHOOK_ERRORES" "Webhook para #errores-internos" "https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_TOKEN")
DEV_WEBHOOK=$(read_or_prompt "DISCORD_WEBHOOK_DESARROLLO" "Webhook para #desarrollo" "https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_TOKEN")

cat > "$ENV_FILE" <<EOF
# Discord Webhooks (NO COMMITED)
DISCORD_WEBHOOK_LOGS_ANALISIS=$LOGS_WEBHOOK
DISCORD_WEBHOOK_ERRORES=$ERRORS_WEBHOOK
DISCORD_WEBHOOK_DESARROLLO=$DEV_WEBHOOK
EOF

echo "✅ Archivo $ENV_FILE creado/actualizado. Asegúrate de que $ENV_FILE está en .gitignore"
echo "Puedes borrar este archivo con: ./add_webhooks_to_env.sh --delete"

exit 0
