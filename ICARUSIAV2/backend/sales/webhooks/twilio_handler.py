from __future__ import annotations

from fastapi import Request
import logging

try:
    from twilio.twiml.messaging_response import MessagingResponse  # type: ignore
except Exception:  # pragma: no cover
    MessagingResponse = None  # type: ignore

logger = logging.getLogger("icarusiav2.twilio")


class TwilioWebhookHandler:
    async def handle_incoming_message(self, request: Request) -> str:
        try:
            form = await request.form()
            body = (form.get("Body") or "").strip()
            frm = form.get("From")
            logger.info("twilio_in", from_number=frm, body_preview=body[:80])
            if not MessagingResponse:
                return "Twilio SDK not installed"
            resp = MessagingResponse()
            resp.message("Recibido. ¿Qué producto/servicio te interesa y cuál es tu objetivo?")
            return str(resp)
        except Exception as e:
            logger.error("twilio_error", error=str(e))
            if not MessagingResponse:
                return "Twilio SDK not installed"
            resp = MessagingResponse()
            resp.message("Error procesando mensaje.")
            return str(resp)

"""
Twilio Webhook Handler
Handles incoming webhooks from Twilio
"""

from typing import Dict, Any, Optional
from fastapi import Request, HTTPException
import structlog
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from config.settings import settings

logger = structlog.get_logger()


class TwilioWebhookHandler:
    """Handles Twilio webhooks"""
    
    def __init__(self):
        self.client = None
        if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
            self.client = Client(
                settings.TWILIO_ACCOUNT_SID,
                settings.TWILIO_AUTH_TOKEN
            )
            logger.info("Twilio client initialized")
        else:
            logger.warning("Twilio credentials not configured")
    
    async def handle_incoming_message(
        self,
        request: Request
    ) -> str:
        """Handle incoming Twilio message"""
        try:
            form_data = await request.form()
            
            message_sid = form_data.get("MessageSid")
            from_number = form_data.get("From")
            to_number = form_data.get("To")
            body = form_data.get("Body", "")
            
            logger.info(
                "Twilio message received",
                message_sid=message_sid,
                from_number=from_number,
                body_preview=body[:50]
            )
            
            # Process message (integrate with sales agent)
            # This would call the sales script engine
            
            # Create response
            response = MessagingResponse()
            response.message("Mensaje recibido. Procesando...")
            
            return str(response)
            
        except Exception as e:
            logger.error("Twilio webhook error", error=str(e))
            response = MessagingResponse()
            response.message("Error procesando mensaje.")
            return str(response)
    
    async def handle_incoming_call(
        self,
        request: Request
    ) -> str:
        """Handle incoming Twilio call"""
        try:
            form_data = await request.form()
            
            call_sid = form_data.get("CallSid")
            from_number = form_data.get("From")
            to_number = form_data.get("To")
            
            logger.info(
                "Twilio call received",
                call_sid=call_sid,
                from_number=from_number
            )
            
            # Create TwiML response
            from twilio.twiml.voice_response import VoiceResponse
            
            response = VoiceResponse()
            response.say("Hola, bienvenido a Icarus IA.", language="es-ES")
            response.record(max_length=60, transcribe=True)
            
            return str(response)
            
        except Exception as e:
            logger.error("Twilio call error", error=str(e))
            from twilio.twiml.voice_response import VoiceResponse
            response = VoiceResponse()
            response.say("Lo siento, hubo un error.", language="es-ES")
            return str(response)
    
    async def send_message(
        self,
        to: str,
        body: str,
        from_number: Optional[str] = None
    ) -> Optional[str]:
        """Send message via Twilio"""
        if not self.client:
            logger.error("Twilio client not initialized")
            return None
        
        try:
            message = self.client.messages.create(
                body=body,
                from_=from_number or settings.TWILIO_PHONE_NUMBER,
                to=to
            )
            
            logger.info("Twilio message sent", message_sid=message.sid, to=to)
            
            return message.sid
            
        except Exception as e:
            logger.error("Twilio send error", error=str(e))
            return None
    
    async def make_call(
        self,
        to: str,
        url: str,
        from_number: Optional[str] = None
    ) -> Optional[str]:
        """Make call via Twilio"""
        if not self.client:
            return None
        
        try:
            call = self.client.calls.create(
                url=url,
                from_=from_number or settings.TWILIO_PHONE_NUMBER,
                to=to
            )
            
            logger.info("Twilio call initiated", call_sid=call.sid, to=to)
            
            return call.sid
            
        except Exception as e:
            logger.error("Twilio call error", error=str(e))
            return None
    
    def verify_webhook(self, request: Request) -> bool:
        """Verify Twilio webhook signature"""
        # Implement Twilio signature verification
        # For now, return True (should implement proper verification in production)
        return True
