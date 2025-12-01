#!/bin/bash
# Script para ejecutar CyberSec AI - Asistente de Pentesting

set -e

echo "================================"
echo "🔐 CyberSec AI - Iniciando API"
echo "================================"
echo ""

# Verificar dependencias básicas
echo "[*] Verificando dependencias..."
python3 check_env.py || true

echo ""
echo "[*] Iniciando FastAPI en http://localhost:8001"
echo "[*] Abre tu navegador en: http://localhost:8001"
echo "[*] Presiona Ctrl+C para detener"
echo ""

# Ejecutar la API
python3 app.py
