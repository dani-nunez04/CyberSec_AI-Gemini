#!/usr/bin/env python3
"""
Script de diagnóstico para Gemini API
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

# Cargar variables de entorno
load_dotenv()

def diagnose():
    print("🔍 Diagnóstico de Gemini API\n")
    print("=" * 60)
    
    # 1. Verificar API Key
    api_key = os.getenv("GEMINI_API")
    if not api_key:
        print("❌ GEMINI_API no está configurada en .env")
        return False
    
    # Mostrar solo primeros caracteres
    masked_key = f"{api_key[:10]}...{api_key[-5:]}"
    print(f"✓ API Key encontrada: {masked_key}")
    
    # 2. Configurar cliente
    try:
        genai.configure(api_key=api_key)
        print("✓ Cliente Gemini configurado")
    except Exception as e:
        print(f"❌ Error configurando cliente: {e}")
        return False
    
    # 3. Verificar modelos disponibles
    print("\n📋 Verificando acceso a modelos...")
    try:
        models = list(genai.list_models())
        if models:
            print(f"✓ Acceso a API funcionando ({len(models)} modelos disponibles)")
        else:
            print("❌ No se encontraron modelos")
            return False
    except Exception as e:
        print(f"❌ Error listando modelos: {e}")
        if "403" in str(e):
            print("\n   💡 Solución: El proyecto no tiene acceso a Gemini API")
            print("   1. Ve a: https://console.cloud.google.com/apis/library/generativelanguage.googleapis.com")
            print("   2. Haz clic en 'Enable'")
            print("   3. Espera 2-3 minutos")
            print("   4. Intenta de nuevo")
        return False
    
    # 4. Probar generación de contenido con warmup=False
    print("\n🧪 Probando generación de contenido...")
    try:
        model = genai.GenerativeModel("models/gemini-2.5-flash")
        response = model.generate_content("¿Cuál es el puerto SSH por defecto?", stream=False)
        
        if response and response.text:
            print(f"✓ Respuesta recibida:")
            print(f"   '{response.text[:100]}...'")
            print("\n✅ ¡Gemini API está funcionando correctamente!")
            return True
        else:
            print("❌ Respuesta vacía")
            return False
            
    except Exception as e:
        error_str = str(e)
        print(f"❌ Error: {error_str[:200]}")
        
        if "403" in error_str:
            print("\n   💡 Problema de acceso (403):")
            print("   - La API key es válida pero el proyecto NO tiene permiso")
            print("   - Ve a https://console.cloud.google.com/apis/library/generativelanguage.googleapis.com")
            print("   - Haz clic en 'Enable API'")
            print("   - Espera 2-3 minutos para que se propague")
        
        return False

if __name__ == "__main__":
    success = diagnose()
    exit(0 if success else 1)
