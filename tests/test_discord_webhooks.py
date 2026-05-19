#!/usr/bin/env python3
"""
Script de prueba para Discord Webhooks
Simula lo que sucede cuando se ejecuta un análisis
"""

import sys
from discord_webhook import discord_webhook
from datetime import datetime

def test_discord_webhooks():
    """Prueba los webhooks de Discord (sin enviar si no están configurados)"""
    
    print("\n" + "="*60)
    print("🧪 PRUEBA DE DISCORD WEBHOOKS")
    print("="*60 + "\n")
    
    # Mostrar estado actual
    print("📊 Estado Actual de Webhooks:")
    print(f"  ✅ LOGS_ANALISIS: {'CONFIGURADO' if discord_webhook.webhook_logs else '❌ NO CONFIGURADO'}")
    print(f"  ✅ ERRORES: {'CONFIGURADO' if discord_webhook.webhook_errors else '❌ NO CONFIGURADO'}")
    print(f"  ✅ DESARROLLO: {'CONFIGURADO' if discord_webhook.webhook_dev else '❌ NO CONFIGURADO'}\n")
    
    # Si no hay webhooks configurados
    if not any([discord_webhook.webhook_logs, discord_webhook.webhook_errors, discord_webhook.webhook_dev]):
        print("⚠️  ADVERTENCIA: No hay webhooks configurados")
        print("    Por favor, sigue estos pasos:\n")
        print("    1. Lee: SETUP_DISCORD_WEBHOOKS.md")
        print("    2. Crea los webhooks en Discord")
        print("    3. Copia la URLs en un archivo .env")
        print("    4. Ejecuta este script nuevamente\n")
        print("    Ejemplo .env:")
        print("    DISCORD_WEBHOOK_LOGS_ANALISIS=https://discord.com/api/webhooks/...")
        print("    DISCORD_WEBHOOK_ERRORES=https://discord.com/api/webhooks/...")
        print("    DISCORD_WEBHOOK_DESARROLLO=https://discord.com/api/webhooks/...\n")
        return
    
    print("✅ Webhooks detectados. Continuando con simulación...\n")
    
    # Simular eventos
    job_id = "test-job-123"
    target_ip = "192.168.1.100"
    
    print("📤 Simulando eventos (intenta enviarlos a Discord):\n")
    
    # 1. Inicio
    print("1️⃣  Inicio de análisis...")
    result = discord_webhook.send_job_start(job_id, target_ip, "basic")
    print(f"   {'✅ Enviado' if result else '❌ Error'}\n")
    
    # 2. Log de búsqueda
    print("2️⃣  Log de búsqueda...")
    result = discord_webhook.send_log(
        "Buscando servicios en puerto 22, 80, 443...",
        "searching",
        job_id
    )
    print(f"   {'✅ Enviado' if result else '❌ Error'}\n")
    
    # 3. Exploit encontrado
    print("3️⃣  Exploit encontrado...")
    result = discord_webhook.send_exploit_found(
        job_id,
        "OpenSSH 7.4",
        "OpenSSH < 6.6 Command Execution"
    )
    print(f"   {'✅ Enviado' if result else '❌ Error'}\n")
    
    # 4. Completación
    print("4️⃣  Análisis completado...")
    result = discord_webhook.send_job_complete(job_id, target_ip, 3, 5)
    print(f"   {'✅ Enviado' if result else '❌ Error'}\n")
    
    # 5. Error (opcional)
    print("5️⃣  Error de ejemplo...")
    result = discord_webhook.send_job_error(job_id, target_ip, "Connection timeout")
    print(f"   {'✅ Enviado' if result else '❌ Error'}\n")
    
    # 6. Log de desarrollo
    print("6️⃣  Log de desarrollo...")
    result = discord_webhook.send_dev_log("Sistema iniciado correctamente", "info")
    print(f"   {'✅ Enviado' if result else '❌ Error'}\n")
    
    print("="*60)
    print("✅ PRUEBA COMPLETADA")
    print("="*60)
    print("\n💡 Consejo: Verifica tu servidor Discord para ver los mensajes\n")

if __name__ == "__main__":
    test_discord_webhooks()
