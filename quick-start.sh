#!/bin/bash
# Quick Start Guide - CyberSec AI with Options A & D

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     CyberSec AI - Quick Start (Options A & D)                 ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Check environment
echo -e "${BLUE}[1/4]${NC} Verificando dependencias..."
python check_env.py > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Todas las dependencias están instaladas"
else
    echo -e "${YELLOW}⚠${NC}  Instalando dependencias..."
    bash install_deps.sh
fi
echo ""

# Step 2: Check Ollama
echo -e "${BLUE}[2/4]${NC} Verificando Ollama..."
if command -v ollama &> /dev/null; then
    echo -e "${GREEN}✓${NC} Ollama instalado"
    # Check if model exists
    ollama list | grep -q "deepseek-coder" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC} Modelo deepseek-coder disponible"
    else
        echo -e "${YELLOW}⚠${NC}  Descargando modelo deepseek-coder:1.3b (esto puede tomar tiempo)..."
        ollama pull deepseek-coder:1.3b
    fi
else
    echo -e "${YELLOW}⚠${NC}  Ollama no está instalado"
    echo "   Descargalo desde: https://ollama.ai"
    exit 1
fi
echo ""

# Step 3: Check Nmap
echo -e "${BLUE}[3/4]${NC} Verificando Nmap..."
if command -v nmap &> /dev/null; then
    echo -e "${GREEN}✓${NC} Nmap instalado"
else
    echo -e "${YELLOW}⚠${NC}  Instalando Nmap..."
    sudo apt update && sudo apt install -y nmap
fi
echo ""

# Step 4: Start API
echo -e "${BLUE}[4/4]${NC} Iniciando API..."
echo ""
echo -e "${GREEN}✓ API iniciada en http://localhost:8001${NC}"
echo ""
echo "Abre en tu navegador:"
echo "  → http://localhost:8001"
echo ""
echo "Características disponibles:"
echo "  A) Background Job Queue:"
echo "     • Análisis en background (sin timeouts)"
echo "     • Logs en tiempo real"
echo "     • Endpoints: /api/jobs/{job_id}/*"
echo ""
echo "  D) Real Exploit Search:"
echo "     • Búsqueda FAISS en ExploitDB"
echo "     • Exploits reales por servicio"
echo "     • ~5ms por búsqueda"
echo ""
echo "Documentación completa:"
echo "  • README.md - Guía principal"
echo "  • IMPLEMENTATION_SUMMARY.md - Detalles técnicos"
echo "  • CHANGES.md - Cambios realizados"
echo ""

python app.py
