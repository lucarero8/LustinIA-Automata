from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional

try:
    from openai import AsyncOpenAI  # type: ignore
except Exception:  # pragma: no cover
    AsyncOpenAI = None  # type: ignore

from config.settings import settings


class ScriptStage(Enum):
    GREETING = "greeting"
    QUALIFICATION = "qualification"
    PRESENTATION = "presentation"
    OBJECTION_HANDLING = "objection_handling"
    CLOSING = "closing"
    FOLLOW_UP = "follow_up"


class SalesScriptEngine:
    def __init__(self):
        self.client = (
            AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if (AsyncOpenAI and settings.OPENAI_API_KEY) else None
        )
        self.model = settings.OPENAI_MODEL

    async def get_response(
        self,
        user_message: str,
        conversation_history: List[str],
        session_id: str,
        customer_data: Optional[Dict[str, Any]] = None,
        current_stage: Optional[ScriptStage] = None,
    ) -> Dict[str, Any]:
        stage = current_stage or self._determine_stage(conversation_history)
        prompt = self._build_prompt(user_message, conversation_history, customer_data, stage)

        if not self.client:
            return {
                "response": f"[fallback:{stage.value}] Gracias. ¿Me cuentas un poco más para ayudarte mejor?",
                "stage": stage.value,
                "next_stage": self._next_stage(stage).value,
                "script_used": "fallback",
            }

        resp = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "Eres un agente de ventas profesional (ES)."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=250,
        )
        text = (resp.choices[0].message.content or "").strip()
        return {"response": text, "stage": stage.value, "next_stage": self._next_stage(stage).value, "script_used": "llm"}

    def _determine_stage(self, history: List[str]) -> ScriptStage:
        if not history:
            return ScriptStage.GREETING
        last = history[-1].lower()
        if any(w in last for w in ["precio", "cuesta", "coste"]):
            return ScriptStage.PRESENTATION
        if any(w in last for w in ["no", "pero", "caro", "duda"]):
            return ScriptStage.OBJECTION_HANDLING
        if any(w in last for w in ["comprar", "contratar", "pagar"]):
            return ScriptStage.CLOSING
        return ScriptStage.QUALIFICATION

    def _next_stage(self, stage: ScriptStage) -> ScriptStage:
        if stage == ScriptStage.GREETING:
            return ScriptStage.QUALIFICATION
        if stage == ScriptStage.QUALIFICATION:
            return ScriptStage.PRESENTATION
        if stage == ScriptStage.PRESENTATION:
            return ScriptStage.OBJECTION_HANDLING
        if stage == ScriptStage.OBJECTION_HANDLING:
            return ScriptStage.CLOSING
        if stage == ScriptStage.CLOSING:
            return ScriptStage.FOLLOW_UP
        return stage

    def _build_prompt(
        self, msg: str, history: List[str], customer_data: Optional[Dict[str, Any]], stage: ScriptStage
    ) -> str:
        hist = "\n".join(history[-6:])
        return f"""Etapa: {stage.value}
Cliente: {customer_data or {}}
Historial:
{hist}

Mensaje: {msg}

Responde en español, breve, empático y con una pregunta que avance la conversación."""

"""
Sales Script Engine
Manages and executes sales scripts
"""

from typing import Dict, List, Optional, Any
from enum import Enum
import structlog
from openai import AsyncOpenAI
from config.settings import settings

logger = structlog.get_logger()


class ScriptStage(Enum):
    """Sales script stages"""
    GREETING = "greeting"
    QUALIFICATION = "qualification"
    PRESENTATION = "presentation"
    OBJECTION_HANDLING = "objection_handling"
    CLOSING = "closing"
    FOLLOW_UP = "follow_up"


class SalesScriptEngine:
    """Sales script engine"""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
        self._scripts: Dict[str, Dict[str, Any]] = {}
        self._session_stage: Dict[str, ScriptStage] = {}
        self.auto_adapt = settings.SALES_SCRIPT_AUTO_ADAPT
    
    async def get_response(
        self,
        user_message: str,
        conversation_history: List[str],
        session_id: str,
        customer_data: Optional[Dict[str, Any]] = None,
        current_stage: Optional[ScriptStage] = None
    ) -> Dict[str, Any]:
        """Get sales script response"""
        
        # Determine current stage
        if not current_stage:
            current_stage = self._determine_stage(conversation_history, session_id)
        
        # Get script for stage
        script = self._get_script_for_stage(current_stage)
        
        # Build context
        context = self._build_context(
            conversation_history,
            customer_data,
            current_stage,
            script
        )
        
        # Generate response
        response = await self._generate_response(
            user_message,
            context,
            script,
            current_stage
        )
        
        # Update stage if needed
        next_stage = self._determine_next_stage(
            response,
            current_stage,
            conversation_history
        )
        
        if next_stage != current_stage:
            self._session_stage[session_id] = next_stage
            logger.info("Stage transition", session_id=session_id, from_stage=current_stage.value, to_stage=next_stage.value)
        
        return {
            "response": response,
            "stage": current_stage.value,
            "next_stage": next_stage.value,
            "script_used": script.get("name", "default")
        }
    
    def _determine_stage(
        self,
        conversation_history: List[str],
        session_id: str
    ) -> ScriptStage:
        """Determine current conversation stage"""
        # Check if we have a stored stage
        if session_id in self._session_stage:
            return self._session_stage[session_id]
        
        # Determine from history
        if len(conversation_history) == 0:
            return ScriptStage.GREETING
        
        # Simple heuristics (can be enhanced with ML)
        last_message = conversation_history[-1].lower()
        
        if any(word in last_message for word in ["hola", "buenos", "buenas"]):
            return ScriptStage.GREETING
        elif any(word in last_message for word in ["precio", "cuesta", "coste"]):
            return ScriptStage.PRESENTATION
        elif any(word in last_message for word in ["no", "pero", "sin embargo", "pero"]):
            return ScriptStage.OBJECTION_HANDLING
        elif any(word in last_message for word in ["comprar", "contratar", "adquirir"]):
            return ScriptStage.CLOSING
        else:
            return ScriptStage.QUALIFICATION
    
    def _get_script_for_stage(self, stage: ScriptStage) -> Dict[str, Any]:
        """Get script configuration for stage"""
        scripts = {
            ScriptStage.GREETING: {
                "name": "greeting",
                "tone": "friendly",
                "key_points": ["introduce", "ask_how_can_help"],
                "examples": [
                    "¡Hola! Bienvenido a [Empresa]. ¿En qué puedo ayudarte hoy?",
                    "Hola, gracias por contactarnos. ¿Cómo puedo asistirte?"
                ]
            },
            ScriptStage.QUALIFICATION: {
                "name": "qualification",
                "tone": "consultative",
                "key_points": ["understand_needs", "identify_pain_points"],
                "examples": [
                    "Para poder ayudarte mejor, ¿podrías contarme un poco sobre tu situación actual?",
                    "Entiendo. ¿Qué desafíos estás enfrentando actualmente?"
                ]
            },
            ScriptStage.PRESENTATION: {
                "name": "presentation",
                "tone": "informative",
                "key_points": ["highlight_benefits", "address_needs"],
                "examples": [
                    "Nuestro producto/servicio puede ayudarte con [beneficio específico].",
                    "Basándome en lo que me has contado, creo que [solución] sería perfecta para ti."
                ]
            },
            ScriptStage.OBJECTION_HANDLING: {
                "name": "objection_handling",
                "tone": "empathetic",
                "key_points": ["acknowledge", "address", "reframe"],
                "examples": [
                    "Entiendo tu preocupación. Déjame explicarte cómo abordamos eso.",
                    "Esa es una pregunta válida. Te explico cómo lo resolvemos."
                ]
            },
            ScriptStage.CLOSING: {
                "name": "closing",
                "tone": "confident",
                "key_points": ["summarize_benefits", "call_to_action"],
                "examples": [
                    "Perfecto. ¿Te parece bien si procedemos con [acción]?",
                    "Excelente. ¿Cuándo sería un buen momento para comenzar?"
                ]
            },
            ScriptStage.FOLLOW_UP: {
                "name": "follow_up",
                "tone": "professional",
                "key_points": ["check_in", "offer_assistance"],
                "examples": [
                    "Hola, quería seguir en contacto contigo. ¿Cómo va todo?",
                    "Solo quería asegurarme de que todo está bien. ¿Necesitas algo más?"
                ]
            }
        }
        
        return scripts.get(stage, scripts[ScriptStage.GREETING])
    
    def _build_context(
        self,
        conversation_history: List[str],
        customer_data: Optional[Dict[str, Any]],
        stage: ScriptStage,
        script: Dict[str, Any]
    ) -> str:
        """Build context for response generation"""
        context_parts = [
            f"Current Stage: {stage.value}",
            f"Script: {script.get('name')}",
            f"Tone: {script.get('tone')}",
            f"Key Points: {', '.join(script.get('key_points', []))}"
        ]
        
        if customer_data:
            context_parts.append(f"Customer Data: {customer_data}")
        
        if conversation_history:
            context_parts.append(f"Recent Conversation:\n" + "\n".join(conversation_history[-5:]))
        
        return "\n".join(context_parts)
    
    async def _generate_response(
        self,
        user_message: str,
        context: str,
        script: Dict[str, Any],
        stage: ScriptStage
    ) -> str:
        """Generate response using script"""
        
        prompt = f"""
You are a sales agent following a sales script.

Context:
{context}

User Message: {user_message}

Generate a response that:
1. Follows the script guidelines
2. Maintains the appropriate tone
3. Addresses the user's message
4. Moves the conversation forward

Response:
"""
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional sales agent."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=300
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error("Response generation error", error=str(e))
            # Fallback to script examples
            examples = script.get("examples", [])
            return examples[0] if examples else "Gracias por tu mensaje. ¿En qué puedo ayudarte?"
    
    def _determine_next_stage(
        self,
        response: str,
        current_stage: ScriptStage,
        conversation_history: List[str]
    ) -> ScriptStage:
        """Determine next stage based on response and history"""
        # Simple logic - can be enhanced
        if current_stage == ScriptStage.GREETING:
            return ScriptStage.QUALIFICATION
        elif current_stage == ScriptStage.QUALIFICATION:
            return ScriptStage.PRESENTATION
        elif current_stage == ScriptStage.OBJECTION_HANDLING:
            return ScriptStage.CLOSING
        elif current_stage == ScriptStage.CLOSING:
            return ScriptStage.FOLLOW_UP
        
        return current_stage
    
    def register_script(
        self,
        name: str,
        script: Dict[str, Any]
    ):
        """Register a custom script"""
        self._scripts[name] = script
        logger.info("Script registered", name=name)
    
    def get_script(self, name: str) -> Optional[Dict[str, Any]]:
        """Get registered script"""
        return self._scripts.get(name)
