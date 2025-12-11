"""
Discord Webhook Integration
Envía logs de análisis a Discord en tiempo real via webhooks.
Soporta múltiples webhooks para diferentes canales.
"""

import requests
import logging
from datetime import datetime
from typing import Optional
import os

# Intentar cargar dotenv
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

logger = logging.getLogger(__name__)

class DiscordWebhook:
    """Gestor de webhooks de Discord para logs de análisis."""
    
    def __init__(self):
        """
        Inicializa los webhooks de Discord desde variables de entorno.
        
        Variables soportadas:
        - DISCORD_WEBHOOK_LOGS_ANALISIS: Para logs de análisis
        - DISCORD_WEBHOOK_ERRORES: Para errores
        - DISCORD_WEBHOOK_DESARROLLO: Para logs generales
        """
        # Cargar webhooks del .env
        self.webhook_logs = os.getenv("DISCORD_WEBHOOK_LOGS_ANALISIS")
        self.webhook_errors = os.getenv("DISCORD_WEBHOOK_ERRORES")
        self.webhook_dev = os.getenv("DISCORD_WEBHOOK_DESARROLLO")
        
        # Mostrar estado
        if self.webhook_logs:
            logger.info("✅ Discord Webhook LOGS_ANALISIS activado")
        else:
            logger.info("⚠️ Discord Webhook LOGS_ANALISIS desactivado")
            
        if self.webhook_errors:
            logger.info("✅ Discord Webhook ERRORES activado")
        else:
            logger.info("⚠️ Discord Webhook ERRORES desactivado")
            
        if self.webhook_dev:
            logger.info("✅ Discord Webhook DESARROLLO activado")
        else:
            logger.info("⚠️ Discord Webhook DESARROLLO desactivado")
    
    def _send_to_webhook(self, webhook_url: Optional[str], embed: dict) -> bool:
        """
        Envía un embed a un webhook específico.
        
        Args:
            webhook_url: URL del webhook de Discord
            embed: Diccionario con estructura de embed
            
        Returns:
            True si se envió exitosamente, False en caso contrario
        """
        if not webhook_url:
            return False
        
        try:
            payload = {"embeds": [embed]}
            response = requests.post(webhook_url, json=payload, timeout=5)
            return response.status_code == 204
        except Exception as e:
            logger.warning(f"⚠️ Error enviando a Discord: {e}")
            return False
    
    def _create_embed(self, title: str, description: str, color: int, emoji: str, 
                     job_id: Optional[str] = None, extra_fields: list = None) -> dict:
        """
        Crea un embed de Discord estructurado.
        
        Args:
            title: Título del embed
            description: Descripción principal
            color: Color en formato hexadecimal
            emoji: Emoji para el título
            job_id: ID del job (opcional)
            extra_fields: Lista de campos adicionales (opcional)
            
        Returns:
            Diccionario con estructura de embed
        """
        embed = {
            "title": f"{emoji} {title}",
            "description": description,
            "color": color,
            "timestamp": datetime.now().isoformat(),
            "footer": {"text": "CyberSec_AI Pentest Assistant"}
        }
        
        fields = []
        if job_id:
            fields.append({
                "name": "Job ID",
                "value": f"`{job_id}`",
                "inline": True
            })
        
        if extra_fields:
            fields.extend(extra_fields)
        
        if fields:
            embed["fields"] = fields
        
        return embed
    
    def send_job_start(self, job_id: str, target_ip: str, scan_type: str):
        """Envía notificación de inicio de análisis."""
        embed = self._create_embed(
            title="Nuevo Análisis Iniciado",
            description=f"**Target:** `{target_ip}`\n**Tipo:** `{scan_type}`",
            color=0xF39C12,  # Naranja
            emoji="🚀",
            job_id=job_id
        )
        return self._send_to_webhook(self.webhook_logs, embed)
    
    def send_job_complete(self, job_id: str, target_ip: str, services_count: int, 
                         exploits_count: int):
        """Envía notificación de análisis completado."""
        embed = self._create_embed(
            title="Análisis Completado",
            description=f"**Target:** `{target_ip}`\n**Servicios:** `{services_count}`\n**Exploits:** `{exploits_count}`",
            color=0x2ECC71,  # Verde
            emoji="✨",
            job_id=job_id
        )
        return self._send_to_webhook(self.webhook_logs, embed)
    
    def send_job_error(self, job_id: str, target_ip: str, error_message: str):
        """Envía notificación de error."""
        error_text = error_message[:500] if len(error_message) > 500 else error_message
        embed = self._create_embed(
            title="Error en Análisis",
            description=f"**Target:** `{target_ip}`\n**Error:** ```\n{error_text}\n```",
            color=0xE74C3C,  # Rojo
            emoji="❌",
            job_id=job_id
        )
        return self._send_to_webhook(self.webhook_errors, embed)
    
    def send_log(self, message: str, log_type: str = "info", job_id: Optional[str] = None):
        """
        Envía un log individual a Discord.
        
        Args:
            message: Mensaje de log
            log_type: Tipo ("info", "searching", "success", "error")
            job_id: ID del job (opcional)
        """
        color_map = {
            "info": 0x3498DB,      # Azul
            "searching": 0xF39C12,  # Naranja
            "success": 0x2ECC71,    # Verde
            "error": 0xE74C3C       # Rojo
        }
        
        emoji_map = {
            "info": "ℹ️",
            "searching": "🔍",
            "success": "✅",
            "error": "❌"
        }
        
        color = color_map.get(log_type, 0x3498DB)
        emoji = emoji_map.get(log_type, "")
        webhook = self.webhook_logs if log_type != "error" else self.webhook_errors
        
        embed = self._create_embed(
            title="Log de Análisis",
            description=message,
            color=color,
            emoji=emoji,
            job_id=job_id
        )
        
        return self._send_to_webhook(webhook, embed)
    
    def send_exploit_found(self, job_id: str, service: str, exploit_name: str):
        """Envía notificación cuando se encuentra un exploit."""
        embed = self._create_embed(
            title="Exploit Encontrado",
            description=f"**Servicio:** `{service}`\n**Exploit:** {exploit_name}",
            color=0x2ECC71,  # Verde
            emoji="🎯",
            job_id=job_id
        )
        return self._send_to_webhook(self.webhook_logs, embed)
    
    def send_dev_log(self, message: str, level: str = "info"):
        """
        Envía un log de desarrollo al canal #desarrollo.
        
        Args:
            message: Mensaje del log
            level: Nivel ("info", "warning", "error")
        """
        color_map = {
            "info": 0x3498DB,
            "warning": 0xF39C12,
            "error": 0xE74C3C
        }
        
        emoji_map = {
            "info": "ℹ️",
            "warning": "⚠️",
            "error": "❌"
        }
        
        color = color_map.get(level, 0x3498DB)
        emoji = emoji_map.get(level, "")
        
        embed = self._create_embed(
            title="Log de Desarrollo",
            description=message,
            color=color,
            emoji=emoji
        )
        
        return self._send_to_webhook(self.webhook_dev, embed)


# Instancia global
discord_webhook = DiscordWebhook()
