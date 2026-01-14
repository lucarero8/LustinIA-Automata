from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class Breadcrumb:
    id: str
    session_id: str
    timestamp: datetime
    module: str
    action: str
    context: Dict[str, Any] = field(default_factory=dict)
    result: Optional[Any] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "session_id": self.session_id,
            "timestamp": self.timestamp.isoformat(),
            "module": self.module,
            "action": self.action,
            "context": self.context,
            "result": self.result,
        }


class BreadcrumbsNavigator:
    def __init__(self):
        self._breadcrumbs: Dict[str, List[Breadcrumb]] = {}

    def add_breadcrumb(
        self,
        session_id: str,
        module: str,
        action: str,
        context: Optional[Dict[str, Any]] = None,
        result: Optional[Any] = None,
    ) -> Breadcrumb:
        b = Breadcrumb(
            id=f"{session_id}_{len(self._breadcrumbs.get(session_id, []))}",
            session_id=session_id,
            timestamp=datetime.utcnow(),
            module=module,
            action=action,
            context=context or {},
            result=result,
        )
        self._breadcrumbs.setdefault(session_id, []).append(b)
        return b

    def get_trail(self, session_id: str, module: Optional[str] = None, limit: Optional[int] = None) -> List[Breadcrumb]:
        trail = self._breadcrumbs.get(session_id, [])
        if module:
            trail = [b for b in trail if b.module == module]
        if limit is not None:
            trail = trail[-limit:]
        return trail

"""
Breadcrumbs Navigator
Navigation system for decision trails
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, field
import structlog

logger = structlog.get_logger()


@dataclass
class Breadcrumb:
    """Represents a breadcrumb in the decision trail"""
    id: str
    session_id: str
    timestamp: datetime
    module: str
    action: str
    context: Dict[str, Any] = field(default_factory=dict)
    result: Optional[Any] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class BreadcrumbsNavigator:
    """Navigates breadcrumb trails"""
    
    def __init__(self):
        self._breadcrumbs: Dict[str, List[Breadcrumb]] = {}
        self._index: Dict[str, List[str]] = {}  # module -> breadcrumb_ids
    
    def add_breadcrumb(
        self,
        session_id: str,
        module: str,
        action: str,
        context: Optional[Dict[str, Any]] = None,
        result: Optional[Any] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Breadcrumb:
        """Add a new breadcrumb"""
        breadcrumb = Breadcrumb(
            id=f"{session_id}_{len(self._breadcrumbs.get(session_id, []))}",
            session_id=session_id,
            timestamp=datetime.now(),
            module=module,
            action=action,
            context=context or {},
            result=result,
            metadata=metadata or {}
        )
        
        if session_id not in self._breadcrumbs:
            self._breadcrumbs[session_id] = []
        
        self._breadcrumbs[session_id].append(breadcrumb)
        
        # Index by module
        if module not in self._index:
            self._index[module] = []
        self._index[module].append(breadcrumb.id)
        
        logger.debug(
            "Breadcrumb added",
            session_id=session_id,
            module=module,
            action=action
        )
        
        return breadcrumb
    
    def get_trail(
        self,
        session_id: str,
        module: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Breadcrumb]:
        """Get breadcrumb trail for a session"""
        breadcrumbs = self._breadcrumbs.get(session_id, [])
        
        if module:
            breadcrumbs = [b for b in breadcrumbs if b.module == module]
        
        if limit:
            breadcrumbs = breadcrumbs[-limit:]
        
        return breadcrumbs
    
    def get_trail_summary(
        self,
        session_id: str
    ) -> Dict[str, Any]:
        """Get summary of breadcrumb trail"""
        breadcrumbs = self._breadcrumbs.get(session_id, [])
        
        if not breadcrumbs:
            return {"total": 0, "modules": {}, "timeline": []}
        
        # Count by module
        module_counts = {}
        for breadcrumb in breadcrumbs:
            module_counts[breadcrumb.module] = module_counts.get(breadcrumb.module, 0) + 1
        
        # Create timeline
        timeline = [
            {
                "timestamp": str(b.timestamp),
                "module": b.module,
                "action": b.action
            }
            for b in breadcrumbs[-20:]  # Last 20
        ]
        
        return {
            "total": len(breadcrumbs),
            "modules": module_counts,
            "timeline": timeline,
            "first": str(breadcrumbs[0].timestamp) if breadcrumbs else None,
            "last": str(breadcrumbs[-1].timestamp) if breadcrumbs else None
        }
    
    def search_trail(
        self,
        session_id: str,
        query: str,
        module: Optional[str] = None
    ) -> List[Breadcrumb]:
        """Search breadcrumb trail"""
        breadcrumbs = self.get_trail(session_id, module)
        
        # Simple text search
        query_lower = query.lower()
        results = []
        
        for breadcrumb in breadcrumbs:
            if (query_lower in breadcrumb.action.lower() or
                query_lower in str(breadcrumb.context).lower() or
                query_lower in str(breadcrumb.result).lower()):
                results.append(breadcrumb)
        
        return results
    
    def get_module_history(
        self,
        module: str,
        limit: int = 50
    ) -> List[Breadcrumb]:
        """Get history for a specific module across all sessions"""
        all_breadcrumbs = []
        for session_breadcrumbs in self._breadcrumbs.values():
            for breadcrumb in session_breadcrumbs:
                if breadcrumb.module == module:
                    all_breadcrumbs.append(breadcrumb)
        
        # Sort by timestamp
        all_breadcrumbs.sort(key=lambda x: x.timestamp)
        
        return all_breadcrumbs[-limit:]
    
    def clear_session(self, session_id: str):
        """Clear breadcrumbs for a session"""
        if session_id in self._breadcrumbs:
            # Remove from index
            for breadcrumb in self._breadcrumbs[session_id]:
                if breadcrumb.module in self._index:
                    if breadcrumb.id in self._index[breadcrumb.module]:
                        self._index[breadcrumb.module].remove(breadcrumb.id)
            
            del self._breadcrumbs[session_id]
        
        logger.debug("Breadcrumbs cleared", session_id=session_id)
