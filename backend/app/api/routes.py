from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, BackgroundTasks, FastAPI
from fastapi.responses import JSONResponse
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from app.agent.react_agent import ReActAgent
import json
import asyncio

# Model for the start agent request
class StartAgentRequest(BaseModel):
    goal: str
    context: Optional[Dict[str, Any]] = {}

# Create router
router = APIRouter()

# Global variable to store the agent instance
agent_instance = None

def set_agent(agent):
    """Set the agent instance for use in the routes"""
    global agent_instance
    agent_instance = agent

def get_agent():
    """Get the agent instance for use in the routes"""
    global agent_instance
    if agent_instance is None:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    return agent_instance

# Routes
@router.post("/agent/start")
async def start_agent(request: StartAgentRequest, background_tasks: BackgroundTasks):
    """Start the agent with a goal"""
    agent = get_agent()
    try:
        # Start the agent in a background task
        background_tasks.add_task(agent.start, request.goal, request.context)
        return {"status": "started"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/agent/state")
async def get_agent_state():
    """Get the current state of the agent"""
    agent = get_agent()
    try:
        state = agent.get_state()
        return state
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/agent/stop")
async def stop_agent():
    """Stop the agent"""
    agent = get_agent()
    try:
        await agent.stop()
        return {"status": "stopped"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/agent/reset")
async def reset_agent():
    """Reset the agent state"""
    agent = get_agent()
    try:
        await agent.reset()
        return {"status": "reset"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket endpoint
@router.websocket("/agent/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    from app.api.websocket import handle_websocket_connection
    await handle_websocket_connection(websocket) 