# 🚀 Guía: Crear Webhooks de Discord para CyberSec AI

Te muestro exactamente cómo crear los webhooks paso a paso.

---

## 📝 Paso 1: Acceder a los Webhooks de Discord

### En tu servidor "CyberSec AI":
1. **Click derecho** en el nombre del servidor (arriba a la izquierda)
2. Selecciona **"Configuración del Servidor"**
3. En el lado izquierdo, ve a **"Integraciones"**
4. Click en **"Webhooks"** (si no lo ves, busca en la barra lateral)

---

## 🔗 Paso 2: Crear Webhook para "logs-analisis"

### Para que los logs del análisis vayan aquí:

1. En la página de Webhooks, click en **"Nuevo Webhook"**
2. Completa así:
   - **Nombre:** `CyberSec-Logs-Analisis`
   - **Canal:** Selecciona `#logs-analisis`
3. Click en **"Copiar URL del Webhook"** (el botón azul grande)
4. **GUARDA ESTA URL** en tu `.env` como:
   ```
   DISCORD_WEBHOOK_LOGS_ANALISIS=https://discord.com/api/webhooks/XXXXX/YYYYY
   ```

---

## 🔗 Paso 3: Crear Webhook para "errores-internos"

### Para que los errores vayan aquí:

1. Click en **"Nuevo Webhook"** nuevamente
2. Completa así:
   - **Nombre:** `CyberSec-Errores`
   - **Canal:** Selecciona `#errores-internos`
3. Click en **"Copiar URL del Webhook"**
4. **GUARDA ESTA URL** en tu `.env` como:
   ```
   DISCORD_WEBHOOK_ERRORES=https://discord.com/api/webhooks/XXXXX/YYYYY
   ```

---

## 🔗 Paso 4: (Opcional) Webhook para "desarrollo"

### Para logs generales de desarrollo:

1. Click en **"Nuevo Webhook"** otra vez
2. Completa así:
   - **Nombre:** `CyberSec-Desarrollo`
   - **Canal:** Selecciona `#desarrollo`
3. Click en **"Copiar URL del Webhook"**
4. **GUARDA ESTA URL** en tu `.env` como:
   ```
   DISCORD_WEBHOOK_DESARROLLO=https://discord.com/api/webhooks/XXXXX/YYYYY
   ```

---

## 📄 Tu archivo `.env` Final

Copia esto en `/workspaces/CyberSec_AI/.env`:

```bash
# Discord Webhooks
DISCORD_WEBHOOK_LOGS_ANALISIS=https://discord.com/api/webhooks/XXXXX/YYYYY
DISCORD_WEBHOOK_ERRORES=https://discord.com/api/webhooks/XXXXX/YYYYY
DISCORD_WEBHOOK_DESARROLLO=https://discord.com/api/webhooks/XXXXX/YYYYY
```

**⚠️ IMPORTANTE:** Reemplaza `XXXXX/YYYYY` con los valores reales de tus webhooks.
