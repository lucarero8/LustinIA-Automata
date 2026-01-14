"""
ICARUSIAV2 - FastAPI entrypoint
"""

from __future__ import annotations

from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config.settings import settings


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("icarusiav2")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("starting app=%s version=%s", settings.APP_NAME, settings.VERSION)
    yield
    logger.info("stopping app=%s version=%s", settings.APP_NAME, settings.VERSION)


app = FastAPI(
    title="ICARUSIAV2 - Advanced Sales AI",
    version=settings.VERSION,
    description="Next-generation Sales AI with cognitive modules",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("unhandled_exception path=%s", str(request.url.path))
    return JSONResponse(status_code=500, content={"error": "Internal server error"})


@app.get("/")
async def root():
    return {"status": "online", "system": settings.APP_NAME, "version": settings.VERSION}


@app.get("/health")
async def health():
    return {"status": "healthy"}


from api.routes import cognitive, enterprise, knowledge, sales  # noqa: E402

app.include_router(cognitive.router, prefix=f"{settings.API_V1_PREFIX}/cognitive", tags=["Cognitive"])
app.include_router(knowledge.router, prefix=f"{settings.API_V1_PREFIX}/knowledge", tags=["Knowledge"])
app.include_router(sales.router, prefix=f"{settings.API_V1_PREFIX}/sales", tags=["Sales"])
app.include_router(enterprise.router, prefix=f"{settings.API_V1_PREFIX}/enterprise", tags=["Enterprise"])

"""
ICARUSIAV2 - Main Application Entry Point
Advanced Sales AI System with Cognitive Capabilities
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import structlog
from contextlib import asynccontextmanager

from core.modules.reasoning.verbal_reasoning import VerbalReasoningEngine
from core.modules.guardrails.abcd import ABCDGuardrail
from core.modules.anchor_points.manager import AnchorPointManager
from core.modules.parallel_decoding.engine import ParallelDecodingEngine
from core.modules.coreference.resolver import CoreferenceResolver
from core.modules.thread_rot.detector import ThreadRotDetector
from core.modules.classification.active_classifier import ActiveClassifier
from core.modules.self_refinement.loop import SelfRefinementLoop

from knowledge.inner_thoughts.processor import InnerThoughtsProcessor
from knowledge.breadcrumbs.navigator import BreadcrumbsNavigator
from knowledge.kgraph.integration import KnowledgeGraphIntegration
from knowledge.memory.manager import MemoryManager
from knowledge.manual_refresh.controller import ManualRefreshController

from sales.webhooks.twilio_handler import TwilioWebhookHandler
from sales.whatsapp.api import WhatsAppAPI
from sales.scripts.engine import SalesScriptEngine
from sales.objections.handler import ObjectionHandler
from sales.tts.synthesizer import TTSSynthesizer
from sales.stt.recognizer import STTRecognizer

from enterprise.crm.integration import CRMIntegration
from enterprise.erp.integration import ERPIntegration
from enterprise.wais.framework import WAISFramework
from enterprise.orchestration.coordinator import MultiAgentCoordinator
from enterprise.analytics.dashboard import AnalyticsDashboard
from enterprise.feedback.loop import FeedbackLearningLoop

from config.settings import Settings

# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.make_filtering_bound_logger(log_level="INFO"),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=False,
)

logger = structlog.get_logger()

# Global settings
settings = Settings()

# Initialize core components
reasoning_engine = VerbalReasoningEngine()
guardrails = ABCDGuardrail()
anchor_manager = AnchorPointManager()
parallel_decoder = ParallelDecodingEngine()
coreference_resolver = CoreferenceResolver()
thread_rot_detector = ThreadRotDetector()
active_classifier = ActiveClassifier()
self_refinement = SelfRefinementLoop()

# Initialize knowledge system
inner_thoughts = InnerThoughtsProcessor()
breadcrumbs = BreadcrumbsNavigator()
kgraph = KnowledgeGraphIntegration()
memory_manager = MemoryManager()
manual_refresh = ManualRefreshController()

# Initialize sales agent
tts = TTSSynthesizer()
stt = STTRecognizer()
twilio_handler = TwilioWebhookHandler()
whatsapp_api = WhatsAppAPI()
sales_scripts = SalesScriptEngine()
objection_handler = ObjectionHandler()

# Initialize enterprise
crm = CRMIntegration()
erp = ERPIntegration()
wais = WAISFramework()
orchestrator = MultiAgentCoordinator()
analytics = AnalyticsDashboard()
feedback_loop = FeedbackLearningLoop()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle management for the application"""
    logger.info("Starting ICARUSIAV2", version="2.0.0")
    
    # Initialize all systems
    await memory_manager.initialize()
    await kgraph.initialize()
    await analytics.initialize()
    
    yield
    
    # Cleanup
    logger.info("Shutting down ICARUSIAV2")
    await memory_manager.cleanup()
    await kgraph.cleanup()


app = FastAPI(
    title="ICARUSIAV2 - Advanced Sales AI",
    version="2.0.0",
    description="Next-generation Sales AI with advanced cognitive capabilities",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error("Unhandled exception", exc_info=exc, path=request.url.path)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "version": "2.0.0",
        "system": "ICARUSIAV2"
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "components": {
            "reasoning_engine": reasoning_engine.is_ready(),
            "memory_manager": memory_manager.is_healthy(),
            "knowledge_graph": kgraph.is_connected(),
            "analytics": analytics.is_ready()
        }
    }


# Include routers
from api.routes import sales, knowledge, enterprise, cognitive

app.include_router(cognitive.router, prefix="/api/v1/cognitive", tags=["Cognitive"])
app.include_router(knowledge.router, prefix="/api/v1/knowledge", tags=["Knowledge"])
app.include_router(sales.router, prefix="/api/v1/sales", tags=["Sales"])
app.include_router(enterprise.router, prefix="/api/v1/enterprise", tags=["Enterprise"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )
