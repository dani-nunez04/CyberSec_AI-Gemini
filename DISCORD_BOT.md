# 🤖 Discord Cleaner Bot - Guía de Configuración

Este archivo explica cómo crear un Bot en Discord que permite limpiar mensajes del canal con `/clear` o `!clear`.

---

## 1) Crear el Bot en Discord Developer Portal

1. Ve a https://discord.com/developers/applications
2. Click en "New Application" y dale un nombre (ej: CyberSec_AI_Cleaner)
3. En la izquierda: "Bot" → Click "Add Bot" → Confirm
4. Copia el **Token** del bot. Mantenlo privado.
Bot token = MTQ0ODc0ODUzNTcyNTAzNTU0MA.GpE1yp.Kh8etwnmgfKTbJbE46o9EdjgLV3K8Q6F0NUdkw

---

## 2) Añadir el Bot a tu servidor

1. Ve a "OAuth2" → "URL Generator".
2. Scopes: `bot` y `applications.commands`
3. Bot permissions: selecciona `Manage Messages` y `Send Messages` (y `Administrator` si quieres).
4. Copia la URL generada y ábrela en tu navegador; añade el bot al servidor.

---

## 3) Configurar token en `.env`

1. Asegúrate de que `.env` está en `.gitignore` (no se debe subir).
2. Agrega esto a `.env` o usa `./add_bot_token_to_env.sh` para añadir el token de manera interactiva:

```
# Token para el bot (opcional)
DISCORD_BOT_TOKEN=YOUR_DISCORD_BOT_TOKEN
# Opcionalmente restringir a IDs:
ALLOWED_GUILD_IDS=123456789012345678,987654321098765432
ALLOWED_CHANNEL_IDS=987654321098765432
# Opcional: habilitar el privileged Message Content Intent (si usas el comando por texto)
DISCORD_INTENT_MESSAGE_CONTENT=false
```

**Si tu token fue publicado accidentalmente o enviado en un canal público, rota (regenera) el token desde Discord Developer Portal inmediatamente y actualiza `.env` con el nuevo token.**

Si vas a dejar `DISCORD_INTENT_MESSAGE_CONTENT=true`, debes habilitar el intent en: https://discord.com/developers/applications -> Your App -> Bot -> Privileged Gateway Intents -> Message Content (activa la casilla y guarda). Si no, deja `DISCORD_INTENT_MESSAGE_CONTENT=false` y usa solamente los comandos slash (`/clear`).

---

## 4) Ejecutar el bot localmente

```bash
pip install -r requirements.txt
python3 discord_cleaner_bot.py
```

- El bot intentará sincronizar los comandos slash y aparecerá en el servidor.
- Si no ves el slash command de inmediato, espera unos segundos (Discord tarda en propagar los comandos), o reasigna el token o reinicia el bot.

---

## 5) Uso del comando

- Slash command:
  - `/clear amount:100` — El bot borrará los últimos `amount` mensajes (predeterminado 100)
  - Opciones adicionales de Slash: `only_webhooks` (boolean) y `dry_run` (boolean)
  - Ejemplo: `/clear amount:200 only_webhooks:true dry_run:false`

- Comando de texto: `!clear 50 --only-webhooks --dry-run` — Alternativa (útil en servidores antiguos).

**Limitaciones**:
- `channel.purge(limit=amount)` puede eliminar solo mensajes de los últimos 14 días mediante `bulk delete`.
- Para mensajes más antiguos, el bot borrará individualmente si fuera necesario (esto puede ser mucho más lento y estar sujeto a rate limits).
- `only_webhooks` permite seleccionar y eliminar solamente mensajes creados por webhooks (p. ej. los posts de `#logs-analisis`).

---

## 6) Permisos y seguridad

- El comando `/clear` está restringido a usuarios con el permiso `manage_messages`.
- Para más seguridad, restringe el uso a un rol específico o a administradores. Puedes actualizar el check en el script.

---

## 7) Extensiones posibles

- Añadir logs de limpieza (p. ej. enviar evento a `#logs-analisis` o registrar en una DB)
- Añadir confirmación interactiva (bot pide Confirm/Cancel con botones)
- Implementar `purge` seleccionando solo mensajes generados por webhooks o por usuarios
- Añadir comando para crear thread y archivar resultados

---

## 8) Notas finales

Para más detalles sobre invitar bots vs crear uno propio, ver [DISCORD_BOT_INVITE.md](DISCORD_BOT_INVITE.md).

- No me envíes el token en este chat; si quieres que configure algo, hazlo localmente con las instrucciones.
- Si quieres, puedo añadir un comando `/clear-all` que borre todos los mensajes hasta cierto punto (con confirmación), o un filtro para borrar solo los mensajes del webhook si prefieres limpiar solo los logs generados por CyberSec AI.