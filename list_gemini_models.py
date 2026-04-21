#!/usr/bin/env python3
"""
Listar modelos disponibles en Gemini API
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

# Cargar variables de entorno
load_dotenv()

# Obtener API key
api_key = os.getenv("GEMINI_API")
if not api_key:
    print("❌ GEMINI_API no está configurada en .env")
    exit(1)

# Configurar cliente
genai.configure(api_key=api_key)

# Listar modelos disponibles
print("📋 Modelos disponibles en Gemini API:\n")
try:
    for model in genai.list_models():
        print(f"  - {model.name}")
        print(f"    Display: {model.display_name}")
        print(f"    Description: {model.description}")
        print()
except Exception as e:
    print(f"❌ Error: {e}")
