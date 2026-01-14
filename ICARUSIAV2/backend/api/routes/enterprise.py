from __future__ import annotations

from datetime import timedelta
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException

from enterprise.analytics.dashboard import AnalyticsDashboard
from enterprise.crm.integration import CRMIntegration
from enterprise.orchestration.coordinator import MultiAgentCoordinator

router = APIRouter()


@router.get("/analytics/dashboard")
async def get_dashboard(time_range_hours: Optional[int] = 24):
    dash = AnalyticsDashboard()
    tr = timedelta(hours=time_range_hours) if time_range_hours else None
    return dash.get_dashboard_data(time_range=tr)


@router.get("/agents/status")
async def get_agent_status():
    coord = MultiAgentCoordinator()
    return coord.get_agent_status()


@router.post("/crm/sync")
async def sync_to_crm(crm_type: str, lead_data: Dict[str, Any]):
    crm = CRMIntegration()
    lead_id = await crm.sync_lead(crm_type=crm_type, lead_data=lead_data)
    if not lead_id:
        raise HTTPException(status_code=400, detail="Failed to sync lead")
    return {"lead_id": lead_id}

"""Enterprise API routes"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

router = APIRouter()


@router.get("/analytics/dashboard")
async def get_dashboard(time_range_hours: Optional[int] = 24):
    """Get analytics dashboard data"""
    from enterprise.analytics.dashboard import AnalyticsDashboard
    from datetime import timedelta
    
    dashboard = AnalyticsDashboard()
    time_range = timedelta(hours=time_range_hours) if time_range_hours else None
    data = dashboard.get_dashboard_data(time_range)
    return data


@router.get("/analytics/funnel")
async def get_funnel(time_range_hours: Optional[int] = 24):
    """Get conversion funnel"""
    from enterprise.analytics.dashboard import AnalyticsDashboard
    from datetime import timedelta
    
    dashboard = AnalyticsDashboard()
    time_range = timedelta(hours=time_range_hours) if time_range_hours else None
    funnel = dashboard.get_conversion_funnel(time_range)
    return funnel


@router.post("/crm/sync")
async def sync_to_crm(crm_type: str, lead_data: Dict[str, Any]):
    """Sync lead to CRM"""
    from enterprise.crm.integration import CRMIntegration
    
    crm = CRMIntegration()
    lead_id = await crm.sync_lead(crm_type, lead_data)
    if not lead_id:
        raise HTTPException(status_code=400, detail="Failed to sync lead")
    return {"lead_id": lead_id}


@router.get("/agents/status")
async def get_agent_status():
    """Get multi-agent status"""
    from enterprise.orchestration.coordinator import MultiAgentCoordinator
    
    coordinator = MultiAgentCoordinator()
    status = coordinator.get_agent_status()
    return status
