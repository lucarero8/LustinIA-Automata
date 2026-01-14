from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from core.modules.anchor_points.manager import AnchorPointManager
from core.modules.guardrails.abcd import ABCDGuardrail
from core.modules.reasoning.verbal_reasoning import ReasoningType, VerbalReasoningEngine

router = APIRouter()


class ReasoningRequest(BaseModel):
    query: str
    context: Dict[str, Any] = {}
    reasoning_type: str = "deductive"


class AnchorPointRequest(BaseModel):
    session_id: str
    objective: str
    constraints: Optional[List[str]] = None
    context: Optional[Dict[str, Any]] = None
    priority: int = 5


@router.post("/reasoning")
async def perform_reasoning(request: ReasoningRequest):
    engine = VerbalReasoningEngine()
    rt = request.reasoning_type.upper()
    reasoning_type = ReasoningType[rt] if rt in ReasoningType.__members__ else ReasoningType.DEDUCTIVE
    return await engine.reason(request.query, request.context, reasoning_type)


@router.post("/anchor-points")
async def create_anchor_point(request: AnchorPointRequest):
    manager = AnchorPointManager()
    anchor = manager.create_anchor(
        session_id=request.session_id,
        objective=request.objective,
        constraints=request.constraints,
        context=request.context,
        priority=request.priority,
    )
    return {"anchor": anchor.to_dict()}


@router.get("/anchor-points/{session_id}")
async def get_anchor_point(session_id: str):
    manager = AnchorPointManager()
    anchor = manager.get_active_anchor(session_id)
    if not anchor:
        raise HTTPException(status_code=404, detail="No anchor point found")
    return {"anchor": anchor.to_dict()}


@router.post("/guardrails/validate")
async def validate_guardrails(text: str, context: Optional[Dict[str, Any]] = None):
    guardrail = ABCDGuardrail()
    is_valid, level, violations = await guardrail.validate(text, context or {})
    return {"is_valid": is_valid, "level": level, "violations": violations}

"""Cognitive API routes"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

router = APIRouter()


class ReasoningRequest(BaseModel):
    query: str
    context: Dict[str, Any]
    reasoning_type: Optional[str] = "deductive"


class AnchorPointRequest(BaseModel):
    session_id: str
    objective: str
    constraints: Optional[List[str]] = None
    context: Optional[Dict[str, Any]] = None
    priority: int = 5


@router.post("/reasoning")
async def perform_reasoning(request: ReasoningRequest):
    """Perform verbal reasoning"""
    # Import here to avoid circular imports
    from core.modules.reasoning.verbal_reasoning import VerbalReasoningEngine, ReasoningType
    
    engine = VerbalReasoningEngine()
    reasoning_type = ReasoningType[request.reasoning_type.upper()] if hasattr(ReasoningType, request.reasoning_type.upper()) else ReasoningType.DEDUCTIVE
    
    result = await engine.reason(request.query, request.context, reasoning_type)
    return result


@router.post("/anchor-points")
async def create_anchor_point(request: AnchorPointRequest):
    """Create anchor point"""
    from core.modules.anchor_points.manager import AnchorPointManager
    
    manager = AnchorPointManager()
    anchor = manager.create_anchor(
        request.session_id,
        request.objective,
        request.constraints,
        request.context,
        request.priority
    )
    return {"anchor": anchor}


@router.get("/anchor-points/{session_id}")
async def get_anchor_point(session_id: str):
    """Get active anchor point"""
    from core.modules.anchor_points.manager import AnchorPointManager
    
    manager = AnchorPointManager()
    anchor = manager.get_active_anchor(session_id)
    if not anchor:
        raise HTTPException(status_code=404, detail="No anchor point found")
    return {"anchor": anchor}


@router.post("/guardrails/validate")
async def validate_guardrails(text: str, context: Optional[Dict[str, Any]] = None):
    """Validate text against guardrails"""
    from core.modules.guardrails.abcd import ABCDGuardrail
    
    guardrail = ABCDGuardrail()
    is_valid, level, violations = await guardrail.validate(text, context)
    return {
        "is_valid": is_valid,
        "level": level.value,
        "violations": violations
    }
