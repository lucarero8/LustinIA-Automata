from __future__ import annotations

import json
from typing import Any, Dict

try:
    import networkx as nx  # type: ignore
except Exception:  # pragma: no cover
    nx = None  # type: ignore

try:
    from openai import AsyncOpenAI  # type: ignore
except Exception:  # pragma: no cover
    AsyncOpenAI = None  # type: ignore

from config.settings import settings


class KnowledgeGraphIntegration:
    def __init__(self):
        self.graph = nx.DiGraph() if nx else None
        self.client = (
            AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if (AsyncOpenAI and settings.OPENAI_API_KEY) else None
        )
        self.model = settings.OPENAI_MODEL

    async def extract_and_link(self, text: str, session_id: str) -> Dict[str, Any]:
        if not self.client or not self.graph:
            return {"entities": [], "relationships": [], "note": "LLM/KG deps not configured"}

        prompt = f"""
Extrae entidades y relaciones del texto y devuelve JSON:
{{"entities":[{{"id":"e1","type":"...","properties":{{}}}}], "relationships":[{{"source":"e1","target":"e2","type":"...","properties":{{}}}}]}}

Texto: {text}
"""
        resp = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            response_format={"type": "json_object"},
        )
        data = json.loads(resp.choices[0].message.content or "{}")

        for ent in data.get("entities", []) or []:
            self.graph.add_node(ent.get("id"), type=ent.get("type"), **(ent.get("properties") or {}))
        for rel in data.get("relationships", []) or []:
            self.graph.add_edge(
                rel.get("source"),
                rel.get("target"),
                type=rel.get("type"),
                **(rel.get("properties") or {}),
            )
        return data

"""
Knowledge Graph Integration
Integrates with knowledge graphs for enhanced understanding
"""

from typing import Dict, List, Optional, Any, Tuple
import structlog
import networkx as nx
from datetime import datetime
from openai import AsyncOpenAI
from config.settings import settings

logger = structlog.get_logger()


class KnowledgeGraphIntegration:
    """Knowledge graph integration system"""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
        self.graph = nx.DiGraph()
        self._entity_cache: Dict[str, Dict[str, Any]] = {}
        self._connected = False
    
    async def initialize(self):
        """Initialize knowledge graph"""
        try:
            # Load existing graph if available
            # For now, start with empty graph
            self._connected = True
            logger.info("Knowledge graph initialized")
        except Exception as e:
            logger.error("Knowledge graph initialization error", error=str(e))
            self._connected = False
    
    async def cleanup(self):
        """Cleanup knowledge graph"""
        self.graph.clear()
        self._connected = False
        logger.info("Knowledge graph cleaned up")
    
    def is_connected(self) -> bool:
        """Check if knowledge graph is connected"""
        return self._connected
    
    async def add_entity(
        self,
        entity_id: str,
        entity_type: str,
        properties: Dict[str, Any]
    ):
        """Add entity to knowledge graph"""
        self.graph.add_node(entity_id, type=entity_type, **properties)
        self._entity_cache[entity_id] = {"type": entity_type, **properties}
        
        logger.debug("Entity added", entity_id=entity_id, entity_type=entity_type)
    
    async def add_relationship(
        self,
        source_id: str,
        target_id: str,
        relationship_type: str,
        properties: Optional[Dict[str, Any]] = None
    ):
        """Add relationship to knowledge graph"""
        if source_id not in self.graph:
            await self.add_entity(source_id, "unknown", {})
        if target_id not in self.graph:
            await self.add_entity(target_id, "unknown", {})
        
        self.graph.add_edge(
            source_id,
            target_id,
            type=relationship_type,
            **(properties or {})
        )
        
        logger.debug(
            "Relationship added",
            source=source_id,
            target=target_id,
            type=relationship_type
        )
    
    async def query_entity(
        self,
        entity_id: str
    ) -> Optional[Dict[str, Any]]:
        """Query entity from knowledge graph"""
        if entity_id not in self.graph:
            return None
        
        node_data = self.graph.nodes[entity_id]
        
        # Get neighbors
        neighbors = list(self.graph.neighbors(entity_id))
        relationships = []
        for neighbor in neighbors:
            edge_data = self.graph.edges[entity_id, neighbor]
            relationships.append({
                "target": neighbor,
                "type": edge_data.get("type", "unknown"),
                "properties": {k: v for k, v in edge_data.items() if k != "type"}
            })
        
        return {
            "id": entity_id,
            "properties": node_data,
            "relationships": relationships,
            "neighbor_count": len(neighbors)
        }
    
    async def find_path(
        self,
        source_id: str,
        target_id: str,
        max_depth: int = 5
    ) -> Optional[List[str]]:
        """Find path between entities"""
        try:
            if source_id not in self.graph or target_id not in self.graph:
                return None
            
            path = nx.shortest_path(self.graph, source_id, target_id)
            return path if len(path) <= max_depth + 1 else None
        except nx.NetworkXNoPath:
            return None
    
    async def extract_and_link(
        self,
        text: str,
        session_id: str
    ) -> Dict[str, Any]:
        """Extract entities and relationships from text and link to graph"""
        
        prompt = f"""
Extract entities and relationships from the following text.

Text: {text}

Provide JSON with:
1. Entities (id, type, properties)
2. Relationships (source, target, type, properties)

Format:
{{
    "entities": [
        {{"id": "entity1", "type": "person", "properties": {{"name": "John"}}}}
    ],
    "relationships": [
        {{"source": "entity1", "target": "entity2", "type": "knows", "properties": {{}}}}
    ]
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
            
            # Add to graph
            for entity in result.get("entities", []):
                await self.add_entity(
                    entity["id"],
                    entity["type"],
                    entity.get("properties", {})
                )
            
            for rel in result.get("relationships", []):
                await self.add_relationship(
                    rel["source"],
                    rel["target"],
                    rel["type"],
                    rel.get("properties", {})
                )
            
            logger.info(
                "Entities extracted and linked",
                entities_count=len(result.get("entities", [])),
                relationships_count=len(result.get("relationships", []))
            )
            
            return result
            
        except Exception as e:
            logger.error("Entity extraction error", error=str(e))
            return {"entities": [], "relationships": [], "error": str(e)}
    
    async def get_subgraph(
        self,
        entity_id: str,
        depth: int = 2
    ) -> Dict[str, Any]:
        """Get subgraph around an entity"""
        if entity_id not in self.graph:
            return {"nodes": [], "edges": []}
        
        # Get nodes within depth
        nodes = {entity_id}
        current_level = {entity_id}
        
        for _ in range(depth):
            next_level = set()
            for node in current_level:
                neighbors = list(self.graph.neighbors(node))
                next_level.update(neighbors)
            nodes.update(next_level)
            current_level = next_level
        
        # Get subgraph
        subgraph = self.graph.subgraph(nodes)
        
        # Convert to dict format
        nodes_data = [
            {"id": n, **self.graph.nodes[n]}
            for n in subgraph.nodes()
        ]
        
        edges_data = [
            {
                "source": u,
                "target": v,
                "type": subgraph.edges[u, v].get("type", "unknown"),
                **{k: v for k, v in subgraph.edges[u, v].items() if k != "type"}
            }
            for u, v in subgraph.edges()
        ]
        
        return {
            "nodes": nodes_data,
            "edges": edges_data,
            "center": entity_id
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get knowledge graph statistics"""
        return {
            "node_count": self.graph.number_of_nodes(),
            "edge_count": self.graph.number_of_edges(),
            "is_connected": self._connected,
            "density": nx.density(self.graph) if self.graph.number_of_nodes() > 0 else 0
        }
