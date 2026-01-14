from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter
from pydantic import BaseModel

from knowledge.breadcrumbs.navigator import BreadcrumbsNavigator
from knowledge.kgraph.integration import KnowledgeGraphIntegration
from knowledge.memory.manager import MemoryManager, MemoryType

router = APIRouter()


class MemoryRequest(BaseModel):
    session_id: str
    content: Any
    memory_type: str = "short_term"
    importance: float = 0.5


@router.post("/memory/store")
async def store_memory(request: MemoryRequest):
    manager = MemoryManager()
    mt = request.memory_type.upper()
    memory_type = MemoryType[mt] if mt in MemoryType.__members__ else MemoryType.SHORT_TERM
    memory_id = await manager.store(
        session_id=request.session_id,
        content=request.content,
        memory_type=memory_type,
        importance=request.importance,
    )
    return {"memory_id": memory_id}


@router.get("/memory/{session_id}")
async def retrieve_memory(session_id: str, query: Optional[str] = None, limit: int = 10):
    manager = MemoryManager()
    memories = await manager.retrieve(session_id=session_id, query=query, limit=limit)
    return {"memories": memories}


@router.get("/breadcrumbs/{session_id}")
async def get_breadcrumbs(session_id: str, module: Optional[str] = None, limit: int = 100):
    nav = BreadcrumbsNavigator()
    trail = nav.get_trail(session_id=session_id, module=module, limit=limit)
    return {"breadcrumbs": [b.to_dict() for b in trail]}


@router.post("/kgraph/extract")
async def extract_entities(text: str, session_id: str):
    kg = KnowledgeGraphIntegration()
    return await kg.extract_and_link(text=text, session_id=session_id)

"""Knowledge API routes"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

router = APIRouter()


class MemoryRequest(BaseModel):
    session_id: str
    content: Any
    memory_type: str = "short_term"
    importance: float = 0.5


@router.post("/memory/store")
async def store_memory(request: MemoryRequest):
    """Store memory"""
    from knowledge.memory.manager import MemoryManager, MemoryType
    
    manager = MemoryManager()
    memory_type = MemoryType[request.memory_type.upper()]
    memory_id = await manager.store(
        request.session_id,
        request.content,
        memory_type,
        importance=request.importance
    )
    return {"memory_id": memory_id}


@router.get("/memory/{session_id}")
async def retrieve_memory(session_id: str, query: Optional[str] = None, limit: int = 10):
    """Retrieve memories"""
    from knowledge.memory.manager import MemoryManager
    
    manager = MemoryManager()
    memories = await manager.retrieve(session_id, query, limit=limit)
    return {"memories": memories}


@router.get("/breadcrumbs/{session_id}")
async def get_breadcrumbs(session_id: str, module: Optional[str] = None):
    """Get breadcrumb trail"""
    from knowledge.breadcrumbs.navigator import BreadcrumbsNavigator
    
    navigator = BreadcrumbsNavigator()
    trail = navigator.get_trail(session_id, module)
    return {"breadcrumbs": trail}


@router.post("/kgraph/extract")
async def extract_entities(text: str, session_id: str):
    """Extract entities and link to knowledge graph"""
    from knowledge.kgraph.integration import KnowledgeGraphIntegration
    
    kgraph = KnowledgeGraphIntegration()
    result = await kgraph.extract_and_link(text, session_id)
    return result
