from __future__ import annotations

from enum import Enum
from typing import Any, Dict

import logging

try:
    from openai import AsyncOpenAI  # type: ignore
except Exception:  # pragma: no cover
    AsyncOpenAI = None  # type: ignore

from config.settings import settings

logger = logging.getLogger("icarusiav2.reasoning")


class ReasoningType(Enum):
    DEDUCTIVE = "deductive"
    INDUCTIVE = "inductive"
    ABDUCTIVE = "abductive"
    ANALOGICAL = "analogical"
    CAUSAL = "causal"


class VerbalReasoningEngine:
    def __init__(self):
        self.client = (
            AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if (AsyncOpenAI and settings.OPENAI_API_KEY) else None
        )
        self.model = settings.OPENAI_MODEL
        self.max_depth = settings.MAX_REASONING_DEPTH

    async def reason(
        self,
        query: str,
        context: Dict[str, Any],
        reasoning_type: ReasoningType = ReasoningType.DEDUCTIVE,
        depth: int = 0,
    ) -> Dict[str, Any]:
        if depth >= self.max_depth:
            return {"conclusion": "Maximum reasoning depth reached", "confidence": 0.5, "reasoning_steps": []}

        if not self.client:
            # fallback (sin OpenAI key)
            return {
                "conclusion": f"[fallback] {query}",
                "confidence": 0.2,
                "reasoning_steps": ["No OPENAI_API_KEY configured"],
                "reasoning_type": reasoning_type.value,
                "depth": depth,
            }

        prompt = self._build_prompt(query, context, reasoning_type)

        try:
            resp = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Eres un motor de razonamiento verbal. Responde claro y estructurado."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_tokens=700,
            )
            text = (resp.choices[0].message.content or "").strip()
            return {
                "conclusion": text[:400],
                "confidence": 0.7,
                "reasoning_steps": [],
                "reasoning_type": reasoning_type.value,
                "depth": depth,
                "full_response": text,
            }
        except Exception as e:
            logger.exception("reasoning_error")
            return {"conclusion": "Reasoning failed", "confidence": 0.0, "reasoning_steps": [], "error": str(e)}

    def _build_prompt(self, query: str, context: Dict[str, Any], reasoning_type: ReasoningType) -> str:
        ctx = "\n".join([f"{k}: {v}" for k, v in (context or {}).items()])
        return f"""Tipo: {reasoning_type.value}

Contexto:
{ctx}

Consulta: {query}

Devuelve: premisas, pasos, conclusión y una recomendación accionable."""

"""
Verbal Reasoning Engine
Advanced verbal reasoning with multi-step logic chains
"""

from typing import Dict, List, Optional, Any
from enum import Enum
import structlog
from openai import AsyncOpenAI
from config.settings import settings

logger = structlog.get_logger()


class ReasoningType(Enum):
    """Types of reasoning operations"""
    DEDUCTIVE = "deductive"
    INDUCTIVE = "inductive"
    ABDUCTIVE = "abductive"
    ANALOGICAL = "analogical"
    CAUSAL = "causal"


class VerbalReasoningEngine:
    """Advanced verbal reasoning engine"""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
        self.max_depth = settings.MAX_REASONING_DEPTH
        self._reasoning_cache: Dict[str, Any] = {}
    
    async def reason(
        self,
        query: str,
        context: Dict[str, Any],
        reasoning_type: ReasoningType = ReasoningType.DEDUCTIVE,
        depth: int = 0
    ) -> Dict[str, Any]:
        """Perform verbal reasoning on a query"""
        
        if depth >= self.max_depth:
            logger.warning("Max reasoning depth reached", depth=depth)
            return {
                "conclusion": "Maximum reasoning depth reached",
                "confidence": 0.5,
                "reasoning_steps": []
            }
        
        cache_key = f"{query}_{reasoning_type.value}_{hash(str(context))}"
        if cache_key in self._reasoning_cache:
            logger.debug("Using cached reasoning result")
            return self._reasoning_cache[cache_key]
        
        reasoning_prompt = self._build_reasoning_prompt(query, context, reasoning_type)
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt(reasoning_type)
                    },
                    {
                        "role": "user",
                        "content": reasoning_prompt
                    }
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            result = self._parse_reasoning_response(response.choices[0].message.content)
            result["reasoning_type"] = reasoning_type.value
            result["depth"] = depth
            
            # Cache result
            self._reasoning_cache[cache_key] = result
            
            logger.info(
                "Reasoning completed",
                reasoning_type=reasoning_type.value,
                depth=depth,
                confidence=result.get("confidence", 0)
            )
            
            return result
            
        except Exception as e:
            logger.error("Reasoning error", error=str(e))
            return {
                "conclusion": "Reasoning failed",
                "confidence": 0.0,
                "reasoning_steps": [],
                "error": str(e)
            }
    
    def _build_reasoning_prompt(
        self,
        query: str,
        context: Dict[str, Any],
        reasoning_type: ReasoningType
    ) -> str:
        """Build reasoning prompt"""
        context_str = "\n".join([f"{k}: {v}" for k, v in context.items()])
        
        prompts = {
            ReasoningType.DEDUCTIVE: f"""
Given the following premises and context, apply deductive reasoning to reach a conclusion.

Context:
{context_str}

Query: {query}

Provide:
1. Premises identified
2. Logical steps
3. Conclusion
4. Confidence level (0-1)
""",
            ReasoningType.INDUCTIVE: f"""
Given the following observations and context, apply inductive reasoning to form a general conclusion.

Context:
{context_str}

Query: {query}

Provide:
1. Observations identified
2. Pattern recognition
3. General conclusion
4. Confidence level (0-1)
""",
            ReasoningType.ABDUCTIVE: f"""
Given the following observations and context, apply abductive reasoning to find the best explanation.

Context:
{context_str}

Query: {query}

Provide:
1. Observations
2. Possible explanations
3. Best explanation (most likely)
4. Confidence level (0-1)
""",
            ReasoningType.ANALOGICAL: f"""
Given the following query and context, apply analogical reasoning by finding similar cases.

Context:
{context_str}

Query: {query}

Provide:
1. Similar cases/analogies
2. Mapping between cases
3. Inferred conclusion
4. Confidence level (0-1)
""",
            ReasoningType.CAUSAL: f"""
Given the following query and context, apply causal reasoning to identify cause-effect relationships.

Context:
{context_str}

Query: {query}

Provide:
1. Causal factors identified
2. Causal chain
3. Predicted outcome
4. Confidence level (0-1)
"""
        }
        
        return prompts.get(reasoning_type, prompts[ReasoningType.DEDUCTIVE])
    
    def _get_system_prompt(self, reasoning_type: ReasoningType) -> str:
        """Get system prompt for reasoning type"""
        prompts = {
            ReasoningType.DEDUCTIVE: "You are an expert in deductive reasoning. Apply strict logical rules.",
            ReasoningType.INDUCTIVE: "You are an expert in inductive reasoning. Identify patterns and generalize.",
            ReasoningType.ABDUCTIVE: "You are an expert in abductive reasoning. Find the best explanation.",
            ReasoningType.ANALOGICAL: "You are an expert in analogical reasoning. Find and apply analogies.",
            ReasoningType.CAUSAL: "You are an expert in causal reasoning. Identify cause-effect relationships."
        }
        return prompts.get(reasoning_type, prompts[ReasoningType.DEDUCTIVE])
    
    def _parse_reasoning_response(self, response: str) -> Dict[str, Any]:
        """Parse reasoning response from LLM"""
        # Simple parsing - can be enhanced with structured output
        lines = response.split("\n")
        conclusion = ""
        confidence = 0.5
        reasoning_steps = []
        
        for line in lines:
            if "conclusion" in line.lower():
                conclusion = line.split(":", 1)[-1].strip()
            elif "confidence" in line.lower():
                try:
                    confidence = float(line.split(":")[-1].strip())
                except:
                    pass
            elif line.strip().startswith(("1.", "2.", "3.", "4.", "-")):
                reasoning_steps.append(line.strip())
        
        return {
            "conclusion": conclusion or response[:200],
            "confidence": confidence,
            "reasoning_steps": reasoning_steps,
            "full_response": response
        }
    
    def is_ready(self) -> bool:
        """Check if reasoning engine is ready"""
        return self.client is not None and settings.OPENAI_API_KEY is not None
