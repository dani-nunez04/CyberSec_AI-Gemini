#!/usr/bin/env python3
"""
Script de prueba para Discord Webhook Integration
Permite probar que el webhook funciona correctamente sin ejecutar análisis completos.
"""

import sys
import os
from discord_webhook import discord_webhook

def test_webhook():
    """Prueba el webhook de Discord"""
    
    print("\n" + "="*60)
    print("🔍 TEST DISCORD WEBHOOK - CyberSec AI")
    print("="*60)
    
    if not discord_webhook.enabled:
        print("\n⚠️  WEBHOOK NO CONFIGURADO")
        print("\nPara activar Discord Webhook:")
        print("1. Copia .env.example a .env")
        print("2. Agrega tu URL de webhook Discord")
        print("3. Vuelve a ejecutar este script\n")
        return False
    
    print(f"\n✅ Webhook URL detectado")
    print("\nEnviando mensajes de prueba a Discord...\n")
    
    # Test 1: Log simple
    print("[1/4] Enviando log de info...")
    result1 = discord_webhook.send_log(
        "📝 Este es un log de prueba desde CyberSec AI",
        "info",
        "test-job-001"
    )
    print(f"      {'✅' if result1 else '❌'} Resultado: {result1}\n")
    
    # Test 2: Job start
    print("[2/4] Enviando notificación de inicio...")
    result2 = discord_webhook.send_job_start(
        "test-job-002",
        "192.168.1.100",
        "basic"
    )
    print(f"      {'✅' if result2 else '❌'} Resultado: {result2}\n")
    
    # Test 3: Exploit encontrado
    print("[3/4] Enviando notificación de exploit encontrado...")
    result3 = discord_webhook.send_exploit_found(
        "test-job-003",
        "OpenSSH 7.4",
        "OpenSSH < 8.0 - Authentication Bypass"
    )
    print(f"      {'✅' if result3 else '❌'} Resultado: {result3}\n")
    
    # Test 4: Completación
    print("[4/4] Enviando notificación de completación...")
    result4 = discord_webhook.send_job_complete(
        "test-job-004",
        "192.168.1.100",
        5,  # servicios
        23  # exploits
    )
    print(f"      {'✅' if result4 else '❌'} Resultado: {result4}\n")
    
    # Test 5: Error
    print("[5/5] Enviando notificación de error...")
    result5 = discord_webhook.send_job_error(
        "test-job-005",
        "192.168.1.100",
        "Connection timeout - Target unreachable"
    )
    print(f"      {'✅' if result5 else '❌'} Resultado: {result5}\n")
    
    print("="*60)
    all_success = all([result1, result2, result3, result4, result5])
    if all_success:
        print("\n✅ TODOS LOS TESTS PASARON")
        print("Discord webhook está funcionando correctamente!\n")
    else:
        print("\n⚠️  ALGUNOS TESTS FALLARON")
        print("Verifica tu conexión a internet y que Discord esté accesible\n")
    print("="*60 + "\n")
    
    return all_success

if __name__ == "__main__":
    try:
        success = test_webhook()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Error durante el test: {e}\n")
        sys.exit(1)
