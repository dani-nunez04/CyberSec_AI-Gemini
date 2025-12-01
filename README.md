# CyberSec AI - Asistente Inteligente de Pentesting

Un proyecto Python que utiliza **DeepSeek-Coder:1.3b** (vía Ollama) para análisis inteligente de ciberseguridad.

Integra:
- **Nmap**: Escaneo de servicios y puertos
- **Ollama + DeepSeek-Coder**: Análisis inteligente de vulnerabilidades
- **ExploitDB**: Búsqueda de exploits usando FAISS y SentenceTransformers
- **FastAPI**: API REST con interfaz web moderna
- **Reportes**: Generación de reportes en TXT y PDF

## 📋 Requisitos

### Sistema
- **Linux** (Ubuntu 20.04+) o WSL2
- **Python 3.8+**
- **Nmap** instalado
- **Ollama** con modelo `deepseek-coder:1.3b`

### Instalación de dependencias del sistema
```bash
sudo apt update
sudo apt install -y nmap
```

### Instalación de Ollama
1. Descarga desde [ollama.ai](https://ollama.ai)
2. Ejecuta: `ollama pull deepseek-coder:1.3b`
3. Verifica: `ollama list`

## 🚀 Inicio Rápido

### 1. Instalar dependencias Python
```bash
bash install_deps.sh
```

O manualmente:
```bash
pip install fastapi uvicorn faiss-cpu sentence-transformers fpdf pandas numpy -q
```

### 2. Iniciar la API
```bash
python app.py
```

O usar el script (con verificación automática):
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

## 🔧 Estructura del Proyecto

```
├── app.py                      # API FastAPI (principal)
├── asistente_pentest.py        # CLI interactivo
├── exploitdb_search.py         # Búsqueda FAISS de exploits
├── create_exploitdb_index.py   # Generador del índice FAISS
├── templates/
│   ├── index.html              # Interfaz web
│   ├── script.js               # Lógica del frontend
│   └── styles.css              # Estilos
├── exploitdb/                  # Base de datos ExploitDB
├── reports/                    # Reportes generados
└── run.sh                       # Script de inicio
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

### "Ollama no responde"
```bash
# Inicia Ollama si no está corriendo
ollama serve

# En otra terminal
ollama run deepseek-coder:1.3b
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

# API con recarga automática
uvicorn app:app --reload --host 0.0.0.0 --port 8001
```

## 🔐 Notas de Seguridad

- **Uso ético solo**: Este proyecto es para penetration testing autorizado
- **IPs locales**: Prueba primero en `127.0.0.1` o `192.168.x.x` locales
- **Permisos**: Nmap requiere permisos elevados para algunos escaneos
- **Reportes**: Se guardan en `reports/` sin cifrar

## 📚 Tecnologías

- **FastAPI**: Framework web moderno y rápido
- **Ollama**: Motor de IA local
- **FAISS**: Búsqueda vectorial eficiente
- **SentenceTransformers**: Embeddings de texto
- **Nmap**: Escaneo de redes estándar
- **FPDF**: Generación de reportes PDF
