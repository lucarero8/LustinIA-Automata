from __future__ import annotations

from typing import Any, Dict


class MultiAgentCoordinator:
    def __init__(self):
        self._agents: Dict[str, Dict[str, Any]] = {}

    def get_agent_status(self) -> Dict[str, Any]:
        return {"total_agents": len(self._agents), "agents": self._agents}

"""
Multi-Agent Orchestration Coordinator
Coordinates multiple AI agents
"""

from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import structlog
import asyncio
from datetime import datetime

logger = structlog.get_logger()


class AgentRole(Enum):
    """Agent roles"""
    SALES = "sales"
    SUPPORT = "support"
    QUALIFICATION = "qualification"
    CLOSING = "closing"
    FOLLOW_UP = "follow_up"


class MultiAgentCoordinator:
    """Multi-agent orchestration coordinator"""
    
    def __init__(self):
        self._agents: Dict[str, Dict[str, Any]] = {}
        self._active_sessions: Dict[str, Dict[str, Any]] = {}
        self._routing_rules: Dict[str, Callable] = {}
    
    def register_agent(
        self,
        agent_id: str,
        role: AgentRole,
        handler: Callable,
        capabilities: List[str]
    ):
        """Register an agent"""
        self._agents[agent_id] = {
            "id": agent_id,
            "role": role.value,
            "handler": handler,
            "capabilities": capabilities,
            "active": True,
            "load": 0
        }
        
        logger.info("Agent registered", agent_id=agent_id, role=role.value)
    
    async def route_request(
        self,
        session_id: str,
        request: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Route request to appropriate agent"""
        
        # Determine which agent to use
        agent_id = self._select_agent(request, context)
        
        if not agent_id:
            logger.warning("No agent available", session_id=session_id)
            return {"error": "No agent available"}
        
        agent = self._agents[agent_id]
        
        # Update session tracking
        if session_id not in self._active_sessions:
            self._active_sessions[session_id] = {
                "current_agent": agent_id,
                "history": [],
                "started_at": datetime.now()
            }
        
        self._active_sessions[session_id]["current_agent"] = agent_id
        self._active_sessions[session_id]["history"].append({
            "agent": agent_id,
            "timestamp": datetime.now(),
            "request": request
        })
        
        # Route to agent
        try:
            agent["load"] += 1
            response = await agent["handler"](request, context)
            agent["load"] -= 1
            
            logger.info("Request routed", session_id=session_id, agent_id=agent_id)
            
            return {
                "agent_id": agent_id,
                "response": response,
                "success": True
            }
            
        except Exception as e:
            agent["load"] -= 1
            logger.error("Agent handling error", agent_id=agent_id, error=str(e))
            return {
                "agent_id": agent_id,
                "error": str(e),
                "success": False
            }
    
    def _select_agent(
        self,
        request: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> Optional[str]:
        """Select appropriate agent"""
        # Simple routing logic - can be enhanced
        
        # Check for explicit agent in request
        if "agent_id" in request:
            if request["agent_id"] in self._agents:
                return request["agent_id"]
        
        # Route based on request type
        request_type = request.get("type", "general")
        
        # Find agents with matching capabilities
        suitable_agents = []
        for agent_id, agent in self._agents.items():
            if not agent["active"]:
                continue
            
            if request_type in agent["capabilities"]:
                suitable_agents.append((agent_id, agent))
        
        if not suitable_agents:
            # Fallback to any available agent
            suitable_agents = [
                (aid, agent) for aid, agent in self._agents.items()
                if agent["active"]
            ]
        
        if not suitable_agents:
            return None
        
        # Select agent with lowest load
        suitable_agents.sort(key=lambda x: x[1]["load"])
        return suitable_agents[0][0]
    
    async def orchestrate_workflow(
        self,
        session_id: str,
        workflow: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Orchestrate multi-step workflow"""
        results = []
        
        for step in workflow:
            agent_id = step.get("agent_id")
            if not agent_id or agent_id not in self._agents:
                results.append({"error": f"Agent {agent_id} not found"})
                continue
            
            agent = self._agents[agent_id]
            
            try:
                result = await agent["handler"](step.get("request", {}), step.get("context"))
                results.append({
                    "step": step.get("name", "unknown"),
                    "agent": agent_id,
                    "result": result,
                    "success": True
                })
            except Exception as e:
                results.append({
                    "step": step.get("name", "unknown"),
                    "agent": agent_id,
                    "error": str(e),
                    "success": False
                })
        
        return {
            "session_id": session_id,
            "workflow_results": results,
            "success_count": sum(1 for r in results if r.get("success")),
            "total_steps": len(workflow)
        }
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents"""
        return {
            "total_agents": len(self._agents),
            "active_agents": sum(1 for a in self._agents.values() if a["active"]),
            "agents": {
                aid: {
                    "role": agent["role"],
                    "active": agent["active"],
                    "load": agent["load"],
                    "capabilities": agent["capabilities"]
                }
                for aid, agent in self._agents.items()
            }
        }
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session information"""
        return self._active_sessions.get(session_id)
