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

---

## 🎯 Dónde Va Cada Cosa

| Evento | Canal | Webhook |
|--------|-------|---------|
| Inicio de análisis | logs-analisis | DISCORD_WEBHOOK_LOGS_ANALISIS |
| Logs del análisis | logs-analisis | DISCORD_WEBHOOK_LOGS_ANALISIS |
| Exploits encontrados | logs-analisis | DISCORD_WEBHOOK_LOGS_ANALISIS |
| Análisis completado | logs-analisis | DISCORD_WEBHOOK_LOGS_ANALISIS |
| Errores en análisis | errores-internos | DISCORD_WEBHOOK_ERRORES |
| Errores internos | errores-internos | DISCORD_WEBHOOK_ERRORES |
| Logs generales | desarrollo | DISCORD_WEBHOOK_DESARROLLO |

---

## ✅ Verificar que Funciona

Una vez configurado:

```bash
# 1. Asegúrate de tener el .env creado
ls -la .env

# 2. Inicia la app
python app.py

# 3. Deberías ver en los logs:
# ✅ Discord Webhook LOGS_ANALISIS activado
# ✅ Discord Webhook ERRORES activado
# ✅ Discord Webhook DESARROLLO activado
```

---

## 🔒 Seguridad: Proteger tus URLs

⚠️ **NUNCA hagas commit de `.env`**

Verifica tu `.gitignore`:
```bash
echo ".env" >> .gitignore
git add .gitignore
git commit -m "Add .env to gitignore"
```

---

## 🚨 Si Necesitas Cambiar un Webhook

1. Ve a **Integraciones → Webhooks** en Discord
2. Haz click en el webhook que quieres cambiar
3. Opción 1: **Editar** (cambiar canal o nombre)
4. Opción 2: **Copiar URL** (si perdiste la URL)
5. Opción 3: **Eliminar** (si quieres borrarlo y crear uno nuevo)

---

## 💡 Ejemplo Visual

```
Tu Servidor Discord "CyberSec AI"
│
├── 📌 #desarrollo
│   └── Logs de desarrollo → DISCORD_WEBHOOK_DESARROLLO
│
├── 📊 #logs-analisis
│   └── Logs del análisis → DISCORD_WEBHOOK_LOGS_ANALISIS
│
└── ⚠️ #errores-internos
    └── Errores de la API → DISCORD_WEBHOOK_ERRORES
```

---

## 🆘 Troubleshooting

### No veo las integraciones
- Verifica que tienes permisos de administrador en el servidor
- Intenta actualizar (F5) la página de Discord

### El webhook no funciona
- Verifica que la URL está correcta en `.env`
- Verifica que el webhook no fue eliminado
- Verifica tu conexión a internet

### Los mensajes van al canal equivocado
- El webhook envía al canal que seleccionaste al crearlo
- Para cambiar, edita el webhook en Discord

---

Una vez hayas creado los webhooks y configurado el `.env`, todo debe funcionar automáticamente. 

**¿Ya creaste los webhooks? Avísame cuando estén listos y continuamos con la integración.**
