#!/usr/bin/env python3
"""
Script de prueba para validar la integración con Gemini API
"""

import os
import sys
from dotenv import load_dotenv
import google.generativeai as genai

# Cargar variables de entorno
load_dotenv()

def test_gemini_connection():
    """Prueba la conexión con Gemini API"""
    
    # Obtener API key
    api_key = os.getenv("GEMINI_API")
    if not api_key:
        print("❌ GEMINI_API no está configurada en .env")
        return False
    
    print(f"✓ GEMINI_API encontrada (key: {api_key[:20]}...)")
    
    # Configurar cliente
    try:
        genai.configure(api_key=api_key)
        print("✓ Cliente Gemini configurado")
    except Exception as e:
        print(f"❌ Error configurando cliente Gemini: {e}")
        return False
    
    # Obtener modelo
    model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    print(f"✓ Usando modelo: {model_name}")
    
    # Probar generación de contenido
    try:
        print("\n📝 Enviando prompt de prueba a Gemini...")
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Hola, soy un sistema de pentesting. ¿Puedes decirme en una frase qué es un escaneo Nmap?")
        
        if response and response.text:
            print(f"✓ Respuesta recibida:\n{response.text}")
            print("\n✅ ¡Gemini está funcionando correctamente!")
            return True
        else:
            print("❌ Respuesta vacía de Gemini")
            return False
            
    except Exception as e:
        print(f"❌ Error al comunicarse con Gemini: {e}")
        return False

def test_nmap_output():
    """Prueba análisis de output Nmap simulado"""
    
    print("\n" + "="*60)
    print("Prueba 2: Análisis de escaneo Nmap")
    print("="*60)
    
    api_key = os.getenv("GEMINI_API")
    if not api_key:
        print("❌ GEMINI_API no configurada")
        return False
    
    genai.configure(api_key=api_key)
    model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    
    # Nmap output simulado
    nmap_output = """Starting Nmap 7.93 ( https://nmap.org ) at 2024-01-01 10:00 UTC
Nmap scan report for example.com (93.184.216.34)
Host is up (0.050s latency).
rDNS record for 93.184.216.34: example.com

PORT      STATE SERVICE      VERSION
80/tcp    open  http         Apache httpd 2.4.41 (Ubuntu)
443/tcp   open  https        Apache httpd 2.4.41 (Ubuntu)
22/tcp    open  ssh          OpenSSH 8.2p1 Ubuntu 4ubuntu0.2 (Ubuntu Linux; protocol 2.0)
3306/tcp  open  mysql        MySQL 8.0.23-0ubuntu0.20.04.1
5432/tcp  open  postgresql   PostgreSQL 12.6 on x86_64-pc-linux-gnu

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done at 2024-01-01 10:05 UTC; 1 IP address (1 host up) scanned in 5.23 seconds"""
    
    try:
        print("\n📝 Analizando escaneo Nmap simulado...")
        model = genai.GenerativeModel(model_name)
        
        prompt = f"""Analiza brevemente este escaneo Nmap (máximo 3 párrafos):

{nmap_output}

Proporciona:
1. Servicios encontrados
2. Vulnerabilidades potenciales
3. Riesgos principales"""
        
        response = model.generate_content(prompt, stream=False)
        
        if response and response.text:
            print(f"✓ Análisis completado:\n{response.text[:500]}...\n")
            print("✅ ¡Análisis de escaneo funciona!")
            return True
        else:
            print("❌ Respuesta vacía")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("Test de Integración Gemini API")
    print("="*60)
    
    test1 = test_gemini_connection()
    
    if test1:
        test2 = test_nmap_output()
        if test2:
            sys.exit(0)
    
    sys.exit(1)
