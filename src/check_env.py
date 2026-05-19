#!/usr/bin/env python3
"""
Verificador de dependencias y requisitos del sistema
"""
import sys
import subprocess
import os

print("\n=== CyberSec AI - Verificador de Dependencias ===\n")

# Verificar Python
print(f"✓ Python: {sys.version.split()[0]}")

# Verificar módulos Python
modules_to_check = [
    'fastapi',
    'uvicorn',
    'faiss',
    'sentence_transformers',
    'fpdf',
    'pandas',
    'numpy',
    'pydantic'
]

print("\nMódulos Python:")
for mod in modules_to_check:
    try:
        __import__(mod)
        print(f"  ✓ {mod}")
    except ImportError:
        print(f"  ✗ {mod} - NO INSTALADO")

# Verificar herramientas del sistema
print("\nHerramientas del Sistema:")
tools_to_check = {
    'nmap': 'nmap --version',
    'ollama': 'ollama --version'
}

for tool_name, cmd in tools_to_check.items():
    try:
        result = subprocess.run(cmd.split(), capture_output=True, timeout=5)
        if result.returncode == 0:
            print(f"  ✓ {tool_name}")
        else:
            print(f"  ✗ {tool_name} - Instalado pero con error")
    except Exception as e:
        print(f"  ✗ {tool_name} - NO ENCONTRADO")

# Verificar archivos necesarios
print("\nArchivos del Proyecto:")
files_to_check = [
    'app.py',
    'templates/index.html',
    'templates/script.js',
    'templates/styles.css',
    'exploitdb/files_exploits.csv'
]

for file in files_to_check:
    if os.path.exists(file):
        print(f"  ✓ {file}")
    else:
        print(f"  ✗ {file} - NO ENCONTRADO")

print("\n=== Verificación Completada ===\n")
