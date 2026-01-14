from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Request
from pydantic import BaseModel

from sales.objections.handler import ObjectionHandler
from sales.scripts.engine import SalesScriptEngine
from sales.webhooks.twilio_handler import TwilioWebhookHandler
from sales.whatsapp.api import WhatsAppAPI

router = APIRouter()


class SalesMessageRequest(BaseModel):
    message: str
    session_id: str
    conversation_history: Optional[List[str]] = None
    customer_data: Optional[Dict[str, Any]] = None


class ObjectionRequest(BaseModel):
    message: str
    conversation_history: List[str]
    customer_data: Optional[Dict[str, Any]] = None


@router.post("/message")
async def handle_sales_message(request: SalesMessageRequest):
    engine = SalesScriptEngine()
    return await engine.get_response(
        user_message=request.message,
        conversation_history=request.conversation_history or [],
        session_id=request.session_id,
        customer_data=request.customer_data,
    )


@router.post("/objections/handle")
async def handle_objection(request: ObjectionRequest):
    handler = ObjectionHandler()
    return await handler.handle_objection_flow(
        message=request.message,
        conversation_history=request.conversation_history,
        customer_data=request.customer_data,
    )


@router.post("/twilio/webhook")
async def twilio_webhook(request: Request):
    handler = TwilioWebhookHandler()
    twiml = await handler.handle_incoming_message(request)
    return {"twiml": twiml}


@router.post("/whatsapp/webhook")
async def whatsapp_webhook(payload: Dict[str, Any]):
    api = WhatsAppAPI()
    return await api.handle_webhook(payload)

"""Sales API routes"""

from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

router = APIRouter()


class SalesMessageRequest(BaseModel):
    message: str
    session_id: str
    conversation_history: Optional[List[str]] = None
    customer_data: Optional[Dict[str, Any]] = None


class ObjectionRequest(BaseModel):
    message: str
    conversation_history: List[str]
    customer_data: Optional[Dict[str, Any]] = None


@router.post("/message")
async def handle_sales_message(request: SalesMessageRequest):
    """Handle sales message"""
    from sales.scripts.engine import SalesScriptEngine
    
    engine = SalesScriptEngine()
    result = await engine.get_response(
        request.message,
        request.conversation_history or [],
        request.session_id,
        request.customer_data
    )
    return result


@router.post("/objections/handle")
async def handle_objection(request: ObjectionRequest):
    """Handle customer objection"""
    from sales.objections.handler import ObjectionHandler
    
    handler = ObjectionHandler()
    result = await handler.handle_objection_flow(
        request.message,
        request.conversation_history,
        request.customer_data
    )
    return result


@router.post("/twilio/webhook")
async def twilio_webhook(request: Request):
    """Handle Twilio webhook"""
    from sales.webhooks.twilio_handler import TwilioWebhookHandler
    
    handler = TwilioWebhookHandler()
    response = await handler.handle_incoming_message(request)
    return {"response": response}


@router.post("/whatsapp/webhook")
async def whatsapp_webhook(payload: Dict[str, Any]):
    """Handle WhatsApp webhook"""
    from sales.whatsapp.api import WhatsAppAPI
    
    api = WhatsAppAPI()
    result = await api.handle_webhook(payload)
    return result
