from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import logging

logger = logging.getLogger("icarusiav2.anchor_points")


@dataclass
class AnchorPoint:
    id: str
    objective: str
    constraints: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    priority: int = 5
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "objective": self.objective,
            "constraints": self.constraints,
            "context": self.context,
            "priority": self.priority,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class AnchorPointManager:
    def __init__(self):
        self._anchors: Dict[str, List[AnchorPoint]] = {}
        self._active: Dict[str, AnchorPoint] = {}

    def create_anchor(
        self,
        session_id: str,
        objective: str,
        constraints: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None,
        priority: int = 5,
    ) -> AnchorPoint:
        anchor = AnchorPoint(
            id=f"{session_id}_{len(self._anchors.get(session_id, []))}",
            objective=objective,
            constraints=constraints or [],
            context=context or {},
            priority=priority,
        )
        self._anchors.setdefault(session_id, []).append(anchor)
        self._active[session_id] = anchor
        logger.info("anchor_created session_id=%s anchor_id=%s", session_id, anchor.id)
        return anchor

    def get_active_anchor(self, session_id: str) -> Optional[AnchorPoint]:
        return self._active.get(session_id)

    def validate_against_anchors(
        self, session_id: str, proposed_action: str, context: Dict[str, Any]
    ) -> Tuple[bool, Optional[str]]:
        anchor = self.get_active_anchor(session_id)
        if not anchor:
            return True, None

        for c in anchor.constraints:
            if c.lower() in proposed_action.lower():
                return False, f"Violates constraint: {c}"

        # lightweight alignment check
        obj = set(anchor.objective.lower().split())
        act = set(proposed_action.lower().split())
        alignment = len(obj & act) / max(len(obj), 1)
        if alignment < 0.2:
            return False, "Low alignment with objective"
        return True, None

"""
Anchor Points Manager
Manages objectives, goals, and constraints for conversations
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import structlog

logger = structlog.get_logger()


@dataclass
class AnchorPoint:
    """Represents an anchor point in a conversation"""
    id: str
    objective: str
    constraints: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    priority: int = 5  # 1-10 scale
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


class AnchorPointManager:
    """Manages anchor points for conversations"""
    
    def __init__(self):
        self._anchors: Dict[str, List[AnchorPoint]] = {}
        self._active_anchors: Dict[str, AnchorPoint] = {}
    
    def create_anchor(
        self,
        session_id: str,
        objective: str,
        constraints: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None,
        priority: int = 5
    ) -> AnchorPoint:
        """Create a new anchor point"""
        anchor = AnchorPoint(
            id=f"{session_id}_{len(self._anchors.get(session_id, []))}",
            objective=objective,
            constraints=constraints or [],
            context=context or {},
            priority=priority
        )
        
        if session_id not in self._anchors:
            self._anchors[session_id] = []
        
        self._anchors[session_id].append(anchor)
        self._active_anchors[session_id] = anchor
        
        logger.info(
            "Anchor point created",
            session_id=session_id,
            anchor_id=anchor.id,
            objective=objective
        )
        
        return anchor
    
    def get_active_anchor(self, session_id: str) -> Optional[AnchorPoint]:
        """Get the active anchor point for a session"""
        return self._active_anchors.get(session_id)
    
    def update_anchor(
        self,
        session_id: str,
        anchor_id: str,
        objective: Optional[str] = None,
        constraints: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None,
        priority: Optional[int] = None
    ) -> Optional[AnchorPoint]:
        """Update an existing anchor point"""
        anchors = self._anchors.get(session_id, [])
        for anchor in anchors:
            if anchor.id == anchor_id:
                if objective:
                    anchor.objective = objective
                if constraints is not None:
                    anchor.constraints = constraints
                if context:
                    anchor.context.update(context)
                if priority is not None:
                    anchor.priority = priority
                anchor.updated_at = datetime.now()
                
                logger.info("Anchor point updated", session_id=session_id, anchor_id=anchor_id)
                return anchor
        
        return None
    
    def get_anchor_history(self, session_id: str) -> List[AnchorPoint]:
        """Get all anchor points for a session"""
        return self._anchors.get(session_id, [])
    
    def validate_against_anchors(
        self,
        session_id: str,
        proposed_action: str,
        context: Dict[str, Any]
    ) -> tuple[bool, Optional[str]]:
        """Validate if a proposed action aligns with anchor points"""
        anchor = self.get_active_anchor(session_id)
        if not anchor:
            return True, None
        
        # Check constraints
        for constraint in anchor.constraints:
            if constraint.lower() in proposed_action.lower():
                return False, f"Violates constraint: {constraint}"
        
        # Check objective alignment
        objective_keywords = set(anchor.objective.lower().split())
        action_keywords = set(proposed_action.lower().split())
        
        alignment_score = len(objective_keywords.intersection(action_keywords)) / max(len(objective_keywords), 1)
        
        if alignment_score < 0.3:
            return False, "Low alignment with objective"
        
        return True, None
    
    def clear_session(self, session_id: str):
        """Clear all anchor points for a session"""
        if session_id in self._anchors:
            del self._anchors[session_id]
        if session_id in self._active_anchors:
            del self._active_anchors[session_id]
        
        logger.info("Session anchors cleared", session_id=session_id)
