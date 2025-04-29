from typing import Dict, List, Optional, Union, Literal, Any
from pydantic import BaseModel, ConfigDict
from datetime import datetime
import uuid

class ThoughtStep(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    id: str = None
    content: str
    timestamp: float = None
    parent_id: Optional[str] = None
    
    def __init__(self, **data):
        if 'id' not in data or data['id'] is None:
            data['id'] = uuid.uuid4().hex
        if 'timestamp' not in data or data['timestamp'] is None:
            data['timestamp'] = datetime.now().timestamp()
        super().__init__(**data)

class ToolCall(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    id: str = None
    tool_name: str
    inputs: Dict[str, Any]
    outputs: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    start_time: float = None
    end_time: Optional[float] = None
    thought_id: str
    
    def __init__(self, **data):
        if 'id' not in data or data['id'] is None:
            data['id'] = uuid.uuid4().hex
        if 'start_time' not in data or data['start_time'] is None:
            data['start_time'] = datetime.now().timestamp()
        super().__init__(**data)

class AgentGoal(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    id: str = None
    description: str
    completed: bool = False
    sub_goals: Optional[List["AgentGoal"]] = None
    
    def __init__(self, **data):
        if 'id' not in data or data['id'] is None:
            data['id'] = uuid.uuid4().hex
        super().__init__(**data)

AgentStatus = Literal["idle", "thinking", "executing-tool", "completed", "failed"]

class AgentState(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    goals: List[AgentGoal] = []
    thoughts: List[ThoughtStep] = []
    tool_calls: List[ToolCall] = []
    context: Dict[str, Any] = {}
    status: AgentStatus = "idle"
    error: Optional[str] = None 