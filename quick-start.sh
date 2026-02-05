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
    ollama ls | grep -q "llama3.2:1b" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC} Modelo llama3.2:1b disponible"
    else
        echo -e "${YELLOW}⚠${NC}  Descargando modelo llama3.2:1b (esto puede tomar tiempo)..."
        ollama pull llama3.2:1b
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

# Step 3.5: Close conflicting ports and ensure ollama serve
echo -e "${BLUE}[3.5]${NC} Cerrando puertos conflictivos y arrancando Ollama serve..."
# Lista procesos escuchando TCP y muestra antes de actuar
echo "Procesos escuchando actualmente (puerto PID/PROG):"
ss -ltnp | sed -n '1,200p'

# Definir puertos permitidos que no tocaremos (puedes editar esta lista si necesitas conservar puertos)
ALLOWED_PORTS="22 80 443 11434 8001"

# Función para chequear si un puerto está en la lista permitida
is_allowed_port() {
  p="$1"
  for ap in $ALLOWED_PORTS; do
    if [ "$ap" = "$p" ]; then
      return 0
    fi
  done
  return 1
}

# Cerrar procesos que escuchan en puertos no permitidos (con LIMITADO scope: sólo kill si pertenecen a usuario actual)
ss -ltnp 2>/dev/null | tail -n +2 | while read -r line; do
  port=$(echo "$line" | awk '{print $4}' | sed -E 's/.*:([0-9]+)$/\1/')
  user_part=$(echo "$line" | grep -o "users:(\"[^"]*\",pid=[0-9]+,fd=[0-9]+)" || true)
  pid=$(echo "$user_part" | sed -n 's/.*pid=\([0-9]\+\).*/\1/p')
  if [ -z "$port" ] || [ -z "$pid" ]; then
    continue
  fi
  if is_allowed_port "$port"; then
    echo "Manteniendo puerto permitido $port (PID $pid)"
    continue
  fi
  # Solo matar procesos del usuario actual para evitar impactar servicios del sistema
  proc_user=$(ps -o user= -p "$pid" 2>/dev/null | tr -d ' ')
  my_user=$(whoami)
  if [ -n "$proc_user" ] && [ "$proc_user" = "$my_user" ]; then
    echo "Cerrando proceso PID $pid que escucha en puerto $port"
    kill -9 "$pid" 2>/dev/null || true
  else
    echo "Saltando PID $pid (propietario $proc_user) en puerto $port"
  fi
done < <(ss -ltnp 2>/dev/null | tail -n +2)

# Stop any background ollama serve/runners we started previously (best-effort)
pkill -f "ollama serve" || true
pkill -f "ollama runner" || true
sleep 1

# Start ollama serve in background if not running
if pgrep -f "ollama serve" > /dev/null; then
  echo -e "${GREEN}✓${NC} Ollama serve ya estaba corriendo"
else
  echo -e "Iniciando 'ollama serve' en background..."
  nohup ollama serve > /tmp/ollama_serve.log 2>&1 &
  sleep 2
  echo "Logs: /tmp/ollama_serve.log"
fi

# Mostrar estado de modelos
ollama ls || true

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

# Ejecutar app
python app.py
