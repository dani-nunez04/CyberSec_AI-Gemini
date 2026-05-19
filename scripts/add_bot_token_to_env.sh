#!/usr/bin/env bash
# Script para añadir o borrar DISCORD_BOT_TOKEN y opciones de restricción en .env
# Uso:
#   ./add_bot_token_to_env.sh          # crea/actualiza .env preguntando por valores
#   ./add_bot_token_to_env.sh --delete # elimina DISCORD_BOT_TOKEN de .env (se pide confirmación)

set -euo pipefail

ENV_FILE=".env"

function delete_bot_token() {
  if [ -f "$ENV_FILE" ]; then
    if grep -q "^DISCORD_BOT_TOKEN=" "$ENV_FILE"; then
      read -p "Estás seguro de que quieres BORRAR DISCORD_BOT_TOKEN de $ENV_FILE? (s/n): " CONF
      if [[ "$CONF" == "s" || "$CONF" == "S" ]]; then
        # Elimina la línea que contiene DISCORD_BOT_TOKEN
        sed -i '/^DISCORD_BOT_TOKEN=/d' "$ENV_FILE"
        sed -i '/^ALLOWED_GUILD_IDS=/d' "$ENV_FILE"
        sed -i '/^ALLOWED_CHANNEL_IDS=/d' "$ENV_FILE"
        echo "✅ DISCORD_BOT_TOKEN eliminado de $ENV_FILE"
      else
        echo "Cancelado"
      fi
    else
      echo "No existe DISCORD_BOT_TOKEN en $ENV_FILE"
    fi
  else
    echo "No existe $ENV_FILE"
  fi
}

if [[ ${1:-} == "--delete" ]]; then
  delete_bot_token
  exit 0
fi

echo "Este script te ayuda a añadir DISCORD_BOT_TOKEN y restricciones al archivo $ENV_FILE (no subas $ENV_FILE a Git)."
read -p "Pulsa Enter para continuar..." -r

read -p "Pega tu DISCORD_BOT_TOKEN (deja vacío para cancelar): " BOT_TOKEN
if [ -z "$BOT_TOKEN" ]; then
  echo "Cancelado: no se proporcionó token"
  exit 0
fi

read -p "ALLOWED_GUILD_IDS (IDs separados por comas, deja vacío para permitir todos): " ALLOWED_GUILD_IDS
read -p "ALLOWED_CHANNEL_IDS (IDs separados por comas, deja vacío para permitir todos): " ALLOWED_CHANNEL_IDS

# Crear .env si no existe
if [ ! -f "$ENV_FILE" ]; then
  echo "# .env creado por add_bot_token_to_env.sh" > "$ENV_FILE"
fi

# Poblar/actualizar variables en .env
# Usamos awk para reemplazar o añadir
function upsert_env() {
  local key="$1"
  local val="$2"
  if grep -q "^${key}=" "$ENV_FILE"; then
    sed -i "s#^${key}=.*#${key}=${val}#" "$ENV_FILE"
  else
    echo "${key}=${val}" >> "$ENV_FILE"
  fi
}

upsert_env "DISCORD_BOT_TOKEN" "$BOT_TOKEN"
if [ -n "$ALLOWED_GUILD_IDS" ]; then
  upsert_env "ALLOWED_GUILD_IDS" "$ALLOWED_GUILD_IDS"
fi
if [ -n "$ALLOWED_CHANNEL_IDS" ]; then
  upsert_env "ALLOWED_CHANNEL_IDS" "$ALLOWED_CHANNEL_IDS"
fi

echo "✅ DISCORD_BOT_TOKEN y restricciones añadidas/actualizadas en $ENV_FILE"

echo "Consejo: Regenera el token en Discord Developer Portal si ya lo compartiste públicamente."

exit 0
