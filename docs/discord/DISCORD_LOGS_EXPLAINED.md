# 📊 Cómo Funcionan los Logs en Discord

## 🔄 Flujo Completo de un Análisis

Cuando ejecutas un análisis, los logs se envían en **DOS LUGARES**:

### 1️⃣ En la Web (HTTP)
- Los logs aparecen en tiempo real en `http://localhost:8001`
- El frontend hace polling cada 500ms
- Ve un panel de "Investigación en Progreso"
- Puedes descargar el reporte

### 2️⃣ En Discord (Webhooks)
- Los logs se envían automáticamente a `#logs-analisis`
- Puedes ver el progreso sin abrir la web
- Notificaciones de inicio y finalización
- Errores en `#errores-internos`

---

## 📨 Qué se Envía a Discord

### Durante el Análisis

```
[Segundo 0] → Inicio
🚀 Nuevo Análisis Iniciado
Target: 192.168.1.1
Tipo: basic
Job ID: abc123...

[Segundo 5] → Nmap
🔍 Iniciando escaneo Nmap en 192.168.1.1
🔍 Ejecutando: sudo nmap -sV -T4 192.168.1.1
✅ Escaneo completado exitosamente

[Segundo 10] → Servicios
🔍 Extrayendo servicios...
✅ Servicios encontrados: 5

[Segundo 15] → IA
🔍 Iniciando análisis con Ollama...
✅ Análisis completado

[Segundo 20] → Exploits
🔍 Buscando exploits...
🎯 Exploit Encontrado
Servicio: OpenSSH 7.4
Exploit: OpenSSH < 6.6 SFTP Command Execution
... más exploits ...

[Segundo 30] → Fin
✨ Análisis Completado
Target: 192.168.1.1
Servicios: 5
Exploits: 23
Job ID: abc123...
```

---

## 🎯 Dónde Va Cada Tipo

| Evento | Canal | Webhook |
|--------|-------|---------|
| 🚀 Inicio | #logs-analisis | DISCORD_WEBHOOK_LOGS_ANALISIS |
| 🔍 Búsqueda de servicios | #logs-analisis | DISCORD_WEBHOOK_LOGS_ANALISIS |
| 🔍 Búsqueda de exploits | #logs-analisis | DISCORD_WEBHOOK_LOGS_ANALISIS |
| 🎯 Exploit encontrado | #logs-analisis | DISCORD_WEBHOOK_LOGS_ANALISIS |
| ✅ Éxitos | #logs-analisis | DISCORD_WEBHOOK_LOGS_ANALISIS |
| ✨ Completación | #logs-analisis | DISCORD_WEBHOOK_LOGS_ANALISIS |
| ❌ Error | #errores-internos | DISCORD_WEBHOOK_ERRORES |
| ⚠️ Warning | #desarrollo | DISCORD_WEBHOOK_DESARROLLO |

---

## 💻 Ejemplo en Código

### En app.py

```python
# 1. Cuando inicia un análisis
discord_webhook.send_job_start(job_id, target_ip, scan_type)

# 2. Durante los logs normales
add_log(f"Iniciando escaneo Nmap en {ip}", "searching")
# Esto se envía automáticamente a Discord también

# 3. Cuando se completa
discord_webhook.send_job_complete(job_id, target_ip, services_count, exploits_count)

# 4. Si hay error
discord_webhook.send_job_error(job_id, target_ip, error_message)

# 5. Exploit encontrado (opcional)
discord_webhook.send_exploit_found(job_id, service, exploit_name)
```

---

## 🌐 Comparación: Web vs Discord

| Aspecto | Web | Discord |
|--------|-----|---------|
| **Acceso** | Necesitas navegador | En el servidor Discord |
| **Tiempo Real** | Polling cada 500ms | Inmediato |
| **Historial** | Solo sesión actual | Historial completo |
| **Notificaciones** | Debes estar en la web | Menciones si quieres |
| **Descargar Reporte** | ✅ Sí | ❌ No |
| **Responsivo** | Bueno | Perfecto |
| **Offline** | ❌ No | ✅ Sí (puedes leer después) |

---

## 📝 Estructura de un Embed de Discord

Cada mensaje en Discord tiene esta estructura:

```
┌─────────────────────────────────┐
│ 🚀 Nuevo Análisis Iniciado      │ ← Emoji + Título
├─────────────────────────────────┤
│ Target: `192.168.1.1`           │ ← Descripción
│ Tipo: `basic`                   │
├─────────────────────────────────┤
│ Job ID `abc123...`              │ ← Campo adicional
├─────────────────────────────────┤
│ 2025-12-11 14:32:45             │ ← Timestamp
│ CyberSec_AI Pentest Assistant   │ ← Footer
└─────────────────────────────────┘
```

---

## 🎨 Sistema de Colores

```
🔵 AZUL (#3498DB)
   └─ Información general
   └─ Uso: Mensajes informativos

🟠 NARANJA (#F39C12)
   └─ Búsquedas en progreso
   └─ Uso: Status de análisis

🟢 VERDE (#2ECC71)
   └─ Éxitos
   └─ Uso: Análisis completado, exploits encontrados

🔴 ROJO (#E74C3C)
   └─ Errores
   └─ Uso: Fallos y excepciones
```

---

## ⚙️ Configuración Avanzada

### Si quieres agregar logs personalizados

En `app.py`, puedes hacer:

```python
# Log normal (va a web y Discord si es importante)
add_log("Tu mensaje aquí", "info")

# Enviar solo a Discord manualmente
discord_webhook.send_dev_log("Log de desarrollo", "info")

# Enviar error a Discord
discord_webhook.send_job_error(job_id, target_ip, "Mensaje de error")

# Exploit encontrado
discord_webhook.send_exploit_found(job_id, "MySQL 5.7", "MySQL Authentication Bypass")
```

---

## 🔒 Privacidad

Los embeds **NO contienen**:
- ❌ Credenciales
- ❌ Datos sensibles
- ❌ Archivos o reportes
- ❌ Resultados completos

Solo contienen:
- ✅ IP del target
- ✅ Tipo de análisis
- ✅ Job ID
- ✅ Status y progreso
- ✅ Mensajes de error

---

## 🚨 Si Algo Sale Mal

### No veo logs en Discord
1. Verifica que `.env` está configurado
2. Verifica que los webhooks son válidos
3. Mira la consola de `python app.py` para errores
4. Reinicia la app

### Los logs van al canal equivocado
1. Los webhooks envían al canal que seleccionaste
2. Para cambiar: edita el webhook en Discord
3. O crea uno nuevo y actualiza `.env`

### Demasiados mensajes en Discord
- Cada log genera un mensaje
- Esto es normal durante un análisis
- Los webhooks tienen rate limit pero es alto

---

## 💡 Pro Tips

### 1. Usar threads en Discord
```
Discord > Click en un embed > "Create Thread"
Todos los logs se agruperan en un thread
```

### 2. Roles y menciones
```
En Discord, puedes mencionar roles:
"@security-team Un análisis completado"
Requiere configuración adicional
```

### 3. Reacciones automáticas
```
Discord bot (futuro):
- ✅ Reacción si completó exitosamente
- ❌ Reacción si hay error
```

---

## 📖 Relacionado

- **DISCORD_INTEGRATION.md** - Documentación técnica
- **SETUP_DISCORD_WEBHOOKS.md** - Cómo crear webhooks
- **discord_webhook.py** - Código del módulo
