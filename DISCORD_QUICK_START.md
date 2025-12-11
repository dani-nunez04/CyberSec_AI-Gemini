# 🚀 Quick Start: Discord Webhooks

Configurar Discord Webhooks en 3 minutos:

## Paso 1: Crear el Archivo `.env`

Crea un archivo llamado `.env` en la raíz del proyecto (al lado de `app.py`):

```bash
touch .env
```

## Paso 2: Agregar URLs de Webhooks

Sigue la guía en **SETUP_DISCORD_WEBHOOKS.md** para crear los webhooks en tu servidor Discord.

Una vez tengas las 3 URLs, copia esto en tu `.env`:

```bash
DISCORD_WEBHOOK_LOGS_ANALISIS=https://discord.com/api/webhooks/ID1/TOKEN1
DISCORD_WEBHOOK_ERRORES=https://discord.com/api/webhooks/ID2/TOKEN2
DISCORD_WEBHOOK_DESARROLLO=https://discord.com/api/webhooks/ID3/TOKEN3
```

## Paso 3: Prueba los Webhooks

```bash
python3 test_discord_webhooks.py
```

Deberías ver en Discord:
- 🚀 Inicio de análisis
- 🔍 Logs de búsqueda
- 🎯 Exploits encontrados
- ✨ Análisis completado
- ⚠️ Errores simulados

## Paso 4: Inicia la Aplicación

```bash
python app.py
```

## ✅ Listo

Los logs ahora se enviarán automáticamente a Discord cuando ejecutes análisis.

---

**Documentación Completa:**
- 📖 [DISCORD_INTEGRATION.md](./DISCORD_INTEGRATION.md) - Detalles técnicos
- 📖 [SETUP_DISCORD_WEBHOOKS.md](./SETUP_DISCORD_WEBHOOKS.md) - Guía paso a paso
