#!/usr/bin/env python3
"""
Discord Cleaner Bot
Bot que añade un comando /clear para limpiar mensajes del canal.

Requisitos:
- Python 3.8+
- py-cord (pip install py-cord)
- Token de bot en variable DISCORD_BOT_TOKEN en .env

Uso:
- Ejecuta `python3 discord_cleaner_bot.py` luego añade el bot al servidor con los scopes `bot` y `applications.commands` y permisos `Manage Messages`.
- Comando slash: `/clear amount:100` (borrar hasta 100 mensajes por defecto)
- Comando de texto alternativo: `!clear 50`

Seguridad:
- Solo usuarios con permisos de 'manage_messages' pueden ejecutar el comando.
- Evita borrar mensajes con fecha mayor a 14 días (restricción de la API de Discord para bulk delete). El bot hace `purge()` y se maneja el límite.
"""

import os
import logging
import asyncio

import discord
from discord.ext import commands
from dotenv import load_dotenv

# Cargar .env si existe
try:
    load_dotenv()
except Exception:
    pass

LOG_LEVEL = os.getenv("DISCORD_BOT_LOG_LEVEL", "INFO")
logging.basicConfig(level=getattr(logging, LOG_LEVEL))
logger = logging.getLogger(__name__)

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
if not TOKEN:
    logger.warning("DISCORD_BOT_TOKEN no configurado. Revisa tu .env o .env.example")

# Intents: necesitamos message_content si queremos comandos por texto (no estrictamente para slash).
intents = discord.Intents.default()
intents.messages = True
# Message Content es un privileged intent: solo activar con consentimiento via env var
ENABLE_MESSAGE_CONTENT = os.getenv("DISCORD_INTENT_MESSAGE_CONTENT", "false").lower() in ("1", "true", "yes")
intents.message_content = ENABLE_MESSAGE_CONTENT
if ENABLE_MESSAGE_CONTENT:
    logger.info("Privileged intent 'message_content' habilitado desde variable de entorno")
else:
    logger.info("Privileged intent 'message_content' DESHABILITADO (usar slash commands o habilitar DISCORD_INTENT_MESSAGE_CONTENT=true si requerir) ")

bot = commands.Bot(command_prefix='!', intents=intents)

# Cargar variables opcionales de seguridad
ALLOWED_GUILD_IDS = os.getenv("ALLOWED_GUILD_IDS", "")
ALLOWED_CHANNEL_IDS = os.getenv("ALLOWED_CHANNEL_IDS", "")

def _parse_ids(ids_str: str):
    if not ids_str:
        return None
    try:
        ids = [int(x.strip()) for x in ids_str.split(',') if x.strip()]
        return set(ids)
    except ValueError:
        logger.warning("ALLOWED_GUILD_IDS/ALLOWED_CHANNEL_IDS contiene un valor no numérico")
        return None

ALLOWED_GUILD_IDS_SET = _parse_ids(ALLOWED_GUILD_IDS)
ALLOWED_CHANNEL_IDS_SET = _parse_ids(ALLOWED_CHANNEL_IDS)

def _is_allowed_guild_channel(guild_id: int, channel_id: int) -> bool:
    if ALLOWED_GUILD_IDS_SET and guild_id not in ALLOWED_GUILD_IDS_SET:
        return False
    if ALLOWED_CHANNEL_IDS_SET and channel_id not in ALLOWED_CHANNEL_IDS_SET:
        return False
    return True

# Helper: comprobación de permisos
def can_manage_messages(ctx):
    return ctx.author.guild_permissions.manage_messages

# Comando de texto alternativo (opcional)
@bot.command(name='clear')
@commands.has_guild_permissions(manage_messages=True)
async def clear_cmd(ctx, amount: int = 100, only_webhooks: bool = False, dry_run: bool = False):
    """Limpiar mensajes en el canal (comando de texto: !clear 50 --only-webhooks --dry-run)

    - amount: máximo de mensajes a procesar (no necesariamente eliminados si 'only_webhooks' está activo)
    - only_webhooks: si True, eliminar solo los mensajes cuyo atributo webhook_id no sea None
    - dry_run: si True, no se eliminan mensajes; se reporta cuántos coincidieron
    """
    if amount < 1:
        await ctx.send("El número de mensajes debe ser mayor a 0", delete_after=5)
        return

    # Comprobar que el comando se ejecuta en un guild/channel permitidos
    if ctx.guild and not _is_allowed_guild_channel(ctx.guild.id, ctx.channel.id):
        await ctx.send("Este bot no está autorizado para ejecutar comandos en este servidor/canal.", delete_after=8)
        return

    if dry_run:
        # Contar coincidencias sin eliminar
        matched = 0
        async for m in ctx.channel.history(limit=amount):
            if only_webhooks and m.webhook_id is None:
                continue
            matched += 1
        await ctx.send(f"🔎 Dry-run: {matched} mensajes coinciden y serían eliminados.", delete_after=10)
        return

    # Real delete
    if only_webhooks:
        deleted = await ctx.channel.purge(limit=amount, check=lambda m: m.webhook_id is not None)
    else:
        deleted = await ctx.channel.purge(limit=amount)

    await ctx.send(f"✅ He eliminado {len(deleted)} mensajes.", delete_after=5)

    # Log a webhook de desarrollo si está configurado
    try:
        from discord_webhook import discord_webhook as _logger
        _logger.send_dev_log(f"Bot: eliminado {len(deleted)} mensajes en #{ctx.channel.name} (id:{ctx.channel.id}) por {ctx.author.name}")
    except Exception:
        pass

# Slash command using app_commands (Discord v2)
@bot.tree.command(name='clear', description='Eliminar mensajes del canal (requiere Manage Messages)')
async def clear(interaction: discord.Interaction, amount: int = 100, only_webhooks: bool = False, dry_run: bool = False):
    """Slash command to clear messages.

    - amount: maximum number of messages to scan
    - only_webhooks: delete only messages created by webhooks
    - dry_run: just count matches, don't delete them
    """
    # Permisos
    if not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message("No tienes permisos para ejecutar este comando.", ephemeral=True)
        return

    if interaction.guild and not _is_allowed_guild_channel(interaction.guild.id, interaction.channel.id):
        await interaction.response.send_message("Este bot no está autorizado para ejecutar comandos en este servidor/canal.", ephemeral=True)
        return

    if amount < 1:
        await interaction.response.send_message("El número de mensajes debe ser mayor a 0", ephemeral=True)
        return

    # Responder inmediatamente para evitar bloqueo
    await interaction.response.defer(ephemeral=True)

    try:
        if dry_run:
            matched = 0
            async for m in interaction.channel.history(limit=amount):
                if only_webhooks and m.webhook_id is None:
                    continue
                matched += 1
            await interaction.followup.send(f"🔎 Dry-run: {matched} mensajes coinciden y serían eliminados.", ephemeral=True)
            return

        if only_webhooks:
            deleted = await interaction.channel.purge(limit=amount, check=lambda m: m.webhook_id is not None)
        else:
            deleted = await interaction.channel.purge(limit=amount)

        await interaction.followup.send(f"✅ He eliminado {len(deleted)} mensajes.", ephemeral=True)
        # Log a webhook de desarrollo si está configurado
        try:
            from discord_webhook import discord_webhook as _logger
            _logger.send_dev_log(f"Bot: eliminado {len(deleted)} mensajes en #{interaction.channel.name} (id:{interaction.channel.id}) por {interaction.user.name}")
        except Exception:
            pass
    except Exception as e:
        logger.exception("Error borrando mensajes")
        await interaction.followup.send(f"❌ Error intentando borrar mensajes: {str(e)}", ephemeral=True)

# Evento: on_ready
@bot.event
async def on_ready():
    # Intent to sync commands (slash) on startup
    await bot.tree.sync()
    logger.info(f"Bot conectado como {bot.user} (ID: {bot.user.id}) - Commands sync OK")

if __name__ == '__main__':
    if not TOKEN:
        logger.error('DISCORD_BOT_TOKEN no configurado; el bot no se iniciará')
    else:
        try:
            bot.run(TOKEN)
        except Exception as e:
            # Mostrar info amigable si es problema de 'PrivilegedIntentsRequired'
            try:
                import discord as _discord
                if isinstance(e, _discord.errors.PrivilegedIntentsRequired):
                    logger.error("Privileged intents required: enable Message Content intent in Discord Developer Portal or set DISCORD_INTENT_MESSAGE_CONTENT=false in .env to disable it.")
                    logger.error("Developer Portal: https://discord.com/developers/applications -> Your App -> Bot -> Privileged Gateway Intents -> Message Content")
                    raise
            except Exception:
                pass
            logger.exception('Error inicializando el bot')
