from __future__ import annotations

import json
from typing import Any, Dict, List, Tuple

import logging

try:
    from openai import AsyncOpenAI  # type: ignore
except Exception:  # pragma: no cover
    AsyncOpenAI = None  # type: ignore

from config.settings import settings

logger = logging.getLogger("icarusiav2.guardrails")


class ABCDGuardrail:
    """
    ABCD:
      A: Accuracy
      B: Bias
      C: Compliance
      D: Danger
    """

    def __init__(self):
        self.client = (
            AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if (AsyncOpenAI and settings.OPENAI_API_KEY) else None
        )
        self.model = settings.OPENAI_MODEL

    async def validate(self, text: str, context: Dict[str, Any]) -> Tuple[bool, str, List[str]]:
        if not self.client:
            return True, "safe", []

        prompt = f"""
Valida el texto según ABCD (accuracy/bias/compliance/danger).
Devuelve JSON con: violated(true/false), level(safe|warning|blocked|critical), reasons([..]).

Contexto: {context}
Texto: {text}
"""
        try:
            resp = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                response_format={"type": "json_object"},
            )
            raw = resp.choices[0].message.content or "{}"
            data = json.loads(raw)
            violated = bool(data.get("violated", False))
            level = str(data.get("level", "safe"))
            reasons = data.get("reasons", []) or []
            is_valid = not violated and level in ("safe", "warning")
            return is_valid, level, [str(r) for r in reasons]
        except Exception as e:
            logger.exception("guardrail_error")
            return True, "warning", ["Guardrail check failed; allowing by fallback"]

"""
ABCD Cognitive Guardrails
A: Accuracy, B: Bias, C: Compliance, D: Danger
"""

from typing import Dict, List, Optional, Tuple
from enum import Enum
import structlog
from openai import AsyncOpenAI
from config.settings import settings

logger = structlog.get_logger()


class GuardrailLevel(Enum):
    """Guardrail severity levels"""
    SAFE = "safe"
    WARNING = "warning"
    BLOCKED = "blocked"
    CRITICAL = "critical"


class ABCDGuardrail:
    """ABCD Cognitive Guardrails System"""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
        
        # Predefined rules
        self.rules = {
            "accuracy": [
                "Do not make unsubstantiated claims",
                "Do not provide false information",
                "Verify facts before stating them"
            ],
            "bias": [
                "Avoid discriminatory language",
                "Do not stereotype",
                "Treat all individuals equally"
            ],
            "compliance": [
                "Follow legal regulations",
                "Respect privacy laws",
                "Do not engage in illegal activities"
            ],
            "danger": [
                "Do not encourage harmful behavior",
                "Do not provide dangerous instructions",
                "Prioritize safety"
            ]
        }
    
    async def validate(
        self,
        text: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, GuardrailLevel, List[str]]:
        """
        Validate text against ABCD guardrails
        Returns: (is_valid, level, violations)
        """
        violations = []
        
        # Check each category
        accuracy_check = await self._check_accuracy(text, context)
        bias_check = await self._check_bias(text, context)
        compliance_check = await self._check_compliance(text, context)
        danger_check = await self._check_danger(text, context)
        
        if accuracy_check["violated"]:
            violations.extend(accuracy_check["reasons"])
        if bias_check["violated"]:
            violations.extend(bias_check["reasons"])
        if compliance_check["violated"]:
            violations.extend(compliance_check["reasons"])
        if danger_check["violated"]:
            violations.extend(danger_check["reasons"])
        
        # Determine severity level
        if danger_check["violated"]:
            level = GuardrailLevel.CRITICAL
        elif compliance_check["violated"]:
            level = GuardrailLevel.BLOCKED
        elif bias_check["violated"] or accuracy_check["violated"]:
            level = GuardrailLevel.WARNING
        else:
            level = GuardrailLevel.SAFE
        
        is_valid = level in [GuardrailLevel.SAFE, GuardrailLevel.WARNING]
        
        logger.info(
            "Guardrail validation",
            is_valid=is_valid,
            level=level.value,
            violations_count=len(violations)
        )
        
        return is_valid, level, violations
    
    async def _check_accuracy(
        self,
        text: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, any]:
        """Check accuracy guardrails"""
        prompt = f"""
Analyze the following text for accuracy violations:
- Unsubstantiated claims
- False information
- Unverified facts

Text: {text}

Respond with JSON:
{{"violated": true/false, "reasons": ["reason1", "reason2"]}}
"""
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            result = eval(response.choices[0].message.content)
            return result
        except:
            return {"violated": False, "reasons": []}
    
    async def _check_bias(
        self,
        text: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, any]:
        """Check bias guardrails"""
        prompt = f"""
Analyze the following text for bias violations:
- Discriminatory language
- Stereotypes
- Unequal treatment

Text: {text}

Respond with JSON:
{{"violated": true/false, "reasons": ["reason1", "reason2"]}}
"""
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            result = eval(response.choices[0].message.content)
            return result
        except:
            return {"violated": False, "reasons": []}
    
    async def _check_compliance(
        self,
        text: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, any]:
        """Check compliance guardrails"""
        prompt = f"""
Analyze the following text for compliance violations:
- Legal regulations
- Privacy laws
- Illegal activities

Text: {text}

Respond with JSON:
{{"violated": true/false, "reasons": ["reason1", "reason2"]}}
"""
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            result = eval(response.choices[0].message.content)
            return result
        except:
            return {"violated": False, "reasons": []}
    
    async def _check_danger(
        self,
        text: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, any]:
        """Check danger guardrails"""
        prompt = f"""
Analyze the following text for danger violations:
- Harmful behavior encouragement
- Dangerous instructions
- Safety risks

Text: {text}

Respond with JSON:
{{"violated": true/false, "reasons": ["reason1", "reason2"]}}
"""
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            result = eval(response.choices[0].message.content)
            return result
        except:
            return {"violated": False, "reasons": []}
    
    def get_rules(self) -> Dict[str, List[str]]:
        """Get all guardrail rules"""
        return self.rules
    
    def add_rule(self, category: str, rule: str):
        """Add a custom rule"""
        if category not in self.rules:
            self.rules[category] = []
        self.rules[category].append(rule)
        logger.info("Rule added", category=category, rule=rule)
