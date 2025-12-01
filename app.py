from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import subprocess
import json
import os
from fpdf import FPDF
import asyncio
import sys
import logging
from collections import deque
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sistema de logs para el frontend
analysis_logs = deque(maxlen=100)  # Guardar últimos 100 logs

def add_log(message: str, log_type: str = "info"):
    """Agregar log que será visible en el frontend"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "message": message,
        "type": log_type  # "info", "searching", "success", "error"
    }
    analysis_logs.append(log_entry)
    logger.info(f"[{log_type.upper()}] {message}")

app = FastAPI()

# Permitir CORS para la interfaz web
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PentestRequest(BaseModel):
    target_ip: str
    scan_type: str = "basic"  # basic, deep, etc

class AnalysisResponse(BaseModel):
    nmap_output: str
    analysis: str
    exploits: list
    services: list

def scan_target(ip: str, scan_type: str = "basic") -> str:
    """Ejecuta escaneo Nmap
    
    Args:
        ip: IP o dominio a escanear
        scan_type: 'basic' o 'deep'
            - basic: Rápido (~30-60s), 1000 puertos comunes, -sV -T4
            - deep: Completo (2-5 min), todos los 65535 puertos, -sV -sC -T3
    """
    try:
        add_log(f"Iniciando escaneo Nmap en {ip}", "searching")
        
        if scan_type == "basic":
            cmd = ["sudo", "nmap", "-sV", "-T4", ip]
            add_log("Tipo: BÁSICO (rápido, 1000 puertos comunes)", "info")
        elif scan_type == "deep":
            cmd = ["sudo", "nmap", "-sV", "-sC", "-T3", ip]
            add_log("Tipo: PROFUNDO (versiones + scripts NSE, todos los puertos)", "info")
        else:
            cmd = ["sudo", "nmap", "-sV", "-T4", ip]
        
        add_log(f"Ejecutando: {' '.join(cmd)}", "searching")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=None)  # Sin timeout
        
        if result.returncode != 0:
            add_log(f"Warning: {result.stderr[:100]}", "info")
        
        add_log(f"Escaneo completado exitosamente", "success")
        return result.stdout if result.stdout else f"[INFO] Nmap finalizó pero sin output estándar.\nSTDERR: {result.stderr}"
        
    except subprocess.TimeoutExpired:
        add_log("Error: Timeout en escaneo Nmap", "error")
        raise HTTPException(status_code=408, detail="Nmap scan timeout - took too long")
    except FileNotFoundError:
        add_log("Error: Nmap no encontrado", "error")
        raise HTTPException(status_code=500, detail="Nmap no está instalado. Instala con: sudo apt install nmap")
    except Exception as e:
        add_log(f"Error Nmap: {str(e)}", "error")
        raise HTTPException(status_code=500, detail=f"Nmap error: {str(e)}")


def analyze_with_ollama(scan_output: str, ip: str) -> str:
    """Analiza el output de Nmap con Ollama"""
    try:
        add_log(f"Iniciando análisis con Ollama para {ip}", "searching")
        
        prompt = f"""Analiza estos resultados de Nmap para {ip}:

{scan_output}

Proporciona:
1. Servicios detectados y sus versiones
2. Vulnerabilidades potenciales
3. Puntos débiles de seguridad
4. Vectores de ataque posibles
5. Recomendaciones de remediación

Sé conciso pero informativo."""

        add_log("Conectando a Ollama (puede tardar)...", "searching")
        
        # Intentar conexión a Ollama con reintentos
        max_retries = 3
        for attempt in range(max_retries):
            try:
                add_log(f"Intento {attempt + 1}/{max_retries}: Ejecutando ollama...", "searching")
                
                process = subprocess.run(
                    ["ollama", "run", "deepseek-coder:1.3b"],
                    input=prompt,
                    text=True,
                    capture_output=True,
                    encoding='utf-8',
                    errors='replace',
                    timeout=None
                )
                
                if process.returncode == 0 and process.stdout.strip():
                    add_log("Análisis completado", "success")
                    return process.stdout.strip()
                elif attempt < max_retries - 1:
                    add_log(f"Reintentando... (intento {attempt + 2}/{max_retries})", "searching")
                    continue
                else:
                    raise Exception("Ollama no retornó resultado válido después de reintentos")
                    
            except Exception as e:
                if attempt < max_retries - 1:
                    add_log(f"Error, reintentando: {str(e)[:50]}", "searching")
                    continue
                else:
                    raise
        
        return process.stdout.strip() if process.stdout.strip() else f"[INFO] Ollama no retornó output.\nSTDERR: {process.stderr}"
        
    except FileNotFoundError:
        add_log("Error: Ollama no encontrado", "error")
        raise HTTPException(status_code=500, detail="Ollama no está instalado. Descárgalo desde ollama.ai")
    except Exception as e:
        add_log(f"Error Ollama: {str(e)}", "error")
        raise HTTPException(status_code=500, detail=f"Ollama error: {str(e)}")

def extract_services(nmap_output: str) -> list:
    """Extrae servicios del output de Nmap"""
    services = []
    for line in nmap_output.splitlines():
        if "/tcp" in line or "/udp" in line:
            parts = line.strip().split()
            if len(parts) >= 3:
                services.append(" ".join(parts[2:]))
    return services

def get_exploits(services: list) -> list:
    """Busca exploits para cada servicio (versión simplificada sin FAISS)"""
    all_exploits = []
    # Versión simplificada: retorna la lista de servicios como exploits potenciales
    for service in services:
        all_exploits.append({
            "service": service,
            "exploits": [f"Buscar exploit para: {service}"]
        })
    return all_exploits

def ensure_report_folder():
    """Asegura que la carpeta de reportes existe"""
    folder = "reports"
    if not os.path.exists(folder):
        os.makedirs(folder)
    return folder

def clean_text(text):
    """Limpia caracteres no ASCII"""
    return ''.join(char if ord(char) < 128 else '?' for char in text)

@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_target(request: PentestRequest):
    """Endpoint principal: recibe IP y realiza análisis completo"""
    
    try:
        # Limpiar logs anteriores
        analysis_logs.clear()
        add_log(f"Iniciando análisis de {request.target_ip} (tipo: {request.scan_type})", "info")
        
        # 1. Escaneo Nmap
        add_log("Paso 1/4: Ejecutando escaneo Nmap...", "searching")
        nmap_output = scan_target(request.target_ip, request.scan_type)
        
        # 2. Extrae servicios
        add_log("Paso 2/4: Extrayendo servicios...", "searching")
        services = extract_services(nmap_output)
        add_log(f"Servicios encontrados: {len(services)}", "success")
        
        # 3. Análisis con IA
        add_log("Paso 3/4: Analizando con IA...", "searching")
        analysis = analyze_with_ollama(nmap_output, request.target_ip)
        
        # 4. Busca exploits
        add_log("Paso 4/4: Buscando exploits...", "searching")
        exploits = get_exploits(services)
        
        add_log("Análisis completado exitosamente", "success")
        
        return AnalysisResponse(
            nmap_output=nmap_output,
            analysis=analysis,
            exploits=exploits,
            services=services
        )
    
    except HTTPException as e:
        add_log(f"Error: {e.detail}", "error")
        raise
    except Exception as e:
        add_log(f"Error inesperado: {str(e)}", "error")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

def extract_services(nmap_output: str) -> list:
    """Extrae servicios del output de Nmap"""
    services = []
    for line in nmap_output.splitlines():
        if "/tcp" in line or "/udp" in line:
            parts = line.strip().split()
            if len(parts) >= 3:
                services.append(" ".join(parts[2:]))
    return services

def get_exploits(services: list) -> list:
    """Busca exploits para cada servicio (versión simplificada sin FAISS)"""
    all_exploits = []
    # Versión simplificada: retorna la lista de servicios como exploits potenciales
    for service in services:
        all_exploits.append({
            "service": service,
            "exploits": [f"Buscar exploit para: {service}"]
        })
    return all_exploits

def ensure_report_folder():
    """Asegura que la carpeta de reportes existe"""
    folder = "reports"
    if not os.path.exists(folder):
        os.makedirs(folder)
    return folder

def clean_text(text):
    """Limpia caracteres no ASCII"""
    return ''.join(char if ord(char) < 128 else '?' for char in text)

@app.post("/api/save-report")
async def save_report(
    target_ip: str,
    nmap_output: str,
    analysis: str,
    exploits: str,  # JSON string
    format: str = "txt"  # txt o pdf
):
    """Guarda el reporte en el formato especificado"""
    try:
        exploits_data = json.loads(exploits)
        ensure_report_folder()
        
        if format == "txt":
            filename = save_as_txt(target_ip, nmap_output, analysis, exploits_data)
        elif format == "pdf":
            filename = save_as_pdf(target_ip, nmap_output, analysis, exploits_data)
        else:
            raise HTTPException(status_code=400, detail="Format must be 'txt' or 'pdf'")
        
        return {"success": True, "filename": filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Save error: {str(e)}")

def save_as_txt(target_ip: str, nmap_output: str, analysis: str, exploits: list) -> str:
    """Guarda reporte en TXT"""
    filename = os.path.join("reports", f"report_{target_ip}.txt")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"=== Análisis de Pentesting: {target_ip} ===\n\n")
        f.write(f"=== Resultado del Escaneo Nmap ===\n\n{nmap_output}\n\n")
        f.write(f"=== Análisis de Vulnerabilidades ===\n\n{analysis}\n\n")
        f.write(f"=== Exploits Sugeridos ===\n\n")
        
        for exploit_group in exploits:
            f.write(f"\n→ Servicio: {exploit_group['service']}\n")
            for exploit in exploit_group.get('exploits', []):
                if isinstance(exploit, dict):
                    f.write(f"  - {exploit.get('description', exploit)} ({exploit.get('file', 'N/A')})\n")
                else:
                    f.write(f"  - {exploit}\n")
    
    return filename

def save_as_pdf(target_ip: str, nmap_output: str, analysis: str, exploits: list) -> str:
    """Guarda reporte en PDF"""
    filename = os.path.join("reports", f"report_{target_ip}.pdf")
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    
    pdf.cell(200, 10, txt=f"Reporte de Pentesting: {target_ip}", ln=True, align="C")
    pdf.ln(10)
    
    pdf.set_font("Helvetica", style="B", size=11)
    pdf.cell(0, 10, txt="=== Resultado del Escaneo Nmap ===", ln=True)
    pdf.set_font("Helvetica", size=9)
    pdf.multi_cell(0, 5, clean_text(nmap_output[:1000]))  # Limita tamaño
    
    pdf.ln(5)
    pdf.set_font("Helvetica", style="B", size=11)
    pdf.cell(0, 10, txt="=== Análisis de Vulnerabilidades ===", ln=True)
    pdf.set_font("Helvetica", size=9)
    pdf.multi_cell(0, 5, clean_text(analysis))
    
    pdf.ln(5)
    pdf.set_font("Helvetica", style="B", size=11)
    pdf.cell(0, 10, txt="=== Exploits Sugeridos ===", ln=True)
    pdf.set_font("Helvetica", size=9)
    
    for exploit_group in exploits:
        pdf.set_font("Helvetica", style="B", size=10)
        pdf.cell(0, 8, txt=f"→ {exploit_group['service']}", ln=True)
        pdf.set_font("Helvetica", size=9)
        for exploit in exploit_group.get('exploits', []):
            if isinstance(exploit, dict):
                text = f"  - {exploit.get('description', exploit)}"
            else:
                text = f"  - {exploit}"
            pdf.multi_cell(0, 5, clean_text(text))
    
    pdf.output(filename)
    return filename

@app.get("/api/status")
async def status():
    """Verifica si la API está activa"""
    return {"status": "active", "message": "CyberSec AI API running"}

@app.get("/api/logs")
async def get_logs():
    """Obtiene los logs actuales de la investigación"""
    return {"logs": list(analysis_logs)}
    return {"status": "active", "message": "CyberSec AI API running"}

# Servir archivos estáticos desde la carpeta templates (DEBE IR AL FINAL)
if os.path.exists("templates"):
    app.mount("/", StaticFiles(directory="templates", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
