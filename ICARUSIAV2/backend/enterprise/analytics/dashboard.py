from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from config.settings import settings


class AnalyticsDashboard:
    def __init__(self):
        self._events: list[dict[str, Any]] = []
        self._metrics: dict[str, list[dict[str, Any]]] = defaultdict(list)
        self.update_interval = settings.ANALYTICS_UPDATE_INTERVAL

    def track_event(self, event_type: str, session_id: str, data: Optional[Dict[str, Any]] = None) -> None:
        ev = {"type": event_type, "session_id": session_id, "timestamp": datetime.utcnow(), "data": data or {}}
        self._events.append(ev)
        self._metrics[event_type].append(ev)

    def get_metrics(self, time_range: Optional[timedelta] = None) -> Dict[str, Any]:
        cutoff = datetime.utcnow() - (time_range or timedelta(hours=24))
        events = [e for e in self._events if e["timestamp"] > cutoff]
        by_type: dict[str, int] = defaultdict(int)
        by_session: dict[str, int] = defaultdict(int)
        for e in events:
            by_type[e["type"]] += 1
            by_session[e["session_id"]] += 1
        return {"total_events": len(events), "events_by_type": dict(by_type), "unique_sessions": len(by_session)}

    def get_dashboard_data(self, time_range: Optional[timedelta] = None) -> Dict[str, Any]:
        return {"metrics": self.get_metrics(time_range=time_range), "timestamp": datetime.utcnow().isoformat()}

"""
Real-time Analytics Dashboard
Provides real-time analytics and metrics
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import structlog
from collections import defaultdict
from config.settings import settings

logger = structlog.get_logger()


class AnalyticsDashboard:
    """Real-time analytics dashboard"""
    
    def __init__(self):
        self._metrics: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self._events: List[Dict[str, Any]] = []
        self.update_interval = settings.ANALYTICS_UPDATE_INTERVAL
        self._initialized = False
    
    async def initialize(self):
        """Initialize analytics dashboard"""
        self._initialized = True
        logger.info("Analytics dashboard initialized")
    
    def is_ready(self) -> bool:
        """Check if dashboard is ready"""
        return self._initialized
    
    def track_event(
        self,
        event_type: str,
        session_id: str,
        data: Optional[Dict[str, Any]] = None
    ):
        """Track an event"""
        event = {
            "type": event_type,
            "session_id": session_id,
            "timestamp": datetime.now(),
            "data": data or {}
        }
        
        self._events.append(event)
        self._metrics[event_type].append(event)
        
        # Keep only recent events (last 10000)
        if len(self._events) > 10000:
            self._events = self._events[-10000:]
        
        logger.debug("Event tracked", event_type=event_type, session_id=session_id)
    
    def get_metrics(
        self,
        metric_type: Optional[str] = None,
        time_range: Optional[timedelta] = None
    ) -> Dict[str, Any]:
        """Get metrics"""
        cutoff = datetime.now() - (time_range or timedelta(hours=24))
        
        if metric_type:
            events = [
                e for e in self._metrics.get(metric_type, [])
                if e["timestamp"] > cutoff
            ]
        else:
            events = [
                e for e in self._events
                if e["timestamp"] > cutoff
            ]
        
        # Calculate basic metrics
        by_type = defaultdict(int)
        by_session = defaultdict(int)
        
        for event in events:
            by_type[event["type"]] += 1
            by_session[event["session_id"]] += 1
        
        return {
            "total_events": len(events),
            "events_by_type": dict(by_type),
            "unique_sessions": len(by_session),
            "time_range": str(time_range or timedelta(hours=24))
        }
    
    def get_conversion_funnel(
        self,
        time_range: Optional[timedelta] = None
    ) -> Dict[str, Any]:
        """Get conversion funnel metrics"""
        cutoff = datetime.now() - (time_range or timedelta(hours=24))
        
        events = [e for e in self._events if e["timestamp"] > cutoff]
        
        # Define funnel stages
        stages = {
            "greeting": 0,
            "qualification": 0,
            "presentation": 0,
            "objection": 0,
            "closing": 0,
            "conversion": 0
        }
        
        for event in events:
            event_type = event["type"].lower()
            if "greeting" in event_type:
                stages["greeting"] += 1
            elif "qualification" in event_type:
                stages["qualification"] += 1
            elif "presentation" in event_type:
                stages["presentation"] += 1
            elif "objection" in event_type:
                stages["objection"] += 1
            elif "closing" in event_type:
                stages["closing"] += 1
            elif "conversion" in event_type or "sale" in event_type:
                stages["conversion"] += 1
        
        # Calculate conversion rates
        conversion_rates = {}
        prev_count = stages["greeting"]
        for stage, count in stages.items():
            if prev_count > 0:
                conversion_rates[stage] = (count / prev_count) * 100
            else:
                conversion_rates[stage] = 0
            prev_count = count
        
        return {
            "stages": stages,
            "conversion_rates": conversion_rates,
            "overall_conversion": conversion_rates.get("conversion", 0)
        }
    
    def get_performance_metrics(
        self,
        time_range: Optional[timedelta] = None
    ) -> Dict[str, Any]:
        """Get performance metrics"""
        cutoff = datetime.now() - (time_range or timedelta(hours=24))
        
        events = [e for e in self._events if e["timestamp"] > cutoff]
        
        # Calculate response times (if available in event data)
        response_times = [
            e["data"].get("response_time", 0)
            for e in events
            if "response_time" in e.get("data", {})
        ]
        
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        # Calculate success rates
        success_events = [e for e in events if e.get("data", {}).get("success", False)]
        success_rate = (len(success_events) / len(events) * 100) if events else 0
        
        return {
            "total_events": len(events),
            "average_response_time": avg_response_time,
            "success_rate": success_rate,
            "events_per_hour": len(events) / max((time_range or timedelta(hours=24)).total_seconds() / 3600, 1)
        }
    
    def get_dashboard_data(
        self,
        time_range: Optional[timedelta] = None
    ) -> Dict[str, Any]:
        """Get complete dashboard data"""
        return {
            "metrics": self.get_metrics(time_range=time_range),
            "funnel": self.get_conversion_funnel(time_range=time_range),
            "performance": self.get_performance_metrics(time_range=time_range),
            "timestamp": datetime.now().isoformat()
        }
