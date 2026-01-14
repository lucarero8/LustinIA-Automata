from __future__ import annotations

from typing import Any, Dict


class WhatsAppAPI:
    async def handle_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        # Minimal handler; tu integración real irá aquí.
        entry = (payload.get("entry") or [{}])[0]
        changes = (entry.get("changes") or [{}])[0]
        value = changes.get("value") or {}
        messages = value.get("messages") or []
        if not messages:
            return {"status": "no_messages"}

        msg = messages[0]
        text = ""
        if msg.get("type") == "text":
            text = (msg.get("text") or {}).get("body", "")
        return {"status": "received", "from": msg.get("from"), "text": text}

"""
WhatsApp Business API Integration
Integrates with WhatsApp Business API
"""

from typing import Dict, Any, Optional
import structlog
import httpx
from config.settings import settings

logger = structlog.get_logger()


class WhatsAppAPI:
    """WhatsApp Business API client"""
    
    def __init__(self):
        self.api_token = settings.WHATSAPP_API_TOKEN
        self.phone_number_id = settings.WHATSAPP_PHONE_NUMBER_ID
        self.verify_token = settings.WHATSAPP_VERIFY_TOKEN
        self.base_url = "https://graph.facebook.com/v18.0"
        self._client = None
    
    def _get_client(self) -> httpx.AsyncClient:
        """Get HTTP client"""
        if not self._client:
            self._client = httpx.AsyncClient(
                timeout=30.0,
                headers={
                    "Authorization": f"Bearer {self.api_token}",
                    "Content-Type": "application/json"
                }
            )
        return self._client
    
    async def send_text_message(
        self,
        to: str,
        text: str
    ) -> Optional[Dict[str, Any]]:
        """Send text message via WhatsApp"""
        if not self.api_token or not self.phone_number_id:
            logger.error("WhatsApp API not configured")
            return None
        
        try:
            url = f"{self.base_url}/{self.phone_number_id}/messages"
            
            payload = {
                "messaging_product": "whatsapp",
                "to": to,
                "type": "text",
                "text": {
                    "body": text
                }
            }
            
            client = self._get_client()
            response = await client.post(url, json=payload)
            response.raise_for_status()
            
            result = response.json()
            
            logger.info("WhatsApp message sent", to=to, message_id=result.get("messages", [{}])[0].get("id"))
            
            return result
            
        except Exception as e:
            logger.error("WhatsApp send error", error=str(e))
            return None
    
    async def send_template_message(
        self,
        to: str,
        template_name: str,
        parameters: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Send template message via WhatsApp"""
        if not self.api_token or not self.phone_number_id:
            return None
        
        try:
            url = f"{self.base_url}/{self.phone_number_id}/messages"
            
            payload = {
                "messaging_product": "whatsapp",
                "to": to,
                "type": "template",
                "template": {
                    "name": template_name,
                    "language": {
                        "code": "es"
                    },
                    "components": [
                        {
                            "type": "body",
                            "parameters": [
                                {"type": "text", "text": str(v)}
                                for v in parameters.values()
                            ]
                        }
                    ]
                }
            }
            
            client = self._get_client()
            response = await client.post(url, json=payload)
            response.raise_for_status()
            
            result = response.json()
            
            logger.info("WhatsApp template sent", to=to, template=template_name)
            
            return result
            
        except Exception as e:
            logger.error("WhatsApp template error", error=str(e))
            return None
    
    async def handle_webhook(
        self,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle incoming WhatsApp webhook"""
        try:
            entry = payload.get("entry", [{}])[0]
            changes = entry.get("changes", [{}])[0]
            value = changes.get("value", {})
            messages = value.get("messages", [])
            
            if not messages:
                return {"status": "no_messages"}
            
            message = messages[0]
            from_number = message.get("from")
            message_id = message.get("id")
            message_type = message.get("type")
            
            # Extract text
            text = ""
            if message_type == "text":
                text = message.get("text", {}).get("body", "")
            
            logger.info(
                "WhatsApp message received",
                from_number=from_number,
                message_id=message_id,
                message_type=message_type,
                text_preview=text[:50]
            )
            
            return {
                "status": "received",
                "from": from_number,
                "message_id": message_id,
                "type": message_type,
                "text": text
            }
            
        except Exception as e:
            logger.error("WhatsApp webhook error", error=str(e))
            return {"status": "error", "error": str(e)}
    
    def verify_webhook(
        self,
        mode: str,
        token: str,
        challenge: str
    ) -> Optional[str]:
        """Verify WhatsApp webhook"""
        if mode == "subscribe" and token == self.verify_token:
            logger.info("WhatsApp webhook verified")
            return challenge
        return None
    
    async def get_message_status(
        self,
        message_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get message delivery status"""
        # This would require webhook handling to track status
        # For now, return None
        return None
