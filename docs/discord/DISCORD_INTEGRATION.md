# 🤖 Discord Webhook Integration

El sistema ahora envía logs en tiempo real a Discord usando webhooks. Monitorea tus análisis directamente desde Discord.

## 🎯 Estructura de Canales

El sistema soporta 3 webhooks diferentes para 3 canales:

```
Servidor: CyberSec AI
├── #desarrollo
│   └── Logs generales de desarrollo
├── #logs-analisis
│   └── Todos los logs del análisis
└── #errores-internos
    └── Errores de la API
```

## 🔧 Setup Rápido

### 1. Copia la Guía Completa
Ve a **SETUP_DISCORD_WEBHOOKS.md** para la guía paso a paso de cómo crear webhooks en Discord.

### 2. Copia tu Archivo `.env`

Una vez tengas los 3 webhooks creados, crea un archivo `.env` en la raíz:

```bash
# Discord Webhooks
DISCORD_WEBHOOK_LOGS_ANALISIS=https://discord.com/api/webhooks/XXXXX/YYYYY
DISCORD_WEBHOOK_ERRORES=https://discord.com/api/webhooks/XXXXX/YYYYY
DISCORD_WEBHOOK_DESARROLLO=https://discord.com/api/webhooks/XXXXX/YYYYY
```

### 3. Inicia la Aplicación

```bash
python app.py
```

Deberías ver:
```
✅ Discord Webhook LOGS_ANALISIS activado
✅ Discord Webhook ERRORES activado
✅ Discord Webhook DESARROLLO activado
```

---

## 📊 Qué se Envía a Cada Canal

### 🔍 #logs-analisis
- ✅ Inicio del análisis
- ✅ Logs de búsqueda de servicios
- ✅ Logs de búsqueda de exploits
- ✅ Exploits encontrados
- ✅ Análisis completado exitosamente

**Ejemplo:**
```
🚀 Nuevo Análisis Iniciado
Target: 192.168.1.1
Tipo: basic

[5 minutos después...]

✨ Análisis Completado
Target: 192.168.1.1
Servicios: 5
Exploits: 23
```

### ⚠️ #errores-internos
- ❌ Errores en el análisis
- ❌ Errores de conexión
- ❌ Errores de Nmap
- ❌ Errores de Ollama
- ❌ Errores internos

**Ejemplo:**
```
❌ Error en Análisis
Target: 192.168.1.1
Error: Connection timeout
```

### 🔧 #desarrollo
- ℹ️ Logs informativos del sistema
- ⚠️ Warnings
- ❌ Errores internos del servidor

---

## 🎨 Sistema de Colores

Los embeds de Discord usan colores para identificar rápidamente:

| Emoji | Color | Significado |
|-------|-------|------------|
| 🔵 | Azul | Información general |
| 🟠 | Naranja | Búsquedas en progreso |
| 🟢 | Verde | Éxitos |
| 🔴 | Rojo | Errores |

---

## 📋 Información en Cada Mensaje

Cada embed de Discord incluye:

1. **Título con Emoji** - Identifica el tipo de evento
2. **Descripción** - Detalles del evento
3. **Job ID** - ID único del análisis (si aplica)
4. **Timestamp** - Hora exacta del evento
5. **Footer** - "CyberSec_AI Pentest Assistant"

**Ejemplo completo:**
```
🚀 Nuevo Análisis Iniciado
Target: `192.168.1.1`
Tipo: `deep`
Job ID: `a1b2c3d4-e5f6-g7h8-i9j0`
Enviado a las 14:32:45
```

---

## 🔒 Seguridad

### ⚠️ NUNCA hagas commit de `.env`

Verifica tu `.gitignore`:
```bash
echo ".env" >> .gitignore
git add .gitignore
git commit -m "Protect .env"
```

### Si Expones un Webhook Accidentalmente

1. Ve a Discord → Configuración → Integraciones → Webhooks
2. Haz click en el webhook expuesto
3. Click en **"Eliminar Webhook"**
4. Crea uno nuevo
5. Actualiza la URL en `.env`

---

## 🧪 Funcionamiento Sin Webhooks

Si no configuras webhooks:
- ✅ El sistema continúa funcionando normalmente
- ✅ Los logs se mostrarán en la web como siempre
- ✅ Solo verás warnings: `⚠️ Discord Webhook XXX desactivado`

Puedes tener algunos webhooks y otros desactivados sin problemas.

---

## 📝 Archivos Relacionados

- **SETUP_DISCORD_WEBHOOKS.md** - Guía paso a paso
- **discord_webhook.py** - Módulo de integración
- **.env.example** - Template de configuración

---

## 🆘 Troubleshooting

### No veo mensajes en Discord
- Verifica que el webhook no fue eliminado en Discord
- Verifica que la URL está correcta en `.env`
- Asegúrate de que hiciste `python app.py` DESPUÉS de crear `.env`
- Reinicia la aplicación

### Los mensajes van al canal equivocado
- Los webhooks envían al canal seleccionado al crearlos
- Para cambiar: edita el webhook en Discord y selecciona otro canal

### Webhook expirado/inválido
- Ve a Discord y crea un webhook nuevo
- Copia la nueva URL en `.env`
- Reinicia la app

---

**Para la guía detallada de creación de webhooks, ve a SETUP_DISCORD_WEBHOOKS.md**
