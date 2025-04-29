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

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add routes
app.include_router(router)

# Initialize services and agent
def initialize_agent():
    # Get Gemini API key
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    
    if not gemini_api_key:
        logger.warning("GEMINI_API_KEY not found in environment. Using default key for development only.")
        # Fallback key for development - should be replaced in production
        gemini_api_key = "AIzaSyBvbXoT4gnSSv1anWXtOZx4z0mmOcTjvlQ"
    
    try:
        logger.info("Initializing LLM service")
        # Create LLM service
        llm_service = LLMService(
            api_key=gemini_api_key,
            model="gemini-1.5-pro"
        )
        
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

# Run the app if executed directly
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 