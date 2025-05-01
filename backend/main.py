import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router, set_agent
from app.api.websocket import setup_agent_websocket
from app.agent.llm_service import LLMService
from app.agent.tool_orchestrator import ToolOrchestrator
from app.agent.react_agent import ReActAgent
from app.tools.tool_registry import ToolRegistry
from app.tools.specialized.environmental_assessment import (
    SiteAnalysisTool, 
    RegulatoryComplianceTool,
    AirQualityAssessmentTool,
    HydrologicalAssessmentTool,
    WaterQualityAssessmentTool
)
import os
import logging
from dotenv import load_dotenv
from prometheus_client import make_asgi_app
import time
from app.metrics import http_requests_total, request_duration

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Environmental Impact Assessment ReAct Agent")

# Add Prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# Middleware to track request duration
@app.middleware("http")
async def track_requests(request, call_next):
    method = request.method
    path = request.url.path
    
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    status = response.status_code
    http_requests_total.labels(method=method, endpoint=path, status=status).inc()
    request_duration.labels(method=method, endpoint=path).observe(duration)
    
    return response

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Add routes
app.include_router(router)

# Initialize services and agent
def initialize_agent():
    try:
        logger.info("Initializing LLM service")
        # Create LLM service using environment variables
        llm_service = LLMService()
        
        logger.info("Setting up tool registry")
        # Create tool registry and register tools
        tool_registry = ToolRegistry()
        
        # Register environmental assessment tools
        tool_registry.register_tool(SiteAnalysisTool())
        tool_registry.register_tool(RegulatoryComplianceTool())
        tool_registry.register_tool(AirQualityAssessmentTool())
        tool_registry.register_tool(HydrologicalAssessmentTool())
        tool_registry.register_tool(WaterQualityAssessmentTool())
        
        logger.info("Creating tool orchestrator")
        # Create tool orchestrator
        tool_orchestrator = ToolOrchestrator(tool_registry)
        
        logger.info("Initializing ReAct agent")
        # Create ReAct agent
        agent = ReActAgent(llm_service, tool_orchestrator)
        
        return agent
    except Exception as e:
        logger.error(f"Error initializing agent: {str(e)}", exc_info=True)
        raise

# Startup event to initialize the agent
@app.on_event("startup")
async def startup_event():
    try:
        logger.info("Starting up application")
        # Create agent instance
        agent = initialize_agent()
        
        # Set the agent instance in the routes
        set_agent(agent)
        
        # Setup WebSocket connection for the agent
        setup_agent_websocket(agent)
        logger.info("Application startup complete")
    except Exception as e:
        logger.error(f"Startup error: {str(e)}", exc_info=True)
        # We can't raise an exception here as it would prevent the app from starting
        # but we log it so it's visible

# Get server configuration from environment
host = os.getenv("HOST", "0.0.0.0")
port = int(os.getenv("PORT", "8000"))
debug = os.getenv("DEBUG", "true").lower() == "true"

# Run the app if executed directly
if __name__ == "__main__":
    uvicorn.run("main:app", host=host, port=port, reload=debug) 