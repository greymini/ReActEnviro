from pydantic import BaseModel
from typing import Dict, List, Optional, Any

class StartAgentRequest(BaseModel):
    goal: str
    context: Optional[Dict[str, Any]] = {}

class AgentUpdateEvent(BaseModel):
    event_type: str  # "thought_added", "tool_started", "tool_completed", "goal_completed", etc.
    data: Dict[str, Any]
    
class AgentStateResponse(BaseModel):
    goals: List[Dict[str, Any]]
    thoughts: List[Dict[str, Any]]
    tool_calls: List[Dict[str, Any]]
    status: str
    error: Optional[str] = None 