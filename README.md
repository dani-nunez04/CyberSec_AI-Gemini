# CyberSec AI - Asistente Inteligente de Pentesting

Un proyecto Python que utiliza **Gemini API** de Google para análisis inteligente de ciberseguridad.

Integra:
- **Nmap**: Escaneo de servicios y puertos
- **Gemini 2.5**: Análisis inteligente de vulnerabilidades con IA avanzada
- **ExploitDB**: Búsqueda de exploits usando FAISS y SentenceTransformers
- **FastAPI**: API REST con interfaz web moderna
- **Reportes**: Generación de reportes en TXT y PDF
- **Background Jobs**: Procesamiento asincrónico de análisis largos
- **Real Exploit Search**: Búsqueda real de exploits en la base de datos de ExploitDB

## 📋 Requisitos

### Sistema
- **Linux** (Ubuntu 20.04+) o WSL2
- **Python 3.8+**
- **Nmap** instalado

### Requisitos API
- **Gemini API Key** (gratuito en [ai.google.dev](https://ai.google.dev))

### Instalación de dependencias del sistema
```bash
sudo apt update
sudo apt install -y nmap
```

## 🚀 Inicio Rápido

### 1. Obtener Gemini API Key
1. Visita [ai.google.dev](https://ai.google.dev)
2. Haz clic en "Get API Key"
3. Copia tu API key

### 2. Configurar variables de entorno
```bash
cp .env.example .env
# Edita .env y añade:
# GEMINI_API=tu_api_key_aqui
```

### 3. Instalar dependencias Python
```bash
bash install_deps.sh
```

O manualmente:
```bash
pip install -r requirements.txt
```

### 4. Iniciar la API
```bash
python app.py
```
```bash
bash run.sh
```

### 3. Abrir en el navegador
```
http://localhost:8001
```

## 📖 Uso

### Opción 1: Interfaz Web (Recomendada)
1. Abre `http://localhost:8001` en tu navegador
2. Ingresa una IP o dominio
3. Elige tipo de escaneo (básico o profundo)
4. Espera los resultados
5. Descarga el reporte (TXT o PDF)

### Opción 2: CLI Interactivo
```bash
python asistente_pentest.py
```

## 🎯 Características Principales

### Opción A: Background Job Queue (Procesamiento Asincrónico)

El análisis de pentesting ahora se ejecuta **en background** usando un sistema de jobs con ThreadPoolExecutor. Esto evita timeouts y proporciona mejor UX.

**Cómo funciona:**
1. La request `/api/analyze` encoloa el trabajo y retorna inmediatamente con un `job_id`
2. El frontend detecta el `job_id` y comienza a hacer polling
3. Polling cada 500ms a `/api/jobs/{job_id}/logs` para obtener logs en tiempo real
4. Cuando el job termina, se consulta `/api/jobs/{job_id}/result` para obtener los resultados

**Endpoints principales:**
- `POST /api/analyze` - Encoloa un análisis, retorna job_id
- `GET /api/jobs/{job_id}/status` - Obtiene el estado del job (running, completed, error)
- `GET /api/jobs/{job_id}/logs` - Obtiene los logs en tiempo real del job
- `GET /api/jobs/{job_id}/result` - Obtiene el resultado completo (solo si está completed)

**Ventajas:**
- ✅ No hay timeouts en análisis largos (>30 min)
- ✅ UI responsive: muestra logs en tiempo real
- ✅ Escalable: ThreadPool con max_workers=2 (adaptable a más)
- ✅ Compatible con clientes que se reconecten
- ✅ Mejor debugging: cada job tiene sus propios logs

**Ejemplo de uso desde CLI:**
```bash
# 1. Encoloa un análisis
curl -X POST http://localhost:8001/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"target_ip": "192.168.1.1", "scan_type": "basic"}'

# Respuesta:
# {"nmap_output": "[PENDING] Job abc123-... encolado. Use /api/jobs/abc123-.../logs para ver el progreso", ...}

# 2. Monitorea el progreso
curl http://localhost:8001/api/jobs/abc123-.../logs

# 3. Obtén el resultado cuando esté listo
curl http://localhost:8001/api/jobs/abc123-.../result
```

**Implementación técnica:**
- `app.py` usa `concurrent.futures.ThreadPoolExecutor` con max_workers=2
- Cada job tiene un `job_id` (UUID) y se almacena en `job_store` (dict en memoria)
- Los logs se enrutan por job usando `thread_local.current_job`
- La función `perform_analysis()` ejecuta en el worker thread

### Opción D: Real Exploit Search with ExploitDB

La búsqueda de exploits ahora usa **FAISS + SentenceTransformers** para búsqueda real en la base de datos de ExploitDB.

**Cómo funciona:**
1. Se detectan los servicios del output de Nmap (ej: "Apache httpd 2.4.49")
2. Para cada servicio, se busca en el índice FAISS usando embeddings semánticos
3. Se retornan los top 5 exploits más relevantes con descripción y archivo

**Ventajas:**
- ✅ Exploits reales de ExploitDB, no placeholders
- ✅ Búsqueda semántica: entiende variaciones de nombres de servicios
- ✅ Rápido: FAISS vectorial es O(1) (~5ms por servicio)
- ✅ Preciso: SentenceTransformers captura intención semántica
- ✅ Fallback a versión simplificada si FAISS no está disponible

**Ejemplo de resultado:**
```json
{
  "service": "Apache httpd 2.4.49",
  "exploits": [
    {
      "description": "Apache 2.4.49 - RCE via mod_proxy",
      "file": "exploits/unix/remote/50383.py"
    },
    {
      "description": "Apache 2.4 - Path Traversal",
      "file": "exploits/unix/remote/48084.txt"
    }
  ]
}
```

**Implementación técnica:**
- `exploitdb_search.py` proporciona `search_exploits(service_name)` que usa:
  - FAISS index: `exploitdb_index.index` (~69MB)
  - Metadata: `exploitdb_metadata.pkl` (pickled metadata)
  - SentenceTransformer: `all-MiniLM-L6-v2` para embeddings
- `app.py` importa y usa `search_exploits_faiss()` en `get_exploits()`
- Si FAISS falla, fallback a versión simplificada

**Reconstruir índice (si es necesario):**
```bash
python create_exploitdb_index.py
```

## 🔧 Estructura del Proyecto

```
├── app.py                      # API FastAPI (principal) - con job queue y exploit search
├── asistente_pentest.py        # CLI interactivo
├── exploitdb_search.py         # Búsqueda FAISS de exploits
├── create_exploitdb_index.py   # Generador del índice FAISS
├── templates/
│   ├── index.html              # Interfaz web (con polling de jobs)
│   ├── script.js               # Lógica del frontend (job polling)
│   └── styles.css              # Estilos (investigación panel)
├── exploitdb/                  # Base de datos ExploitDB
├── reports/                    # Reportes generados
├── run.sh                       # Script de inicio
└── check_env.py                # Verificador de dependencias
```

## ⚠️ Solución de Problemas

### Error 403 al abrir el navegador
- **Causa**: Servidor estático mal configurado
- **Solución**: Usa `python app.py` (no `python -m http.server`)

### "Error al conectar con la API"
Verifica que:
1. FastAPI esté ejecutándose: `ps aux | grep app.py`
2. Puerto 8001 esté disponible: `lsof -i :8001`
3. CORS esté habilitado (ya lo está en `app.py`)

### "Gemini API Error"
```bash
# Verifica que GEMINI_API esté en .env
grep GEMINI_API .env

# Verifica que sea una API key válida
# Obtén una nueva en: https://ai.google.dev/

# Prueba la conexión
python test_gemini.py
```

### "Nmap no funciona"
```bash
# Verifica instalación
which nmap
nmap --version

# Si falta, instala
sudo apt install -y nmap
```

### "FAISS index no encontrado"
Reconstruye el índice:
```bash
python create_exploitdb_index.py
```

### "Job sigue en running después de mucho tiempo"
1. Verifica el log del servidor: `ps aux | grep app.py`
2. Checa si Nmap está colgado
3. Prueba con un escaneo básico en lugar de profundo
4. Verifica recursos: `free -h` y `top`
5. Verifica conexión a Gemini API: `python test_gemini.py`

## 📝 Comandos Útiles

```bash
# Verificar dependencias
python check_env.py

# Generar índice FAISS
python create_exploitdb_index.py

# Prueba de búsqueda de exploits
python exploitdb_search.py

# Interfaz CLI
python asistente_pentest.py

# API con recarga automática (desarrollo)
uvicorn app:app --reload --host 0.0.0.0 --port 8001

# Ver jobs activos (desde otra terminal)
curl http://localhost:8001/api/logs | jq
```

## 🔐 Notas de Seguridad

- **Uso ético solo**: Este proyecto es para penetration testing autorizado
- **IPs locales**: Prueba primero en `127.0.0.1` o `192.168.x.x` locales
- **Permisos**: Nmap requiere permisos elevados para algunos escaneos
- **Reportes**: Se guardan en `reports/` sin cifrar
- **Jobs**: Se almacenan en memoria; se pierden si el servidor se reinicia

## 📊 Monitoreo de Jobs (Avanzado)

**Ver estado de todos los jobs en memoria:**
```python
# En una sesión Python
import requests
import json

# Obtener logs de la API
response = requests.get('http://localhost:8001/api/logs')
jobs = response.json()
print(json.dumps(jobs, indent=2))
```

**Monitorear un job específico en tiempo real:**
```bash
watch -n 0.5 'curl -s http://localhost:8001/api/jobs/{job_id}/status | jq .'
```

## 📚 Tecnologías

- **FastAPI**: Framework web moderno y rápido
- **Gemini 2.5**: API de IA avanzada (Google)
- **FAISS**: Búsqueda vectorial eficiente (Meta)
- **SentenceTransformers**: Embeddings de texto (Hugging Face)
- **Nmap**: Escaneo de redes estándar
- **FPDF**: Generación de reportes PDF
- **ThreadPoolExecutor**: Procesamiento asincrónico (stdlib)

## 📝 Roadmap Futuro

- [ ] Migrar job queue a Redis + RQ para persistencia
- [ ] Usar SSE/WebSocket en lugar de polling para logs
- [ ] Interfaz de monitoreo de jobs con gráficos
- [ ] Autenticación y control de acceso
- [ ] Caché de resultados de FAISS
- [ ] Exportar reportes a HTML interactivo

