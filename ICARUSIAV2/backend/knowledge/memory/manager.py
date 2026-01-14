from __future__ import annotations

from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

from config.settings import settings


class MemoryType(Enum):
    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    WORKING = "working"


class MemoryManager:
    def __init__(self):
        self._memories: Dict[str, List[Dict[str, Any]]] = {}
        self.retention_days = settings.MEMORY_RETENTION_DAYS

    async def store(
        self,
        session_id: str,
        content: Any,
        memory_type: MemoryType = MemoryType.SHORT_TERM,
        metadata: Optional[Dict[str, Any]] = None,
        importance: float = 0.5,
    ) -> str:
        mem_id = f"{session_id}_{len(self._memories.get(session_id, []))}"
        mem = {
            "id": mem_id,
            "session_id": session_id,
            "content": content,
            "type": memory_type.value,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {},
            "importance": float(importance),
        }
        self._memories.setdefault(session_id, []).append(mem)
        return mem_id

    async def retrieve(self, session_id: str, query: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        items = list(self._memories.get(session_id, []))
        if query:
            q = query.lower()
            items = [m for m in items if q in str(m.get("content", "")).lower() or q in str(m.get("metadata", "")).lower()]
        items.sort(key=lambda m: (m.get("importance", 0), m.get("timestamp", "")), reverse=True)
        return items[:limit]

    async def cleanup(self) -> int:
        cutoff = datetime.utcnow() - timedelta(days=self.retention_days)
        removed = 0
        for sid, memories in list(self._memories.items()):
            kept = []
            for m in memories:
                try:
                    ts = datetime.fromisoformat(m.get("timestamp", ""))
                except Exception:
                    ts = datetime.utcnow()
                if ts >= cutoff:
                    kept.append(m)
                else:
                    removed += 1
            self._memories[sid] = kept
        return removed

"""
Memory Management System
Manages short-term and long-term memory
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from enum import Enum
import structlog
import json
from config.settings import settings

logger = structlog.get_logger()


class MemoryType(Enum):
    """Types of memory"""
    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    WORKING = "working"


class MemoryManager:
    """Memory management system"""
    
    def __init__(self):
        self._memories: Dict[str, List[Dict[str, Any]]] = {}
        self._session_memory: Dict[str, Dict[str, Any]] = {}
        self.retention_days = settings.MEMORY_RETENTION_DAYS
        self._initialized = False
    
    async def initialize(self):
        """Initialize memory manager"""
        try:
            # Load persistent memories if available
            self._initialized = True
            logger.info("Memory manager initialized")
        except Exception as e:
            logger.error("Memory manager initialization error", error=str(e))
    
    async def cleanup(self):
        """Cleanup memory manager"""
        # Clean up old memories
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        
        for session_id, memories in self._memories.items():
            self._memories[session_id] = [
                m for m in memories
                if datetime.fromisoformat(m.get("timestamp", "")) > cutoff_date
            ]
        
        logger.info("Memory manager cleaned up")
    
    def is_healthy(self) -> bool:
        """Check if memory manager is healthy"""
        return self._initialized
    
    async def store(
        self,
        session_id: str,
        content: Any,
        memory_type: MemoryType = MemoryType.SHORT_TERM,
        metadata: Optional[Dict[str, Any]] = None,
        importance: float = 0.5
    ) -> str:
        """Store a memory"""
        memory_id = f"{session_id}_{len(self._memories.get(session_id, []))}"
        
        memory = {
            "id": memory_id,
            "session_id": session_id,
            "content": content,
            "type": memory_type.value,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {},
            "importance": importance,
            "access_count": 0,
            "last_accessed": datetime.now().isoformat()
        }
        
        if session_id not in self._memories:
            self._memories[session_id] = []
        
        self._memories[session_id].append(memory)
        
        # Update session memory summary
        if session_id not in self._session_memory:
            self._session_memory[session_id] = {
                "total_memories": 0,
                "last_updated": datetime.now().isoformat()
            }
        self._session_memory[session_id]["total_memories"] += 1
        self._session_memory[session_id]["last_updated"] = datetime.now().isoformat()
        
        logger.debug(
            "Memory stored",
            session_id=session_id,
            memory_id=memory_id,
            memory_type=memory_type.value
        )
        
        return memory_id
    
    async def retrieve(
        self,
        session_id: str,
        query: Optional[str] = None,
        memory_type: Optional[MemoryType] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Retrieve memories"""
        memories = self._memories.get(session_id, [])
        
        # Filter by type
        if memory_type:
            memories = [m for m in memories if m["type"] == memory_type.value]
        
        # Filter by query (simple text search)
        if query:
            query_lower = query.lower()
            memories = [
                m for m in memories
                if query_lower in str(m["content"]).lower() or
                   query_lower in str(m["metadata"]).lower()
            ]
        
        # Sort by importance and recency
        memories.sort(
            key=lambda x: (
                x["importance"],
                datetime.fromisoformat(x["timestamp"])
            ),
            reverse=True
        )
        
        # Update access counts
        for memory in memories[:limit]:
            memory["access_count"] = memory.get("access_count", 0) + 1
            memory["last_accessed"] = datetime.now().isoformat()
        
        return memories[:limit]
    
    async def consolidate(
        self,
        session_id: str
    ) -> Dict[str, Any]:
        """Consolidate memories (move important short-term to long-term)"""
        memories = self._memories.get(session_id, [])
        
        short_term = [m for m in memories if m["type"] == MemoryType.SHORT_TERM.value]
        
        # Find high-importance short-term memories
        important = [m for m in short_term if m["importance"] > 0.7]
        
        # Convert to long-term
        converted = 0
        for memory in important:
            memory["type"] = MemoryType.LONG_TERM.value
            converted += 1
        
        logger.info(
            "Memories consolidated",
            session_id=session_id,
            converted=converted
        )
        
        return {
            "converted": converted,
            "remaining_short_term": len(short_term) - converted
        }
    
    async def forget(
        self,
        session_id: str,
        memory_id: Optional[str] = None,
        memory_type: Optional[MemoryType] = None
    ) -> int:
        """Forget memories"""
        memories = self._memories.get(session_id, [])
        
        if memory_id:
            # Remove specific memory
            self._memories[session_id] = [
                m for m in memories if m["id"] != memory_id
            ]
            return 1
        elif memory_type:
            # Remove all memories of type
            before = len(memories)
            self._memories[session_id] = [
                m for m in memories if m["type"] != memory_type.value
            ]
            return before - len(self._memories[session_id])
        else:
            # Clear all memories for session
            count = len(memories)
            self._memories[session_id] = []
            return count
    
    def get_memory_stats(self, session_id: str) -> Dict[str, Any]:
        """Get memory statistics for a session"""
        memories = self._memories.get(session_id, [])
        
        if not memories:
            return {"total": 0, "by_type": {}}
        
        by_type = {}
        for memory in memories:
            mtype = memory["type"]
            by_type[mtype] = by_type.get(mtype, 0) + 1
        
        avg_importance = sum(m.get("importance", 0) for m in memories) / len(memories)
        
        return {
            "total": len(memories),
            "by_type": by_type,
            "average_importance": avg_importance,
            "session_summary": self._session_memory.get(session_id, {})
        }
