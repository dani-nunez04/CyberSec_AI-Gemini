from fastapi import FastAPI, HTTPException, Request
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
import uuid
import threading
import concurrent.futures
import time
import difflib
import re

# Intentar importar exploitdb_search; si falla, se usará la versión simplificada
try:
    from exploitdb_search import search_exploits as search_exploits_faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

# Importar Discord Webhook
from discord_webhook import discord_webhook

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración por variables de entorno
OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "300"))  # segundos
OLLAMA_MAX_RETRIES = int(os.getenv("OLLAMA_MAX_RETRIES", "3"))

# Sistema de logs para el frontend
analysis_logs = deque(maxlen=100)  # Guardar últimos 100 logs (global)

# Jobs en memoria (simple queue)
job_store = {}

# Thread-local para enrutar logs al job correcto
thread_local = threading.local()

# ThreadPool para ejecutar trabajos en background
executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)


def add_log(message: str, log_type: str = "info"):
    """Agregar log que será visible en el frontend.
    Si el worker actual tiene un job en thread_local, el log va al job; sino va a logs globales.
    """
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "message": message,
        "type": log_type  # "info", "searching", "success", "error"
    }

    job_id = getattr(thread_local, "current_job", None)
    if job_id:
        job = job_store.get(job_id)
        if job:
            job["logs"].append(log_entry)
    else:
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

# Warmup: pre-carga del modelo Ollama al arrancar para evitar latencia en la primera petición
@app.on_event("startup")
async def warm_ollama():
    def _warm():
        try:
            add_log("Warmup: pre-cargando modelo llama3.2:3b-instruct-q5_K_M ", "info")
            # Ejecuta un run corto para mantener el modelo en memoria (keepalive)
            subprocess.run([
                "ollama",
                "run",
                "llama3.2:3b-instruct-q5_K_M",
                "--hidethinking",
                "--keepalive",
                "5m"
            ], input="Warmup", text=True, capture_output=True, timeout=60)
            add_log("Warmup llama3.2:3b-instruct-q5_K_M  completado", "info")
        except Exception as e:
            add_log(f"Warmup Ollama falló: {str(e)}", "error")
    executor.submit(_warm)

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
    """Analiza el output de Nmap con llama3.2:3b-instruct-q5_K_M  (modelo especializado en pentesting)"""
    try:
        add_log(f"Iniciando análisis con llama3.2:3b-instruct-q5_K_M  para {ip}", "searching")
        
        prompt = f"""Eres llama3.2:3b-instruct-q5_K_M , un experto en ciberseguridad ofensiva y pentesting. Analiza los siguientes resultados de un escaneo Nmap para el objetivo {ip}.

## RESULTADOS DEL ESCANEO NMAP:
{scan_output}

## INSTRUCCIONES DE ANÁLISIS:
Proporciona un análisis exhaustivo desde la perspectiva de un pentester profesional:

1. **RESUMEN EJECUTIVO**: Valoración rápida del objetivo - ¿qué tan expuesto está? ¿Es un objetivo fácil o hardened?

2. **SUPERFICIE DE ATAQUE**: 
   - Puertos abiertos y servicios identificados
   - Versiones de software detectadas (si hay versiones vulnerables conocidas, mencionarlas)
   - Fingerprinting del sistema operativo si es posible

3. **VULNERABILIDADES Y CVEs**:
   - Identifica vulnerabilidades conocidas basándote en las versiones de servicios
   - Menciona CVEs específicos si aplican
   - Clasifica por severidad (Crítico, Alto, Medio, Bajo)

4. **VECTORES DE ATAQUE POTENCIALES**:
   - Cómo podría un atacante explotar cada servicio vulnerable
   - Técnicas de explotación aplicables (ej: brute force, exploit público, misconfig)
   - Herramientas que se usarían (metasploit, hydra, etc.)

5. **MISCONFIGURATIONS**:
   - Servicios que no deberían estar expuestos
   - Headers de seguridad faltantes
   - Configuraciones por defecto detectadas

6. **RECOMENDACIONES DE REMEDIACIÓN**:
   - Acciones prioritarias para el administrador
   - Hardening específico por servicio

7. **CONCLUSIÓN**: Nivel de riesgo global (Crítico/Alto/Medio/Bajo) con justificación.

Responde en español, formato texto plano con secciones claras. Sé técnico y específico."""

        add_log("Conectando a Ollama (puede tardar)...", "searching")
        # Quick health check: is the `ollama` process reachable?
        try:
            ls_check = subprocess.run(["ollama", "ls"], capture_output=True, text=True, timeout=4)
            if ls_check.returncode != 0:
                stderr_clean = strip_ansi_sequences(ls_check.stderr)
                diagnosis = diagnose_ollama_error(stderr_clean)
                add_log(f"Ollama unreachable: {stderr_clean[:200]} - {diagnosis}", "error")
                raise HTTPException(status_code=503, detail=f"Ollama not responding: {diagnosis}")
        except FileNotFoundError:
            add_log("Error: Ollama no encontrado", "error")
            raise HTTPException(status_code=500, detail="Ollama no está instalado. Descárgalo desde ollama.ai")
        except subprocess.TimeoutExpired:
            add_log("Ollama ls timeout (servicio provavelmente no disponible)", "error")
            raise HTTPException(status_code=504, detail="Ollama ls timeout - ensure `ollama serve` is running")
        
        # Intentar conexión a Ollama con reintentos (configurable vía env)
        max_retries = int(os.getenv("OLLAMA_MAX_RETRIES", "3"))
        for attempt in range(max_retries):
            try:
                add_log(f"Intento {attempt + 1}/{max_retries}: Ejecutando llama3.2:3b-instruct-q5_K_M ...", "searching")
                
                # Timeout configurable per call (seconds) via OLLAMA_TIMEOUT (default 300s)
                ollama_timeout = int(os.getenv("OLLAMA_TIMEOUT", "600"))
                cmd = ["ollama", "run", "llama3.2:3b-instruct-q5_K_M", "--verbose", "--hidethinking", "--keepalive", "5m"]
                add_log(f"Ejecutando comando: {' '.join(cmd)}", "info")
                start_time = time.time()
                process = subprocess.run(
                    cmd,
                    input=prompt,
                    text=True,
                    capture_output=True,
                    encoding='utf-8',
                    errors='replace',
                    timeout=ollama_timeout
                )
                duration = time.time() - start_time
                add_log(f"Ollama run duró {duration:.1f}s (returncode={process.returncode})", "info")
                
                # Log for debugging - strip ANSI escape sequences to improve readability
                stderr_clean = strip_ansi_sequences(process.stderr)
                stdout_clean = strip_ansi_sequences(process.stdout)
                if process.returncode != 0:
                    # Detect common failure modes in stderr
                    lowered_err = stderr_clean.lower()
                    if "killed" in lowered_err or "oom" in lowered_err or "out of memory" in lowered_err:
                        add_log("Ollama likely killed due to OOM", "error")
                    elif "model not found" in lowered_err or "no such model" in lowered_err or "not found" in lowered_err:
                        add_log("Ollama model not found - pull the model (ollama pull)", "error")
                    elif "connection refused" in lowered_err or "connection error" in lowered_err or "cannot connect" in lowered_err:
                        add_log("Ollama connection error - ensure `ollama serve` is running", "error")
                    diagnosis = diagnose_ollama_error(stderr_clean)
                    add_log(f"Ollama returncode={process.returncode} stderr={stderr_clean[:300]} - {diagnosis}", "error")
                else:
                    add_log("Ollama returned successfully", "info")

                if process.returncode == 0 and process.stdout.strip():
                    add_log("Análisis completado", "success")
                    return process.stdout.strip()
                elif attempt < max_retries - 1:
                    add_log(f"Reintentando... (intento {attempt + 2}/{max_retries})", "searching")
                    continue
                else:
                    stderr_snippet = stderr_clean[:1000] if stderr_clean else ""
                    stdout_snippet = stdout_clean[:1000] if stdout_clean else ""
                    diagnosis = diagnose_ollama_error(stderr_snippet)
                    detail = (
                        f"Ollama returned non-zero (returncode={process.returncode}). "
                        f"Diagnosis: {diagnosis}. STDERR: {stderr_snippet}. STDOUT: {stdout_snippet}"
                    )
                    add_log(detail, "error")
                    # If the error looks like OOM/killed, attempt fallback model if available
                    if "oom" in stderr_snippet.lower() or "killed" in stderr_snippet.lower() or "signal: terminated" in stderr_snippet.lower():
                        fallback = select_fallback_model("llama3.2:3b-instruct-q5_K_M")
                        if fallback and fallback != "llama3.2:3b-instruct-q5_K_M":
                            add_log(f"Intentando fallback con modelo {fallback}", "searching")
                            try:
                                fb_cmd = ["ollama", "run", fallback, "--verbose", "--hidethinking", "--keepalive", "5m"]
                                add_log(f"Ejecutando fallback comando: {' '.join(fb_cmd)}", "info")
                                fb_start = time.time()
                                fb_proc = subprocess.run(
                                    fb_cmd,
                                    input=prompt,
                                    text=True,
                                    capture_output=True,
                                    timeout=120
                                )
                                fb_duration = time.time() - fb_start
                                add_log(f"Fallback run duró {fb_duration:.1f}s (returncode={fb_proc.returncode})", "info")
                                fb_stderr = strip_ansi_sequences(fb_proc.stderr)
                                fb_stdout = strip_ansi_sequences(fb_proc.stdout)
                                if fb_proc.returncode == 0 and fb_stdout.strip():
                                    add_log(f"Fallback con {fallback} exitoso", "success")
                                    return fb_stdout.strip()
                                else:
                                    add_log(f"Fallback con {fallback} también falló. returncode={fb_proc.returncode} stderr={fb_stderr[:300]}", "error")
                            except subprocess.TimeoutExpired:
                                add_log("Timeout en fallback model run", "error")
                            except Exception as e:
                                add_log(f"Fallback error: {str(e)}", "error")
                    raise Exception(detail)
                    
            except subprocess.TimeoutExpired as e:
                add_log("Ollama run timeout", "error")
                if attempt < max_retries - 1:
                    add_log("Reintentando por Timeout...", "searching")
                    continue
                else:
                    raise Exception("Ollama run timeout después de reintentos")
            except Exception as e:
                if attempt < max_retries - 1:
                    add_log(f"Error, reintentando: {str(e)[:50]}", "searching")
                    continue
                else:
                    raise
        
        cleaned_stderr = strip_ansi_sequences(process.stderr)
        return process.stdout.strip() if process.stdout.strip() else f"[INFO] Ollama no retornó output. STDERR: {cleaned_stderr}"
        
    except FileNotFoundError:
        add_log("Error: Ollama no encontrado", "error")
        raise HTTPException(status_code=500, detail="Ollama no está instalado. Descárgalo desde ollama.ai")
    except Exception as e:
        err_str = str(e)
        add_log(f"Error Ollama: {err_str}", "error")
        truncated = err_str[:1000]
        # Detect OOM/killed common patterns
        lowered = truncated.lower()
        if "killed" in lowered or "oom" in lowered or "out of memory" in lowered:
            raise HTTPException(status_code=500, detail=f"Ollama likely OOM/killed: {truncated}")
        raise HTTPException(status_code=500, detail=f"Ollama error: {truncated}")

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
    """Busca exploits para cada servicio usando FAISS si está disponible, sino usa versión simplificada"""
    all_exploits = []
    
    for service in services:
        exploits = []
        
        if FAISS_AVAILABLE:
            try:
                add_log(f"Buscando exploits para: {service}", "searching")
                # Buscar exploits usando FAISS
                faiss_results = search_exploits_faiss(service)
                
                if faiss_results:
                    exploits = faiss_results
                    add_log(f"Encontrados {len(faiss_results)} exploits para {service}", "success")
                else:
                    add_log(f"No se encontraron exploits para: {service}", "info")
                    exploits = [{"description": f"No encontrado en ExploitDB: {service}", "file": "N/A"}]
                    
            except Exception as e:
                add_log(f"Error buscando exploits para {service}: {str(e)[:50]}", "error")
                exploits = [{"description": f"Error en búsqueda: {service}", "file": "N/A"}]
        else:
            # Versión simplificada si FAISS no está disponible
            exploits = [{"description": f"Buscar exploit para: {service}", "file": "ExploitDB"}]
        
        all_exploits.append({
            "service": service,
            "exploits": exploits
        })
    
    return all_exploits

def extract_json_from_text(text: str):
    """Attempt to extract and parse the first JSON object/array found in text."""
    import json
    if not text:
        return None
    # Try a simple regex to find a JSON object or array
    m = re.search(r'(\{.*\}|\[.*\])', text, flags=re.DOTALL)
    if m:
        candidate = m.group(1)
        try:
            return json.loads(candidate)
        except Exception:
            pass
    # Fallback: try to find the first { ... } block
    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end != -1 and end > start:
        candidate = text[start:end+1]
        try:
            return json.loads(candidate)
        except Exception:
            pass
    return None


def find_exploit_refs(query: str, limit: int = 10):
    """Search ExploitDB for query. Uses FAISS if available, otherwise text search as fallback."""
    results = []
    try:
        if FAISS_AVAILABLE:
            try:
                faiss_res = search_exploits_faiss(query)
                if faiss_res:
                    return faiss_res[:limit]
            except Exception:
                pass
        data_file = "exploitdb_data.txt"
        if os.path.exists(data_file):
            with open(data_file, encoding='utf-8', errors='ignore') as f:
                for line in f:
                    if query.lower() in line.lower():
                        results.append(line.strip())
                        if len(results) >= limit:
                            break
    except Exception:
        pass
    return results


def max_confidence(c1: str, c2: str) -> str:
    order = ["low", "medium", "high"]
    try:
        return c2 if order.index(c2) > order.index(c1) else c1
    except Exception:
        return c2 if c2 == "high" else c1


def classify_and_validate_vulnerabilities(parsed_vulns, nmap_output: str, services: list):
    """Validate parsed vulnerabilities against the Nmap output and ExploitDB.

    Returns a list of records with match_type, confidence and evidence.
    """
    validated = []
    for v in parsed_vulns:
        name = (v.get('name') or v.get('title') or v.get('vuln') or "").strip()
        service_claim = (v.get('service') or "").strip()
        description = (v.get('description') or v.get('desc') or v.get('details') or "").strip()
        evidence_line = v.get('evidence_line')
        cve = v.get('cve')
        exploit_ref = (v.get('exploit_reference') or v.get('exploit') or v.get('reference') or "").strip()

        result = {
            "name": name,
            "service_claim": service_claim,
            "description": description,
            "cve": cve,
            "exploit_reference": exploit_ref,
            "match_type": "none",
            "confidence": "low",
            "evidence": None,
            "exploit_matches": [],
            "notes": None,
        }

        # If an evidence_line was supplied by the model, try to find an exact match in Nmap output
        if evidence_line:
            for line in nmap_output.splitlines():
                if evidence_line.strip().lower() in line.lower():
                    result["match_type"] = "exact"
                    result["confidence"] = "high"
                    result["evidence"] = line.strip()
                    break

        # If no evidence_line, check service exact match with detected services
        if result["match_type"] == "none" and service_claim:
            for svc in services:
                if service_claim.lower() in svc.lower() or svc.lower() in service_claim.lower():
                    result["match_type"] = "exact"
                    result["confidence"] = "high"
                    # find an evidence line containing service name
                    for line in nmap_output.splitlines():
                        if svc.split()[0].lower() in line.lower():
                            result["evidence"] = line.strip()
                            break
                    break

        # Fuzzy match across services
        if result["match_type"] == "none" and service_claim and services:
            best_score = 0.0
            best_svc = None
            for svc in services:
                score = difflib.SequenceMatcher(None, service_claim.lower(), svc.lower()).ratio()
                if score > best_score:
                    best_score = score
                    best_svc = svc
            if best_score >= 0.9:
                result["match_type"] = "fuzzy"
                result["confidence"] = "medium"
                for line in nmap_output.splitlines():
                    if best_svc and best_svc.split()[0].lower() in line.lower():
                        result["evidence"] = line.strip()
                        break
            elif best_score >= 0.75:
                result["match_type"] = "possible"
                result["confidence"] = "low"

        # Check exploit references and CVEs against ExploitDB
        if exploit_ref:
            matches = find_exploit_refs(exploit_ref)
            result["exploit_matches"] = matches
            if matches:
                result["confidence"] = max_confidence(result["confidence"], "medium")
                if not result["evidence"]:
                    result["evidence"] = matches[0]

        if cve and not result["evidence"]:
            matches = find_exploit_refs(cve)
            if matches:
                result["exploit_matches"].extend(matches)
                result["confidence"] = max_confidence(result["confidence"], "medium")
                if not result["evidence"]:
                    result["evidence"] = matches[0]

        # If no services detected at all, keep low confidence and add note
        if not services:
            result["notes"] = "No se detectaron servicios; no se puede confirmar esta vulnerabilidad sin evidencia adicional."
            result["confidence"] = "low"

        validated.append(result)
    return validated


def validate_and_classify_analysis(analysis_text: str, nmap_output: str, services: list):
    """Parse AI analysis (prefer JSON) and classify/validate claims."""
    parsed = extract_json_from_text(analysis_text)
    parsed_vulns = []
    if parsed and isinstance(parsed, dict) and parsed.get('vulnerabilities'):
        parsed_vulns = parsed.get('vulnerabilities')
    elif parsed and isinstance(parsed, list):
        parsed_vulns = parsed
    else:
        # Fallback: extract CVEs and lines mentioning vulnerabilities
        cves = list(set(re.findall(r"CVE-\d{4}-\d{4,7}", analysis_text, flags=re.I)))
        for c in cves:
            parsed_vulns.append({"name": c, "description": f"Mentioned CVE {c}", "cve": c})
        if not parsed_vulns:
            # Add first few non-empty lines as claims
            lines = [l.strip() for l in analysis_text.splitlines() if l.strip()]
            for i, line in enumerate(lines[:5]):
                parsed_vulns.append({"name": f"claim_{i+1}", "description": line})

    validated = classify_and_validate_vulnerabilities(parsed_vulns, nmap_output, services)
    return {"vulnerabilities": validated}


def ensure_report_folder():
    """Asegura que la carpeta de reportes existe"""
    folder = "reports"
    if not os.path.exists(folder):
        os.makedirs(folder)
    return folder


def sanitize_filename_component(value: str) -> str:
    """Sanitize a text value to be used safely in a filename."""
    import re
    if value is None:
        return "unknown"
    # keep alnum, dot, underscore, dash
    return re.sub(r"[^A-Za-z0-9._-]", "_", str(value))

def clean_text(text):
    """Limpia caracteres no ASCII"""
    return ''.join(char if ord(char) < 128 else '?' for char in text)


def strip_ansi_sequences(text: str) -> str:
    """Remove ANSI escape sequences and control characters often printed by interactive programs."""
    import re
    if not text:
        return ""
    # ANSI CSI sequences like \x1b[?2026h and spinner chars; strip them
    ansi_escape = re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]")
    cleaned = ansi_escape.sub("", text)
    # Remove other common control codes (carriage returns, backspace, etc.)
    cleaned = re.sub(r"[\x00-\x1F\x7F]+", "", cleaned)
    return cleaned.strip()


@app.get("/api/ollama/debug")
async def ollama_debug():
    """Endpoint simple para diagnosticar Ollama: lista modelos y hace un run corto"""
    try:
        ls = subprocess.run(["ollama", "ls"], capture_output=True, text=True, timeout=5)
        ls_out = strip_ansi_sequences(ls.stdout)
        ls_err = strip_ansi_sequences(ls.stderr)
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Ollama no encontrado")
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="Timeout ejecutando `ollama ls`")

    try:
        # Ejecutar un run corto con timeout limitado
        run_proc = subprocess.run(
            ["ollama", "run", "llama3.2:3b-instruct-q5_K_M", "--verbose", "--hidethinking", "--keepalive", "1m"],
            input="Ping",
            text=True,
            capture_output=True,
            timeout=60
        )
        run_out = strip_ansi_sequences(run_proc.stdout)
        run_err = strip_ansi_sequences(run_proc.stderr)
    except subprocess.TimeoutExpired:
        run_out = ""
        run_err = "Timeout during run"
        run_proc = None
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ejecutando ollama run: {str(e)[:300]}")

    return {
        "ls_returncode": ls.returncode,
        "ls_stdout": ls_out,
        "ls_stderr": ls_err,
        "run_returncode": run_proc.returncode if run_proc is not None else -1,
        "run_stdout": run_out,
        "run_stderr": run_err
    }


def parse_model_size(model_name: str) -> float | None:
    """Parse the size in model name like ':1.3b' -> 1.3. Return None if not found."""
    import re
    match = re.search(r":(\d+(?:\.\d+)?)b$", model_name)
    if match:
        try:
            return float(match.group(1))
        except Exception:
            return None
    return None


def select_fallback_model(preferred_model: str) -> str | None:
    """Return a fallback model name available via `ollama ls` that has a smaller size than preferred_model.
    If no suitable fallback is found, return None.
    """
    try:
        ls_proc = subprocess.run(["ollama", "ls"], capture_output=True, text=True, timeout=3)
        if ls_proc.returncode != 0 or not ls_proc.stdout:
            return None
        models = [line.strip() for line in ls_proc.stdout.splitlines() if line.strip()]
        # Parse preferred size
        pref_size = parse_model_size(preferred_model) or float("inf")
        # Candidates with sizes parsed and smaller than preferred
        candidates = []
        for m in models:
            size = parse_model_size(m)
            if size is not None and size < pref_size:
                candidates.append((size, m))
        if not candidates:
            # If no smaller sized models, choose any model different from preferred
            for m in models:
                if m != preferred_model:
                    return m
            return None
        # Pick the largest model among the smaller ones (closest size < preferred)
        candidates.sort(reverse=True)
        return candidates[0][1]
    except Exception:
        return None


def diagnose_ollama_error(stderr_clean: str) -> str:
    """Return a short diagnosis based on common patterns in Ollama stderr."""
    if not stderr_clean:
        return "Sin detalles proporcionados por Ollama"
    lower = stderr_clean.lower()
    if "killed" in lower or "oom" in lower or "out of memory" in lower or "runner process has terminated" in lower or "signal: terminated" in lower:
        return "Posible OOM - reinicia `ollama serve` o asigna más RAM al modelo"
    if "model not found" in lower or "no such model" in lower or "not found" in lower:
        return "Modelo no encontrado - ejecuta `ollama pull llama3.2:3b-instruct-q5_K_M`"
    if "connection refused" in lower or "cannot connect" in lower or "connection error" in lower or "not responding" in lower or "could not connect" in lower:
        return "Conexión a Ollama fallida - verifica `ollama serve` y puertos"
    if "permission denied" in lower:
        return "Permiso denegado - checa permisos de usuario/ejecución"
    return "Error desconocido - revisa stderr para más detalles"

def perform_analysis(job_id: str, request: PentestRequest):
    """Realiza el análisis completo (ejecutado en background por el executor)"""
    try:
        # Establecer el job_id en thread_local para que add_log enrute correctamente
        thread_local.current_job = job_id
        
        # Limpiar logs anteriores para este job
        job = job_store[job_id]
        job["logs"] = []
        
        # Notificar inicio en Discord
        discord_webhook.send_job_start(job_id, request.target_ip, request.scan_type)
        
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
        analysis_text = analyze_with_ollama(nmap_output, request.target_ip)
        add_log("Validando afirmaciones de la IA...", "searching")
        validated_analysis = validate_and_classify_analysis(analysis_text, nmap_output, services)
        
        # 4. Busca exploits
        add_log("Paso 4/4: Buscando exploits...", "searching")
        exploits = get_exploits(services)
        
        # Contar exploits encontrados
        total_exploits = sum(len(e.get('exploits', [])) for e in exploits)
        
        add_log("Análisis completado exitosamente", "success")
        
        # Notificar completación en Discord
        discord_webhook.send_job_complete(job_id, request.target_ip, len(services), total_exploits)
        
        # Guardar resultado en el job
        job["status"] = "completed"
        job["result"] = {
            "nmap_output": nmap_output,
            "analysis": analysis_text,
            "analysis_validated": validated_analysis,
            "exploits": exploits,
            "services": services
        }
        job["completed_at"] = datetime.now().isoformat()
        
    except HTTPException as e:
        error_msg = str(e.detail)
        add_log(f"Error: {error_msg}", "error")
        discord_webhook.send_job_error(job_id, request.target_ip, error_msg)
        job = job_store.get(job_id)
        if job:
            job["status"] = "error"
            job["error"] = error_msg
            job["completed_at"] = datetime.now().isoformat()
    except Exception as e:
        error_msg = str(e)
        add_log(f"Error inesperado: {error_msg}", "error")
        discord_webhook.send_job_error(job_id, request.target_ip, error_msg)
        job = job_store.get(job_id)
        if job:
            job["status"] = "error"
            job["error"] = error_msg
            job["completed_at"] = datetime.now().isoformat()
    finally:
        # Limpiar thread_local
        thread_local.current_job = None

@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_target(request: PentestRequest):
    """Endpoint principal: encoloa el análisis y retorna el job_id"""
    
    try:
        # Crear un nuevo job
        job_id = str(uuid.uuid4())
        job_store[job_id] = {
            "id": job_id,
            "status": "running",
            "target": request.target_ip,
            "scan_type": request.scan_type,
            "created_at": datetime.now().isoformat(),
            "logs": [],
            "result": None,
            "error": None,
            "completed_at": None
        }
        
        # Encolar el trabajo en el executor
        executor.submit(perform_analysis, job_id, request)
        
        # Retornar el job_id y estado inicial
        # NOTA: FastAPI esperaría AnalysisResponse con todos los campos,
        # pero como es async y el job aún no terminó, retornamos 202 Accepted
        return {
            "nmap_output": f"[PENDING] Job {job_id} encolado. Use /api/jobs/{job_id}/logs para ver el progreso",
            "analysis": "Análisis en progreso...",
            "exploits": [],
            "services": []
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creando job: {str(e)}")

@app.post("/api/save-report")
async def save_report(request: Request):
    """Guarda el reporte en el formato especificado. Espera JSON body.

    JSON body keys: target_ip, nmap_output, analysis, exploits (list o string), format
    Returns: { success: True, filename: basename, download_url }
    """
    try:
        payload = await request.json()
        target_ip = payload.get("target_ip") or "unknown"
        nmap_output = payload.get("nmap_output", "")
        analysis = payload.get("analysis", "")
        format = payload.get("format", "txt")

        exploits_param = payload.get("exploits")
        if isinstance(exploits_param, str):
            try:
                exploits_data = json.loads(exploits_param)
            except Exception:
                exploits_data = []
        elif isinstance(exploits_param, list):
            exploits_data = exploits_param
        else:
            exploits_data = []

        ensure_report_folder()

        if format == "txt":
            filename = save_as_txt(target_ip, nmap_output, analysis, exploits_data)
        elif format == "pdf":
            filename = save_as_pdf(target_ip, nmap_output, analysis, exploits_data)
        else:
            raise HTTPException(status_code=400, detail="Format must be 'txt' or 'pdf'")

        basename = os.path.basename(filename)
        download_url = f"/api/reports/{basename}"
        return {"success": True, "filename": basename, "download_url": download_url}

    except Exception as e:
        logger.exception("Save error")
        raise HTTPException(status_code=500, detail=f"Save error: {str(e)}")

def save_as_txt(target_ip: str, nmap_output: str, analysis: str, exploits: list) -> str:
    """Guarda reporte en TXT"""
    safe_ip = sanitize_filename_component(target_ip)
    filename = os.path.join("reports", f"report_{safe_ip}.txt")
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
    safe_ip = sanitize_filename_component(target_ip)
    filename = os.path.join("reports", f"report_{safe_ip}.pdf")
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
        service_text = clean_text(str(exploit_group.get('service', '')))
        pdf.cell(0, 8, txt=f"- {service_text}", ln=True)
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


@app.get("/api/ollama/health")
async def ollama_health():
    """Check if `ollama` is running and list the available models (quick health check)."""
    try:
        process = subprocess.run(["ollama", "ls"], capture_output=True, text=True, timeout=5)
        if process.returncode == 0:
            return {"status": "ok", "models": process.stdout.strip().splitlines()}
        else:
            diagnostic = diagnose_ollama_error(strip_ansi_sequences(process.stderr)[:500])
            return {"status": "error", "stderr": strip_ansi_sequences(process.stderr)[:500], "returncode": process.returncode, "diagnosis": diagnostic}
    except FileNotFoundError:
        return {"status": "error", "detail": "ollama not found"}
    except subprocess.TimeoutExpired:
        return {"status": "error", "detail": "ollama ls timeout"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


@app.post("/api/ollama/test-run")
async def ollama_test_run(request: Request):
    """Run a quick test Ollama prompt to validate if the model respond correctly.

    Request JSON (optional): {"prompt": "Hello"}
    """
    data = await request.json()
    prompt = data.get("prompt") if isinstance(data, dict) else None
    if not prompt:
        prompt = "Say hello and list numbers 1..3"

    try:
        add_log("Ejecutando prueba rápida de Ollama", "searching")
        process = subprocess.run([
            "ollama",
            "run",
            "llama3.2:1b"
        ], input=prompt, capture_output=True, text=True, timeout=30)

        diagnosis = diagnose_ollama_error(strip_ansi_sequences(process.stderr)[:2000] if process.stderr else "")
        return {
            "returncode": process.returncode,
            "stdout": strip_ansi_sequences(process.stdout)[:2000] if process.stdout else "",
            "stderr": strip_ansi_sequences(process.stderr)[:2000] if process.stderr else "",
            "diagnosis": diagnosis,
        }
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Ollama no encontrado")
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="Ollama test-run timeout")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/jobs/{job_id}/status")
async def get_job_status(job_id: str):
    """Obtiene el estado de un job específico"""
    job = job_store.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    return {
        "id": job["id"],
        "status": job["status"],
        "target": job["target"],
        "scan_type": job["scan_type"],
        "created_at": job["created_at"],
        "completed_at": job["completed_at"],
        "error": job["error"]
    }

@app.get("/api/jobs/{job_id}/logs")
async def get_job_logs(job_id: str):
    """Obtiene los logs de un job específico"""
    job = job_store.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    return {"logs": job["logs"]}

@app.get("/api/jobs/{job_id}/result")
async def get_job_result(job_id: str):
    """Obtiene el resultado completo de un job (solo si está completed)"""
    job = job_store.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    if job["status"] == "running":
        raise HTTPException(status_code=202, detail="Job still running")
    
    if job["status"] == "error":
        raise HTTPException(status_code=500, detail=f"Job error: {job['error']}")
    
    return job.get("result", {})

@app.get("/api/logs")
async def get_logs():
    """Obtiene los logs actuales de la investigación (global, para compatibilidad)"""
    return {"logs": list(analysis_logs)}


@app.get("/api/reports/{filename}")
async def download_report(filename: str):
    """Devuelve un archivo de reporte desde la carpeta `reports` (protegemos path traversal)."""
    # Prevent path traversal
    if ".." in filename or filename.startswith("/") or \
       filename.startswith("\\") or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")

    folder = ensure_report_folder()
    path = os.path.join(folder, filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(path, media_type="application/octet-stream", filename=filename)

# Servir archivos estáticos desde la carpeta templates (DEBE IR AL FINAL)
if os.path.exists("templates"):
    app.mount("/", StaticFiles(directory="templates", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
