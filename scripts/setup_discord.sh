#!/bin/bash
# Discord Webhook Quick Setup
# Script de configuración rápida para Discord Webhook

echo "================================"
echo "🤖 Discord Webhook - Setup"
echo "================================"
echo ""

# Verificar si .env existe
if [ ! -f ".env" ]; then
    echo "📝 Creando archivo .env..."
    cp .env.example .env
    echo "✅ .env creado desde .env.example"
else
    echo "⚠️  .env ya existe"
fi

echo ""
echo "📋 Para configurar tu webhook de Discord:"
echo ""
echo "1️⃣  Abre Discord y ve a tu servidor"
echo "2️⃣  Click derecho en el servidor → Configuración"
echo "3️⃣  Ve a Integraciones → Webhooks"
echo "4️⃣  Crea un nuevo Webhook"
echo "5️⃣  Copia la URL completa del webhook"
echo ""
echo "6️⃣  Abre el archivo .env:"
echo "    nano .env"
echo ""
echo "7️⃣  Reemplaza:"
echo "    DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR_ID/YOUR_TOKEN"
echo ""
echo "    Con tu URL copiada de Discord"
echo ""
echo "8️⃣  Guarda el archivo (Ctrl+X, Y, Enter en nano)"
echo ""

# Ofrecer editar ahora
read -p "¿Deseas editar el archivo .env ahora? (s/n): " choice
if [[ "$choice" == "s" || "$choice" == "S" ]]; then
    nano .env
fi

echo ""
echo "9️⃣  Ahora prueba tu webhook:"
echo "    python3 test_discord_webhook.py"
echo ""

# Opcional: ejecutar test
read -p "¿Deseas ejecutar el test ahora? (s/n): " choice
if [[ "$choice" == "s" || "$choice" == "S" ]]; then
    python3 test_discord_webhook.py
fi

echo ""
echo "================================"
echo "✅ Setup completo!"
echo "================================"
echo ""
echo "Para más información, revisa:"
echo "  - DISCORD_INTEGRATION.md"
echo "  - DISCORD_WEBHOOK_CHANGES.md"
echo ""
