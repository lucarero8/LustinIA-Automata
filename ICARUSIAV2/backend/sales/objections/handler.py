from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional

try:
    from openai import AsyncOpenAI  # type: ignore
except Exception:  # pragma: no cover
    AsyncOpenAI = None  # type: ignore

from config.settings import settings


class ObjectionType(Enum):
    PRICE = "price"
    TIMING = "timing"
    NEED = "need"
    TRUST = "trust"
    COMPETITOR = "competitor"
    AUTHORITY = "authority"
    OTHER = "other"


class ObjectionHandler:
    def __init__(self):
        self.client = (
            AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if (AsyncOpenAI and settings.OPENAI_API_KEY) else None
        )
        self.model = settings.OPENAI_MODEL

    async def handle_objection_flow(
        self,
        message: str,
        conversation_history: List[str],
        customer_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        objection = self._detect_simple(message)
        if not self.client:
            return {
                "objection": {"type": objection.value, "concern": message, "confidence": 0.5},
                "handling": {"response": "Te entiendo. ¿Qué presupuesto o rango tenías pensado para ver opciones?", "strategy": "fallback"},
            }

        prompt = f"""Eres experto manejando objeciones de ventas.
Mensaje: {message}
Historial: {conversation_history[-5:]}
Cliente: {customer_data or {}}

Devuelve JSON:
{{"type":"price|timing|need|trust|competitor|authority|other","response":"...","next_question":"..."}}
"""
        resp = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
            response_format={"type": "json_object"},
        )
        import json

        data = json.loads(resp.choices[0].message.content or "{}")
        return {
            "objection": {"type": data.get("type", objection.value), "concern": message, "confidence": 0.7},
            "handling": {"response": data.get("response", ""), "next_question": data.get("next_question", "")},
        }

    def _detect_simple(self, message: str) -> ObjectionType:
        m = message.lower()
        if any(w in m for w in ["caro", "precio", "costoso"]):
            return ObjectionType.PRICE
        if any(w in m for w in ["luego", "después", "ahora no"]):
            return ObjectionType.TIMING
        if any(w in m for w in ["no necesito", "no me sirve"]):
            return ObjectionType.NEED
        return ObjectionType.OTHER

"""
Objection Handling AI
Handles customer objections intelligently
"""

from typing import Dict, List, Optional, Any
from enum import Enum
import structlog
from openai import AsyncOpenAI
from config.settings import settings

logger = structlog.get_logger()


class ObjectionType(Enum):
    """Types of objections"""
    PRICE = "price"
    TIMING = "timing"
    NEED = "need"
    TRUST = "trust"
    COMPETITOR = "competitor"
    AUTHORITY = "authority"
    OTHER = "other"


class ObjectionHandler:
    """Objection handling system"""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
        self._objection_patterns: Dict[ObjectionType, List[str]] = {
            ObjectionType.PRICE: ["caro", "precio", "costoso", "barato", "económico"],
            ObjectionType.TIMING: ["ahora", "después", "esperar", "pronto", "más tarde"],
            ObjectionType.NEED: ["necesito", "no necesito", "no lo necesito"],
            ObjectionType.TRUST: ["confiar", "confianza", "seguro", "garantía"],
            ObjectionType.COMPETITOR: ["competencia", "otro", "alternativa"],
            ObjectionType.AUTHORITY: ["decidir", "jefe", "supervisor", "autorización"]
        }
        self._handling_strategies: Dict[ObjectionType, List[str]] = {
            ObjectionType.PRICE: [
                "Reframe value proposition",
                "Compare to alternatives",
                "Show ROI",
                "Offer payment plans"
            ],
            ObjectionType.TIMING: [
                "Create urgency",
                "Show opportunity cost",
                "Offer limited-time benefits"
            ],
            ObjectionType.NEED: [
                "Identify hidden needs",
                "Show future benefits",
                "Address pain points"
            ],
            ObjectionType.TRUST: [
                "Provide testimonials",
                "Show credentials",
                "Offer guarantees",
                "Share success stories"
            ],
            ObjectionType.COMPETITOR: [
                "Differentiate",
                "Highlight unique value",
                "Address specific concerns"
            ],
            ObjectionType.AUTHORITY: [
                "Provide information for decision maker",
                "Offer to speak with authority",
                "Create urgency for decision"
            ]
        }
    
    async def identify_objection(
        self,
        message: str,
        conversation_history: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Identify objection type and details"""
        
        message_lower = message.lower()
        
        # Check against patterns
        detected_types = []
        for obj_type, patterns in self._objection_patterns.items():
            if any(pattern in message_lower for pattern in patterns):
                detected_types.append(obj_type)
        
        # Use AI for more nuanced detection
        prompt = f"""
Analyze this message for sales objections.

Message: {message}
{"Conversation History: " + " ".join(conversation_history[-3:]) if conversation_history else ""}

Identify:
1. Objection type (price, timing, need, trust, competitor, authority, other)
2. Specific concern
3. Underlying reason
4. Confidence level

Respond with JSON:
{{
    "type": "price/timing/need/trust/competitor/authority/other",
    "concern": "specific concern",
    "reason": "underlying reason",
    "confidence": 0.0-1.0,
    "keywords": ["keyword1", "keyword2"]
}}
"""
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            
            result = eval(response.choices[0].message.content)
            
            # Use detected types if AI didn't find one
            if result.get("type") == "other" and detected_types:
                result["type"] = detected_types[0].value
            
            logger.info("Objection identified", objection_type=result.get("type"), confidence=result.get("confidence"))
            
            return result
            
        except Exception as e:
            logger.error("Objection identification error", error=str(e))
            return {
                "type": detected_types[0].value if detected_types else "other",
                "concern": message,
                "reason": "unknown",
                "confidence": 0.5,
                "error": str(e)
            }
    
    async def handle_objection(
        self,
        objection: Dict[str, Any],
        conversation_history: List[str],
        customer_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate objection handling response"""
        
        objection_type = ObjectionType[objection.get("type", "other").upper()]
        strategies = self._handling_strategies.get(objection_type, [])
        
        prompt = f"""
You are a sales expert handling a customer objection.

Objection Type: {objection.get('type')}
Specific Concern: {objection.get('concern')}
Underlying Reason: {objection.get('reason')}

Recommended Strategies: {', '.join(strategies)}

Conversation History:
{chr(10).join(conversation_history[-5:])}

Customer Data: {customer_data if customer_data else "Not available"}

Generate a response that:
1. Acknowledges the objection empathetically
2. Addresses the specific concern
3. Reframes positively
4. Moves toward resolution

Response:
"""
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at handling sales objections."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=400
            )
            
            handling_response = response.choices[0].message.content.strip()
            
            logger.info("Objection handled", objection_type=objection_type.value)
            
            return {
                "response": handling_response,
                "strategy_used": strategies[0] if strategies else "general",
                "objection_type": objection_type.value,
                "next_steps": self._get_next_steps(objection_type)
            }
            
        except Exception as e:
            logger.error("Objection handling error", error=str(e))
            return {
                "response": "Entiendo tu preocupación. Déjame ayudarte a resolver esto.",
                "strategy_used": "fallback",
                "error": str(e)
            }
    
    def _get_next_steps(self, objection_type: ObjectionType) -> List[str]:
        """Get suggested next steps based on objection type"""
        steps = {
            ObjectionType.PRICE: [
                "Provide detailed pricing breakdown",
                "Show value comparison",
                "Offer payment options"
            ],
            ObjectionType.TIMING: [
                "Discuss timeline flexibility",
                "Show benefits of starting now",
                "Schedule follow-up"
            ],
            ObjectionType.NEED: [
                "Deep dive into needs",
                "Provide case studies",
                "Offer trial or demo"
            ],
            ObjectionType.TRUST: [
                "Share credentials and testimonials",
                "Provide guarantees",
                "Offer references"
            ],
            ObjectionType.COMPETITOR: [
                "Compare features",
                "Highlight differentiators",
                "Address specific concerns"
            ],
            ObjectionType.AUTHORITY: [
                "Prepare information packet",
                "Offer to speak with decision maker",
                "Provide ROI analysis"
            ]
        }
        
        return steps.get(objection_type, ["Continue conversation", "Address concerns"])
    
    async def handle_objection_flow(
        self,
        message: str,
        conversation_history: List[str],
        customer_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Complete objection handling flow"""
        # Identify objection
        objection = await self.identify_objection(message, conversation_history)
        
        # Handle objection
        handling = await self.handle_objection(objection, conversation_history, customer_data)
        
        return {
            "objection": objection,
            "handling": handling,
            "complete": True
        }
