# 📊 Diferencias: Escaneo Básico vs Profundo

## Comparación Rápida

| Aspecto | Básico | Profundo |
|---------|--------|----------|
| **Flags** | `-sV -T4` | `-sV -sC -T3` |
| **Tiempo** | 30-60 seg | 2-5 minutos |
| **Puertos** | 1000 más comunes | Todos (65535) |
| **Versiones** | ✅ Sí | ✅ Sí |
| **Scripts NSE** | ❌ No | ✅ Sí (detección avanzada) |
| **Velocidad** | ⚡ Agresiva | 🐢 Normal |
| **Precisión** | Buena | Excelente |
| **Uso** | Reconnaissance rápida | Análisis completo |

## Detalles de Flags Nmap

### Escaneo Básico
```bash
nmap -sV -T4 google.com
```

- **`-sV`**: "Service Version Detection"
  - Detecta la versión del servicio corriendo en cada puerto abierto
  - Ejemplo: `80/tcp open http Apache httpd 2.4.1`

- **`-T4`**: "Timing Template Aggressive"
  - Velocidad agresiva, escanea rápido
  - Usa paralelismo alto
  - Riesgo: Puede desencadenar IDS/firewalls

### Escaneo Profundo
```bash
nmap -sV -sC -T3 google.com
```

- **`-sV`**: (igual al básico)
  - Detecta versiones de servicios

- **`-sC`**: "Default NSE Scripts"
  - Ejecuta scripts NSE (Nmap Scripting Engine)
  - Scripts de detección de vulnerabilidades
  - Obtiene información más detallada (banners, configuración, etc)
  - Ejemplo: detecta heartbleed, ssl-cert, http-title, etc.

- **`-T3`**: "Timing Template Normal"
  - Velocidad normal/balanceada
  - Menos paralelismo que T4
  - Más preciso, menos detectado por IDS

## ¿Cuándo usar cada uno?

### ✅ Usa Escaneo Básico cuando:
- Necesitas resultado rápido (reconnaissance inicial)
- Tienes poco tiempo
- Quieres evitar detectar el escaneo
- Es tu primer scan de un target

### ✅ Usa Escaneo Profundo cuando:
- Necesitas análisis completo
- Tienes tiempo disponible
- Es un test autorizado (no importa detectar)
- Buscas todas las vulnerabilidades posibles
- Es parte de un pentest completo

## Ejemplo de Salida

### Básico
```
Nmap scan report for google.com
Host is up (0.25s latency).
rDNS record for 142.251.32.14: par21s27-in-f14.1e100.net
Not shown: 997 filtered ports
PORT    STATE SERVICE VERSION
80/tcp  open  http    Google httpd
443/tcp open  https   Google httpd
```

### Profundo
```
Nmap scan report for google.com
Host is up (0.25s latency).
rDNS record for 142.251.32.14: par21s27-in-f14.1e100.net
Not shown: 65533 filtered ports
PORT    STATE SERVICE VERSION
80/tcp  open  http    Google httpd
| http-title: Google
| http-methods: GET, HEAD, OPTIONS, TRACE, POST, PUT, DELETE
443/tcp open  https   Google httpd
| ssl-cert: Subject: commonName=*.google.com
| ssl-date: 2025-12-01T12:00:00Z
```

## En CyberSec AI

En la interfaz web, puedes seleccionar:
- **Escaneo Básico** (botón radio): Reconnaissance rápida
- **Escaneo Profundo** (botón radio): Análisis completo

```html
<label class="scan-option">
    <input type="radio" name="scanType" value="basic" checked>
    <span>Escaneo Básico</span>
</label>
<label class="scan-option">
    <input type="radio" name="scanType" value="deep">
    <span>Escaneo Profundo</span>
</label>
```

El tipo seleccionado se envía en la petición POST a `/api/analyze`:
```json
{
  "target_ip": "google.com",
  "scan_type": "basic"  // o "deep"
}
```
