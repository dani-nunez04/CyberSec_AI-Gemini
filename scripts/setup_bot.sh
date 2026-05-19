#!/usr/bin/env bash
# setup_bot.sh
# Script to setup the Discord Cleaner Bot on a new host with minimal overhead.
# Usage:
#   ./setup_bot.sh --install-service   # install systemd unit (requires sudo)
#   ./setup_bot.sh                    # just create a venv and install requirements

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}") >/dev/null 2>&1 && pwd)"
VENV_DIR="${SCRIPT_DIR}/venv"
SERVICE_FILE="/etc/systemd/system/discord_cleaner.service"

function show_help() {
  cat <<'EOF'
Usage: setup_bot.sh [--install-service]

This script:
  - Creates a Python venv at ./venv
  - Installs pip dependencies
  - Copies .env.example if .env is missing
  - Optionally installs a systemd unit and enables the service (requires sudo)

After running, start the bot with: "source venv/bin/activate && python3 discord_cleaner_bot.py"
If you installed the service: "sudo systemctl daemon-reload && sudo systemctl enable --now discord_cleaner.service"
EOF
}

INSTALL_SERVICE=false
for arg in "$@"; do
  case "$arg" in
    -h|--help) show_help; exit 0 ;;
    --install-service) INSTALL_SERVICE=true ;;
    *) echo "Unknown arg: $arg"; show_help; exit 1 ;;
  esac
done

if [ ! -f "${SCRIPT_DIR}/requirements.txt" ]; then
  echo "requirements.txt missing; aborting"
  exit 1
fi

# Create venv
if [ ! -d "$VENV_DIR" ]; then
  echo "Creating venv at $VENV_DIR"
  python3 -m venv "$VENV_DIR"
fi

echo "Activating venv and installing dependencies..."
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"
pip install --upgrade pip
pip install -r "${SCRIPT_DIR}/requirements.txt"

# Copy .env.example if .env not present
if [ ! -f "${SCRIPT_DIR}/.env" ] && [ -f "${SCRIPT_DIR}/.env.example" ]; then
  echo ".env not found, copying .env.example"
  cp "${SCRIPT_DIR}/.env.example" "${SCRIPT_DIR}/.env"
fi

# If requested, install unit file for systemd
if [ "$INSTALL_SERVICE" = true ]; then
  if ! command -v systemctl >/dev/null 2>&1; then
    echo "systemctl not available; cannot install service"
    exit 1
  fi
  if [ "$(id -u)" -ne 0 ]; then
    echo "This step requires sudo, re-run with: sudo ./setup_bot.sh --install-service"
    exit 1
  fi

  # Create service file content
  cat > "$SERVICE_FILE" <<EOF
[Unit]
Description=CyberSec AI Discord Cleaner Bot
After=network.target

[Service]
Type=simple
User=${SUDO_USER:-$(id -un)}
WorkingDirectory=${SCRIPT_DIR}
EnvironmentFile=${SCRIPT_DIR}/.env
ExecStart=${VENV_DIR}/bin/python3 ${SCRIPT_DIR}/discord_cleaner_bot.py
Restart=always
RestartSec=5
Nice=10
# Limit memory and CPU to avoid impacting host: adjust values if needed
MemoryMax=512M
CPUQuota=50%

[Install]
WantedBy=multi-user.target
EOF

  echo "Installed systemd unit at $SERVICE_FILE"
  systemctl daemon-reload
  systemctl enable --now discord_cleaner.service
  echo "Service enabled and started. Check status with: sudo systemctl status discord_cleaner.service"
fi

cat <<EOF
Setup completed.
- To run locally: source venv/bin/activate && python3 discord_cleaner_bot.py
- To run as a service (if installed): sudo systemctl status discord_cleaner.service
EOF
