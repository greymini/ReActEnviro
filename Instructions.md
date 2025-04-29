## Project Overview

This document provides comprehensive specifications for building a ReAct-based AI agent framework with a Python backend and JavaScript frontend. The framework specializes in solving domain-specific problems while visualizing the agent's reasoning process. The system orchestrates LLM calls, tool executions, and decision-making in a transparent, extensible manner following the ReAct (Reasoning + Acting) paradigm.

## Core Features

1. **ReAct Agent Runtime System**: Python-based central orchestration of LLM reasoning and tool calls
2. **Reasoning Visualization**: JavaScript frontend for real-time visualization of agent thought processes and tool usage
3. **Tool Interface System**: Standardized approach for creating and integrating specialized Python tools
4. **State Management**: Complete tracking of agent's reasoning steps, tool calls, and goal progress
5. **Domain Adaptation**: Easy customization for specific problem domains

## Architecture

### System Components

```
backend/
├── app/
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── react_agent.py            # Main ReAct agent implementation
│   │   ├── llm_service.py            # LLM communication layer
│   │   ├── tool_orchestrator.py      # Manages tool selection and execution
│   │   └── state_manager.py          # State management for the agent
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── tool_registry.py          # Tool registry implementation
│   │   ├── base_tool.py              # Base class for all tools
│   │   └── specialized/              # Domain-specific tool implementations
│   │       ├── __init__.py
│   │       ├── data_analysis.py      # Data analysis tools
│   │       └── domain_specific.py    # Other domain-specific tools
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py                 # API endpoints
│   │   ├── models.py                 # API data models
│   │   └── websocket.py              # WebSocket for real-time updates
│   └── utils/
│       ├── __init__.py
│       ├── prompt_templates.py       # LLM prompt templates
│       └── helpers.py                # Utility functions
├── config.py                         # Configuration settings
├── main.py                           # Application entry point
└── requirements.txt                  # Python dependencies

frontend/
├── public/
│   ├── index.html
│   └── favicon.ico
├── src/
│   ├── components/
│   │   ├── AgentWorkspace/
│   │   │   ├── AgentWorkspace.js     # Main container for agent interactions
│   │   │   ├── ReasoningVisualizer.js # Visualization of agent thinking
│   │   │   ├── ToolExecutionPanel.js # Shows tool executions and results
│   │   │   └── GoalProgress.js       # Tracks progress toward objectives
│   │   └── common/                   # Common UI components
│   ├── services/
│   │   ├── api.js                    # API communication
│   │   ├── websocket.js              # WebSocket connection
│   │   └── state.js                  # Frontend state management
│   ├── utils/
│   │   └── helpers.js                # Utility functions
│   ├── App.js                        # Main React component
│   └── index.js                      # React entry point
├── package.json                      # JavaScript dependencies
└── webpack.config.js                 # Webpack configuration
```

### Data Flow

1. User submits a goal/task through the frontend
2. Request is sent to Python backend API
3. ReAct agent initializes with domain-specific configuration
4. For each reasoning step:
   - Agent reasons about the current state (step-by-step thinking)
   - Agent selects appropriate tool(s) based on reasoning
   - Tool execution occurs with results fed back to agent
   - Agent observes results and decides on next steps
   - Updates are sent to frontend via WebSocket in real-time
5. Process continues until goal completion or failure
6. Final results and reasoning chain are displayed to the user

## Core Types

### Python Backend Types

```python
# app/agent/types.py

from typing import Dict, List, Optional, Union, Literal
from pydantic import BaseModel
from datetime import datetime
import uuid

class ThoughtStep(BaseModel):
    id: str = uuid.uuid4().hex
    content: str
    timestamp: float = datetime.now().timestamp()
    parent_id: Optional[str] = None

class ToolCall(BaseModel):
    id: str = uuid.uuid4().hex
    tool_name: str
    inputs: Dict[str, any]
    outputs: Optional[Dict[str, any]] = None
    error: Optional[str] = None
    start_time: float = datetime.now().timestamp()
    end_time: Optional[float] = None
    thought_id: str

class AgentGoal(BaseModel):
    id: str = uuid.uuid4().hex
    description: str
    completed: bool = False
    sub_goals: Optional[List["AgentGoal"]] = None

class AgentStatus(str, Literal["idle", "thinking", "executing-tool", "completed", "failed"]):
    pass

class AgentState(BaseModel):
    goals: List[AgentGoal] = []
    thoughts: List[ThoughtStep] = []
    tool_calls: List[ToolCall] = []
    context: Dict[str, any] = {}
    status: AgentStatus = "idle"
    error: Optional[str] = None
```

### Tool Interface

```python
# app/tools/base_tool.py

from typing import Dict, List, Optional, Union, Literal, Any
from pydantic import BaseModel

class ToolParameter(BaseModel):
    type: Literal["string", "number", "boolean", "object", "array"]
    description: str
    required: bool = True

class ToolDefinition(BaseModel):
    name: str
    description: str
    category: str
    input_schema: Dict[str, ToolParameter]
    
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the tool with the given inputs"""
        raise NotImplementedError("Tool must implement execute method")
    
    def validate_inputs(self, inputs: Dict[str, Any]) -> Dict[str, Union[bool, List[str]]]:
        """Validate the inputs according to the input schema"""
        valid = True
        errors = []
        
        # Check required parameters
        for param_name, param_def in self.input_schema.items():
            if param_def.required and (param_name not in inputs or inputs[param_name] is None):
                valid = False
                errors.append(f"Required parameter '{param_name}' is missing")
        
        return {"valid": valid, "errors": errors if not valid else None}
```

### API Models

```python
# app/api/models.py

from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from app.agent.types import ThoughtStep, ToolCall, AgentGoal, AgentStatus

class StartAgentRequest(BaseModel):
    goal: str
    context: Optional[Dict[str, Any]] = {}

class AgentUpdateEvent(BaseModel):
    event_type: str  # "thought_added", "tool_started", "tool_completed", "goal_completed", etc.
    data: Dict[str, Any]
    
class AgentStateResponse(BaseModel):
    goals: List[AgentGoal]
    thoughts: List[ThoughtStep]
    tool_calls: List[ToolCall]
    status: AgentStatus
    error: Optional[str] = None
```

## Core Components

### ReAct Agent Implementation

```python
# app/agent/react_agent.py

from typing import Dict, List, Optional, Any
import asyncio
from datetime import datetime
from app.agent.types import ThoughtStep, ToolCall, AgentGoal, AgentState, AgentStatus
from app.agent.llm_service import LLMService
from app.agent.tool_orchestrator import ToolOrchestrator
from app.utils.prompt_templates import create_react_prompt, create_tool_decision_prompt

class ReActAgent:
    def __init__(self, llm_service: LLMService, tool_orchestrator: ToolOrchestrator):
        self.llm_service = llm_service
        self.tool_orchestrator = tool_orchestrator
        self.state = AgentState()
        self.state_listeners = []
    
    def add_state_listener(self, listener):
        """Add a listener function that will be called on state updates"""
        self.state_listeners.append(listener)
    
    def _notify_listeners(self, event_type: str, data: Dict[str, Any]):
        """Notify all listeners of a state update"""
        for listener in self.state_listeners:
            listener(event_type, data)
    
    async def start(self, goal: str, initial_context: Dict[str, Any] = None):
        """Start the agent with a goal"""
        # Create a new goal
        new_goal = AgentGoal(description=goal)
        self.state.goals = [new_goal]
        self.state.status = "thinking"
        
        if initial_context:
            self.state.context = initial_context
        
        self._notify_listeners("goal_set", {"goal": new_goal.dict()})
        self._notify_listeners("status_changed", {"status": self.state.status})
        
        try:
            # Start the ReAct loop
            await self._react_loop()
        except Exception as e:
            self.state.error = str(e)
            self.state.status = "failed"
            self._notify_listeners("error", {"error": str(e)})
            self._notify_listeners("status_changed", {"status": self.state.status})
    
    async def _react_loop(self):
        """Main ReAct loop: Reason → Act → Observe → Decide"""
        while self.state.status not in ["completed", "failed"]:
            # REASON: Generate the next thought
            thought = await self._generate_thought()
            self.state.thoughts.append(thought)
            self._notify_listeners("thought_added", {"thought": thought.dict()})
            
            # Check if goal is completed
            if "goal completed" in thought.content.lower() or "task completed" in thought.content.lower():
                self.state.goals[0].completed = True
                self.state.status = "completed"
                self._notify_listeners("goal_completed", {"goal_id": self.state.goals[0].id})
                self._notify_listeners("status_changed", {"status": self.state.status})
                break
            
            # ACT: Decide if we need to use a tool
            tool_decision = await self._decide_tool(thought.id)
            
            # If no tool needed, continue reasoning
            if tool_decision is None:
                continue
                
            # Execute the tool
            self.state.status = "executing-tool"
            self._notify_listeners("status_changed", {"status": self.state.status})
            
            # Create a tool call
            tool_call = ToolCall(
                tool_name=tool_decision["tool_name"],
                inputs=tool_decision["inputs"],
                thought_id=thought.id
            )
            
            self.state.tool_calls.append(tool_call)
            self._notify_listeners("tool_started", {"tool_call": tool_call.dict()})
            
            # OBSERVE: Execute the tool and observe results
            try:
                tool_result = await self.tool_orchestrator.execute_tool(
                    tool_call.tool_name, 
                    tool_call.inputs
                )
                
                # Update the tool call with results
                tool_call.outputs = tool_result
                tool_call.end_time = datetime.now().timestamp()
                
                self._notify_listeners("tool_completed", {
                    "tool_call_id": tool_call.id,
                    "outputs": tool_result
                })
                
            except Exception as e:
                # Handle tool execution error
                tool_call.error = str(e)
                tool_call.end_time = datetime.now().timestamp()
                
                self._notify_listeners("tool_failed", {
                    "tool_call_id": tool_call.id,
                    "error": str(e)
                })
            
            # Return to thinking
            self.state.status = "thinking"
            self._notify_listeners("status_changed", {"status": self.state.status})
    
    async def _generate_thought(self) -> ThoughtStep:
        """Generate the next thought using the LLM"""
        # Get the most recent thought if it exists
        parent_id = self.state.thoughts[-1].id if self.state.thoughts else None
        
        # Create the ReAct prompt
        prompt = create_react_prompt(
            goal=self.state.goals[0].description,
            thoughts=self.state.thoughts,
            tool_calls=self.state.tool_calls,
            available_tools=self.tool_orchestrator.list_tools(),
            context=self.state.context
        )
        
        # Get the thought content from the LLM
        thought_content = await self.llm_service.generate_text(prompt)
        
        # Create and return a new thought
        return ThoughtStep(
            content=thought_content,
            parent_id=parent_id
        )
    
    async def _decide_tool(self, thought_id: str) -> Optional[Dict[str, Any]]:
        """Decide if we need to use a tool and which one"""
        # Find the thought
        thought = next((t for t in self.state.thoughts if t.id == thought_id), None)
        if not thought:
            raise ValueError(f"Thought with ID {thought_id} not found")
        
        # Create a tool decision prompt
        prompt = create_tool_decision_prompt(
            goal=self.state.goals[0].description,
            thought=thought.content,
            available_tools=self.tool_orchestrator.list_tools(),
            context=self.state.context
        )
        
        # Get the tool decision from the LLM
        tool_decision = await self.llm_service.get_tool_decision(prompt)
        
        # If the decision is not to use a tool, return None
        if not tool_decision or "no_tool" in tool_decision:
            return None
            
        return {
            "tool_name": tool_decision["tool_name"],
            "inputs": tool_decision["inputs"]
        }
    
    def get_state(self) -> Dict[str, Any]:
        """Get the current state of the agent"""
        return self.state.dict()
    
    def stop(self):
        """Stop the agent"""
        if self.state.status in ["thinking", "executing-tool"]:
            self.state.status = "idle"
            self._notify_listeners("status_changed", {"status": self.state.status})
    
    def reset(self):
        """Reset the agent state"""
        self.state = AgentState()
        self._notify_listeners("state_reset", {})
```

### LLM Service

```python
# app/agent/llm_service.py

import aiohttp
from typing import Dict, List, Any, Optional
import json
import os
from tenacity import retry, stop_after_attempt, wait_exponential
from app.utils.prompt_templates import extract_json_from_response

class LLMService:
    def __init__(self, api_key: str, model: str, endpoint: str):
        self.api_key = api_key
        self.model = model
        self.endpoint = endpoint
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def generate_text(self, prompt: str) -> str:
        """Generate text from the LLM"""
        async with aiohttp.ClientSession() as session:
            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2,
                "max_tokens": 1000
            }
            
            async with session.post(self.endpoint, headers=self.headers, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"LLM API error: {response.status} - {error_text}")
                
                data = await response.json()
                return data["choices"][0]["message"]["content"]
    
    async def get_tool_decision(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Get a tool decision from the LLM"""
        response = await self.generate_text(prompt)
        
        try:
            # Extract JSON from the response
            tool_decision = extract_json_from_response(response)
            return tool_decision
        except Exception as e:
            print(f"Error parsing tool decision: {e}")
            print(f"Response: {response}")
            return None
```

### Tool Orchestrator

```python
# app/agent/tool_orchestrator.py

from typing import Dict, List, Any, Optional
from app.tools.tool_registry import ToolRegistry

class ToolOrchestrator:
    def __init__(self, tool_registry: ToolRegistry):
        self.tool_registry = tool_registry
    
    async def execute_tool(self, tool_name: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool with the given inputs"""
        # Get the tool from the registry
        tool = self.tool_registry.get_tool(tool_name)
        if not tool:
            raise ValueError(f"Tool '{tool_name}' not found")
        
        # Validate the inputs
        validation = tool.validate_inputs(inputs)
        if not validation["valid"]:
            error_message = ", ".join(validation["errors"])
            raise ValueError(f"Invalid inputs for tool '{tool_name}': {error_message}")
        
        # Execute the tool
        try:
            result = await tool.execute(inputs)
            return result
        except Exception as e:
            raise Exception(f"Error executing tool '{tool_name}': {str(e)}")
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """List all available tools"""
        tools = self.tool_registry.list_tools()
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "category": tool.category,
                "input_schema": {
                    name: {"type": param.type, "description": param.description, "required": param.required}
                    for name, param in tool.input_schema.items()
                }
            }
            for tool in tools
        ]
    
    def list_tools_by_category(self, category: str) -> List[Dict[str, Any]]:
        """List tools by category"""
        tools = self.tool_registry.list_tools_by_category(category)
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "category": tool.category,
                "input_schema": {
                    name: {"type": param.type, "description": param.description, "required": param.required}
                    for name, param in tool.input_schema.items()
                }
            }
            for tool in tools
        ]
```

### Tool Registry

```python
# app/tools/tool_registry.py

from typing import Dict, List, Optional
from app.tools.base_tool import ToolDefinition

class ToolRegistry:
    def __init__(self):
        self.tools: Dict[str, ToolDefinition] = {}
    
    def register_tool(self, tool: ToolDefinition) -> None:
        """Register a tool in the registry"""
        if tool.name in self.tools:
            print(f"Warning: Tool with name '{tool.name}' already exists. Overwriting.")
        self.tools[tool.name] = tool
    
    def unregister_tool(self, tool_name: str) -> None:
        """Unregister a tool from the registry"""
        if tool_name not in self.tools:
            print(f"Warning: Tool with name '{tool_name}' does not exist.")
            return
        del self.tools[tool_name]
    
    def get_tool(self, tool_name: str) -> Optional[ToolDefinition]:
        """Get a tool by name"""
        return self.tools.get(tool_name)
    
    def list_tools(self) -> List[ToolDefinition]:
        """List all registered tools"""
        return list(self.tools.values())
    
    def list_tools_by_category(self, category: str) -> List[ToolDefinition]:
        """List tools by category"""
        return [tool for tool in self.tools.values() if tool.category == category]
```

## API Endpoints

```python
# app/api/routes.py

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Dict, List, Any
from app.api.models import StartAgentRequest, AgentStateResponse
from app.agent.react_agent import ReActAgent
import json

router = APIRouter()

# Dependency to get the agent
async def get_agent():
    # In a real app, you would get this from a dependency injection system
    # or create/retrieve it based on user session
    return agent_instance

@router.post("/agent/start")
async def start_agent(request: StartAgentRequest, background_tasks: BackgroundTasks, agent: ReActAgent = Depends(get_agent)):
    """Start the agent with a goal"""
    try:
        # Start the agent in a background task
        background_tasks.add_task(agent.start, request.goal, request.context)
        return {"status": "started"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/agent/state")
async def get_agent_state(agent: ReActAgent = Depends(get_agent)):
    """Get the current state of the agent"""
    state = agent.get_state()
    return AgentStateResponse(**state)

@router.post("/agent/stop")
async def stop_agent(agent: ReActAgent = Depends(get_agent)):
    """Stop the agent"""
    agent.stop()
    return {"status": "stopped"}

@router.post("/agent/reset")
async def reset_agent(agent: ReActAgent = Depends(get_agent)):
    """Reset the agent state"""
    agent.reset()
    return {"status": "reset"}

@router.websocket("/agent/ws")
async def websocket_endpoint(websocket: WebSocket, agent: ReActAgent = Depends(get_agent)):
    """WebSocket endpoint for real-time updates"""
    await websocket.accept()
    
    # Define listener function
    async def state_listener(event_type, data):
        await websocket.send_text(json.dumps({
            "event_type": event_type,
            "data": data
        }))
    
    # Add listener to agent
    agent.add_state_listener(state_listener)
    
    try:
        # Wait for messages (client can send commands)
        while True:
            data = await websocket.receive_text()
            command = json.loads(data)
            
            if command["type"] == "start":
                await agent.start(command["goal"], command.get("context", {}))
            elif command["type"] == "stop":
                agent.stop()
            elif command["type"] == "reset":
                agent.reset()
    except WebSocketDisconnect:
        # Remove listener when client disconnects
        agent.state_listeners.remove(state_listener)
```

## Prompt Templates

```python
# app/utils/prompt_templates.py

from typing import Dict, List, Any
import re
import json

def create_react_prompt(goal: str, thoughts: List[Dict[str, Any]], 
                       tool_calls: List[Dict[str, Any]], available_tools: List[Dict[str, Any]],
                       context: Dict[str, Any]) -> str:
    """Create a prompt for the ReAct agent"""
    
    # Format previous thoughts and tool calls
    thought_history = ""
    for i, thought in enumerate(thoughts[-5:]):  # Include only the last 5 thoughts to manage context length
        thought_content = thought["content"]
        thought_history += f"\n## Thought {i+1}\n{thought_content}\n"
        
        # Add tool calls related to this thought
        related_tools = [tc for tc in tool_calls if tc["thought_id"] == thought["id"]]
        for tool_call in related_tools:
            thought_history += f"\n## Action\nTool: {tool_call['tool_name']}\nInputs: {json.dumps(tool_call['inputs'], indent=2)}\n"
            
            if tool_call.get("outputs"):
                thought_history += f"\n## Observation\n{json.dumps(tool_call['outputs'], indent=2)}\n"
            elif tool_call.get("error"):
                thought_history += f"\n## Observation\nError: {tool_call['error']}\n"
    
    # Format available tools
    tools_description = ""
    for tool in available_tools:
        tools_description += f"- {tool['name']}: {tool['description']}\n"
    
    # Format context
    context_str = "\n".join([f"{key}: {value}" for key, value in context.items()])
    
    # Create the full prompt
    prompt = f"""
# ReAct Agent

You are a ReAct (Reasoning + Acting) agent that solves problems by thinking step-by-step and using tools when needed.

## Goal
{goal}

## Context
{context_str}

## Available Tools
{tools_description}

## Previous Steps
{thought_history}

## Instructions
1. Think through the problem step-by-step
2. Decide whether you need to use a tool or can continue reasoning
3. If you need a tool, format your response as:
   ## Thought
   [Your reasoning about what to do next]
   
   ## Action
   Tool: [tool_name]
   Inputs: 
   {{
     "param1": "value1",
     "param2": "value2"
   }}

4. If you don't need a tool, just provide your thought:
   ## Thought
   [Your reasoning about what to do next]

5. If you believe the goal is complete, say so explicitly in your thought.

## Next Step
Think about what to do next:
"""
    
    return prompt

def create_tool_decision_prompt(goal: str, thought: str, 
                               available_tools: List[Dict[str, Any]],
                               context: Dict[str, Any]) -> str:
    """Create a prompt for deciding which tool to use"""
    
    # Format available tools with their input schemas
    tools_description = ""
    for tool in available_tools:
        tools_description += f"Tool: {tool['name']}\nDescription: {tool['description']}\nInputs:\n"
        for param_name, param_info in tool['input_schema'].items():
            required = "required" if param_info["required"] else "optional"
            tools_description += f"- {param_name} ({param_info['type']}, {required}): {param_info['description']}\n"
        tools_description += "\n"
    
    # Create the prompt
    prompt = f"""
# Tool Selection

## Goal
{goal}

## Current Thought
{thought}

## Available Tools
{tools_description}

Based on the current thought, decide whether to use a tool and which one.

If a tool is needed, respond with JSON in this format:
{{
  "tool_name": "name-of-tool",
  "inputs": {{
    "param1": "value1",
    "param2": "value2"
  }}
}}

If no tool is needed, respond with:
{{
  "no_tool": true,
  "reason": "reason why no tool is needed"
}}

## Decision
"""
    
    return prompt

def extract_json_from_response(response: str) -> Dict[str, Any]:
    """Extract JSON from an LLM response"""
    # Find JSON pattern in the response
    json_match = re.search(r'({[\s\S]*})', response)
    if not json_match:
        raise ValueError("No JSON found in response")
    
    json_str = json_match.group(1)
    
    # Try to parse the JSON
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        # Try to clean up the JSON string
        # Remove markdown code block syntax
        json_str = re.sub(r'```json|```', '', json_str).strip()
        return json.loads(json_str)
```

## Environmental Assessment Tool Examples

```python
# app/tools/specialized/environmental_assessment.py

from typing import Dict, List, Any, Optional
from app.tools.base_tool import ToolDefinition, ToolParameter
import asyncio

class SiteAnalysisTool(ToolDefinition):
    def __init__(self):
        super().__init__(
            name="site-analysis",
            description="Analyzes construction site characteristics and surrounding environment",
            category="environmental-assessment",
            input_schema={
                "location": ToolParameter(
                    type="object",
                    description="GPS coordinates or address of the construction site",
                    required=True
                ),
                "site_area": ToolParameter(
                    type="number",
                    description="Total area of the site in square meters",
                    required=True
                ),
                "terrain_type": ToolParameter(
                    type="string",
                    description="Type of terrain (flat, hilly, coastal, etc.)",
                    required=True
                ),
                "existing_vegetation": ToolParameter(
                    type="array",
                    description="List of existing vegetation types on site",
                    required=False
                )
            }
        )
    
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        location = inputs["location"]
        site_area = inputs["site_area"]
        terrain_type = inputs["terrain_type"]
        existing_vegetation = inputs.get("existing_vegetation", [])
        
        # Simulate API delay
        await asyncio.sleep(1)
        
        # Generate environmental sensitivity rating based on inputs
        sensitivity = self._calculate_sensitivity(terrain_type, existing_vegetation, site_area)
        
        # Mock nearby water bodies based on location
        water_bodies = self._get_nearby_water_bodies(location)
        
        # Mock soil data based on terrain
        soil_data = self._get_soil_data(terrain_type)
        
        # Mock ecosystem data
        ecosystem_data = self._get_ecosystem_data(location, existing_vegetation)
        
        # Mock climate data
        climate_data = self._get_climate_data(location)
        
        return {
            "environmentalSensitivity": sensitivity,
            "nearbyWaterBodies": water_bodies,
            "soilComposition": soil_data,
            "localEcosystem": ecosystem_data,
            "climateFactors": climate_data
        }
    
    def _calculate_sensitivity(self, terrain_type: str, vegetation: List[str], area: float) -> str:
        """Calculate environmental sensitivity based on inputs"""
        # Simple scoring system
        score = 0
        
        # Terrain factors
        terrain_scores = {
            "flat": 1,
            "hilly": 2,
            "mountainous": 3,
            "coastal": 4,
            "wetland": 5
        }
        score += terrain_scores.get(terrain_type.
        score += terrain_scores.get(terrain_type.lower(), 2)
        
        # Vegetation factors (more vegetation types = more sensitive)
        score += min(len(vegetation), 3)
        
        # Area factors (larger area = potentially more sensitive)
        if area > 10000:  # > 1 hectare
            score += 2
        elif area > 5000:
            score += 1
        
        # Convert score to rating
        if score >= 8:
            return "high"
        elif score >= 5:
            return "medium"
        else:
            return "low"
    
    def _get_nearby_water_bodies(self, location: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get nearby water bodies based on location"""
        # Mock data - in a real implementation, this would query GIS databases
        water_bodies_by_region = {
            "Seattle": [
                {"name": "Lake Washington", "distance": 1200, "type": "lake"},
                {"name": "Puget Sound", "distance": 3500, "type": "sound"}
            ],
            "Austin": [
                {"name": "Colorado River", "distance": 800, "type": "river"},
                {"name": "Lake Travis", "distance": 15000, "type": "lake"}
            ],
            "New York": [
                {"name": "Hudson River", "distance": 1500, "type": "river"},
                {"name": "East River", "distance": 2000, "type": "river"}
            ]
        }
        
        # Get city from location if available
        city = location.get("city", "")
        if city in water_bodies_by_region:
            return water_bodies_by_region[city]
        
        # Default mock water bodies
        return [
            {"name": "Small Creek", "distance": 450, "type": "creek"},
            {"name": "Unnamed Pond", "distance": 1200, "type": "pond"}
        ]
    
    def _get_soil_data(self, terrain_type: str) -> Dict[str, Any]:
        """Get soil data based on terrain type"""
        # Mock data based on terrain
        soil_types = {
            "flat": {
                "type": "alluvial",
                "permeability": "moderate to high",
                "erosionRisk": "low"
            },
            "hilly": {
                "type": "silty loam",
                "permeability": "moderate",
                "erosionRisk": "medium"
            },
            "mountainous": {
                "type": "rocky",
                "permeability": "low",
                "erosionRisk": "high"
            },
            "coastal": {
                "type": "sandy",
                "permeability": "high",
                "erosionRisk": "medium to high"
            },
            "wetland": {
                "type": "clay",
                "permeability": "low",
                "erosionRisk": "low"
            }
        }
        
        return soil_types.get(terrain_type.lower(), {
            "type": "mixed",
            "permeability": "moderate",
            "erosionRisk": "medium"
        })
    
    def _get_ecosystem_data(self, location: Dict[str, Any], vegetation: List[str]) -> Dict[str, Any]:
        """Get ecosystem data based on location and vegetation"""
        # Mock ecosystem types by region
        ecosystems_by_region = {
            "Seattle": {
                "habitatType": "temperate rainforest",
                "biodiversityIndex": 0.78,
                "protectedSpecies": ["Spotted Owl", "Coho Salmon"]
            },
            "Austin": {
                "habitatType": "mixed woodland/grassland",
                "biodiversityIndex": 0.72,
                "protectedSpecies": ["Golden-cheeked Warbler", "Black-capped Vireo"]
            },
            "New York": {
                "habitatType": "urban/suburban forest fragments",
                "biodiversityIndex": 0.45,
                "protectedSpecies": ["Peregrine Falcon"]
            }
        }
        
        # Get city from location if available
        city = location.get("city", "")
        if city in ecosystems_by_region:
            return ecosystems_by_region[city]
        
        # Default ecosystem data with adjustments based on vegetation
        habitat_type = "mixed woodland"
        if any("pine" in v.lower() for v in vegetation):
            habitat_type = "coniferous forest"
        elif any("oak" in v.lower() for v in vegetation):
            habitat_type = "deciduous forest"
        elif any("grass" in v.lower() for v in vegetation):
            habitat_type = "grassland"
            
        # Calculate biodiversity index based on vegetation diversity
        biodiversity = min(0.4 + (len(vegetation) * 0.1), 0.9)
        
        return {
            "habitatType": habitat_type,
            "biodiversityIndex": round(biodiversity, 2),
            "protectedSpecies": ["Local Protected Species"]
        }
    
    def _get_climate_data(self, location: Dict[str, Any]) -> Dict[str, Any]:
        """Get climate data based on location"""
        # Mock climate data by region
        climate_by_region = {
            "Seattle": {
                "annualRainfall": 950,
                "floodRisk": "medium",
                "windExposure": "moderate"
            },
            "Austin": {
                "annualRainfall": 870,
                "floodRisk": "medium",
                "windExposure": "low"
            },
            "New York": {
                "annualRainfall": 1200,
                "floodRisk": "medium to high",
                "windExposure": "moderate to high"
            }
        }
        
        # Get city from location if available
        city = location.get("city", "")
        if city in climate_by_region:
            return climate_by_region[city]
        
        # Default climate data
        return {
            "annualRainfall": 800,
            "floodRisk": "medium",
            "windExposure": "moderate"
        }

class EmissionsCalculatorTool(ToolDefinition):
    def __init__(self):
        super().__init__(
            name="emissions-calculator",
            description="Calculates projected emissions and environmental impact during construction and operation",
            category="environmental-assessment",
            input_schema={
                "construction_duration": ToolParameter(
                    type="number",
                    description="Expected duration of construction in months",
                    required=True
                ),
                "building_type": ToolParameter(
                    type="string",
                    description="Type of building being constructed",
                    required=True
                ),
                "construction_materials": ToolParameter(
                    type="array",
                    description="List of main construction materials",
                    required=True
                ),
                "energy_systems": ToolParameter(
                    type="object",
                    description="Energy systems to be used in the building",
                    required=False
                ),
                "equipment_usage": ToolParameter(
                    type="array",
                    description="List of heavy equipment to be used",
                    required=False
                )
            }
        )
    
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        construction_duration = inputs["construction_duration"]
        building_type = inputs["building_type"]
        construction_materials = inputs["construction_materials"]
        energy_systems = inputs.get("energy_systems", {})
        equipment_usage = inputs.get("equipment_usage", [])
        
        # Simulate API delay
        await asyncio.sleep(1.5)
        
        # Calculate construction phase emissions
        construction_emissions = self._calculate_construction_emissions(
            construction_duration, building_type, construction_materials, equipment_usage
        )
        
        # Calculate operational phase emissions
        operational_emissions = self._calculate_operational_emissions(
            building_type, energy_systems
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            construction_materials, energy_systems, construction_emissions, operational_emissions
        )
        
        return {
            "constructionPhase": construction_emissions,
            "operationalPhase": operational_emissions,
            "recommendations": recommendations
        }
    
    def _calculate_construction_emissions(self, duration: int, building_type: str, 
                                         materials: List[str], equipment: List[str]) -> Dict[str, Any]:
        """Calculate emissions during the construction phase"""
        # Base emissions factor by building type (tons CO2 per month)
        base_emissions_factors = {
            "residential": 15,
            "office": 20,
            "commercial": 25,
            "industrial": 35,
            "hospital": 30,
            "school": 18
        }
        
        base_factor = base_emissions_factors.get(building_type.lower(), 20)
        
        # Calculate carbon emissions
        carbon_emissions = base_factor * duration
        
        # Adjust based on materials
        material_factors = {
            "concrete": 1.2,
            "steel": 1.5,
            "wood": 0.7,
            "glass": 1.1,
            "aluminum": 1.4,
            "brick": 1.0,
            "recycled": 0.6
        }
        
        for material in materials:
            material_lower = material.lower()
            for key, factor in material_factors.items():
                if key in material_lower:
                    carbon_emissions *= factor
                    break
        
        # Equipment impact
        equipment_count = len(equipment)
        particulate_matter = 1.5 * equipment_count * duration
        noise_impact = "high" if equipment_count > 5 else "medium" if equipment_count > 2 else "low"
        
        # Water and waste calculations
        water_usage = duration * 1500  # cubic meters
        waste_prediction = duration * 30  # tons
        
        return {
            "carbonEmissions": round(carbon_emissions, 1),
            "particulateMatter": round(particulate_matter, 1),
            "noiseImpact": noise_impact,
            "waterUsage": round(water_usage),
            "wastePrediction": round(waste_prediction)
        }
    
    def _calculate_operational_emissions(self, building_type: str, 
                                        energy_systems: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate emissions during the operational phase"""
        # Base annual emissions by building type (tons CO2 per year)
        base_annual_emissions = {
            "residential": 8 * 12,  # per unit
            "office": 25 * 12,
            "commercial": 35 * 12,
            "industrial": 50 * 12,
            "hospital": 60 * 12,
            "school": 30 * 12
        }
        
        annual_emissions = base_annual_emissions.get(building_type.lower(), 300)
        
        # Adjust based on energy systems
        energy_factors = {
            "solar": 0.6,
            "geothermal": 0.5,
            "highEfficiency": 0.8,
            "standard": 1.0,
            "poor": 1.2
        }
        
        # Apply energy system factors
        for system, details in energy_systems.items():
            system_type = details.get("type", "").lower()
            for key, factor in energy_factors.items():
                if key.lower() in system_type:
                    annual_emissions *= factor
                    break
        
        # Energy efficiency rating
        efficiency_score = energy_systems.get("efficiencyScore", 50)
        efficiency_rating = "A" if efficiency_score > 90 else \
                           "B" if efficiency_score > 75 else \
                           "C" if efficiency_score > 55 else \
                           "D" if efficiency_score > 35 else "E"
        
        # Water and waste estimates
        annual_water = 10000  # cubic meters per year
        if building_type.lower() == "residential":
            annual_water = 2500
        elif building_type.lower() in ["office", "school"]:
            annual_water = 5000
        elif building_type.lower() == "hospital":
            annual_water = 15000
            
        annual_waste = 5 * 12  # tons per year
        if building_type.lower() in ["commercial", "industrial"]:
            annual_waste = 10 * 12
        elif building_type.lower() == "hospital":
            annual_waste = 15 * 12
        
        return {
            "annualCarbonFootprint": round(annual_emissions),
            "energyEfficiencyRating": efficiency_rating,
            "waterConsumption": round(annual_water),
            "wasteGeneration": round(annual_waste)
        }
    
    def _generate_recommendations(self, materials: List[str], energy_systems: Dict[str, Any],
                                 construction_emissions: Dict[str, Any], 
                                 operational_emissions: Dict[str, Any]) -> List[str]:
        """Generate recommendations to reduce emissions"""
        recommendations = []
        
        # Construction phase recommendations
        if "concrete" in str(materials).lower():
            recommendations.append("Consider using recycled concrete to reduce carbon footprint by 18%")
        
        if "steel" in str(materials).lower():
            recommendations.append("Use recycled steel to reduce embodied carbon by 30%")
        
        if construction_emissions["particulateMatter"] > 20:
            recommendations.append("Implement comprehensive dust suppression measures to reduce particulate emissions")
        
        if construction_emissions["noiseImpact"] == "high":
            recommendations.append("Use noise barriers and schedule noisy activities during less sensitive hours")
        
        if construction_emissions["waterUsage"] > 10000:
            recommendations.append("Implement water recycling systems for construction activities")
        
        # Operational phase recommendations
        if "solar" not in str(energy_systems).lower():
            recommendations.append("Solar panel installation would offset operational emissions by 35%")
        
        if operational_emissions["waterConsumption"] > 5000:
            recommendations.append("Implementing rainwater harvesting could reduce water consumption by 40%")
        
        if "geothermal" not in str(energy_systems).lower():
            recommendations.append("Consider geothermal heating/cooling to reduce energy consumption by 25%")
        
        if operational_emissions["energyEfficiencyRating"] not in ["A", "B"]:
            recommendations.append("Upgrade insulation and windows to improve energy efficiency rating")
        
        # Limit to top 5 recommendations
        return recommendations[:5]
```

## Frontend Implementation

The frontend will be built with JavaScript and will communicate with the Python backend through REST API and WebSocket connections for real-time updates.

### Key Frontend Components

```javascript
// src/components/AgentWorkspace/AgentWorkspace.js

import React, { useState, useEffect, useRef } from 'react';
import ReasoningVisualizer from './ReasoningVisualizer';
import ToolExecutionPanel from './ToolExecutionPanel';
import GoalProgress from './GoalProgress';
import { startAgent, stopAgent, resetAgent, getAgentState } from '../../services/api';
import { connectWebSocket } from '../../services/websocket';

const AgentWorkspace = ({ initialContext = {} }) => {
    const [state, setState] = useState({
        goals: [],
        thoughts: [],
        toolCalls: [],
        status: 'idle',
        error: null
    });
    
    const wsRef = useRef(null);
    
    // Connect to WebSocket on component mount
    useEffect(() => {
        const ws = connectWebSocket();
        
        ws.onmessage = (event) => {
            const update = JSON.parse(event.data);
            handleAgentUpdate(update);
        };
        
        ws.onclose = () => {
            console.log('WebSocket connection closed');
        };
        
        wsRef.current = ws;
        
        // Get initial state
        fetchAgentState();
        
        // Clean up on unmount
        return () => {
            if (wsRef.current) {
                wsRef.current.close();
            }
        };
    }, []);
    
    // Handle agent state updates
    const handleAgentUpdate = (update) => {
        const { event_type, data } = update;
        
        switch (event_type) {
            case 'thought_added':
                setState(prevState => ({
                    ...prevState,
                    thoughts: [...prevState.thoughts, data.thought]
                }));
                break;
                
            case 'tool_started':
                setState(prevState => ({
                    ...prevState,
                    toolCalls: [...prevState.toolCalls, data.tool_call]
                }));
                break;
                
            case 'tool_completed':
                setState(prevState => ({
                    ...prevState,
                    toolCalls: prevState.toolCalls.map(tc => 
                        tc.id === data.tool_call_id 
                            ? { ...tc, outputs: data.outputs, end_time: Date.now() / 1000 }
                            : tc
                    )
                }));
                break;
                
            case 'tool_failed':
                setState(prevState => ({
                    ...prevState,
                    toolCalls: prevState.toolCalls.map(tc => 
                        tc.id === data.tool_call_id 
                            ? { ...tc, error: data.error, end_time: Date.now() / 1000 }
                            : tc
                    )
                }));
                break;
                
            case 'status_changed':
                setState(prevState => ({
                    ...prevState,
                    status: data.status
                }));
                break;
                
            case 'goal_set':
                setState(prevState => ({
                    ...prevState,
                    goals: [...prevState.goals, data.goal]
                }));
                break;
                
            case 'goal_completed':
                setState(prevState => ({
                    ...prevState,
                    goals: prevState.goals.map(g => 
                        g.id === data.goal_id 
                            ? { ...g, completed: true }
                            : g
                    )
                }));
                break;
                
            case 'error':
                setState(prevState => ({
                    ...prevState,
                    error: data.error
                }));
                break;
                
            case 'state_reset':
                setState({
                    goals: [],
                    thoughts: [],
                    toolCalls: [],
                    status: 'idle',
                    error: null
                });
                break;
                
            default:
                console.log('Unknown event type:', event_type);
        }
    };
    
    // Fetch the current agent state
    const fetchAgentState = async () => {
        try {
            const agentState = await getAgentState();
            setState(agentState);
        } catch (error) {
            console.error('Error fetching agent state:', error);
        }
    };
    
    // Handle goal submission
    const handleGoalSubmit = async (goalText) => {
        try {
            await startAgent(goalText, initialContext);
        } catch (error) {
            console.error('Error starting agent:', error);
        }
    };
    
    // Handle stopping the agent
    const handleStopAgent = async () => {
        try {
            await stopAgent();
        } catch (error) {
            console.error('Error stopping agent:', error);
        }
    };
    
    // Handle resetting the agent
    const handleResetAgent = async () => {
        try {
            await resetAgent();
        } catch (error) {
            console.error('Error resetting agent:', error);
        }
    };
    
    return (
        <div className="agent-workspace">
            <header className="workspace-header">
                <h1>ReAct Agent Workspace</h1>
                <div className="agent-controls">
                    <input 
                        type="text" 
                        placeholder="Enter goal for the agent..." 
                        disabled={state.status !== 'idle'}
                        onKeyDown={(e) => {
                            if (e.key === 'Enter') {
                                handleGoalSubmit(e.currentTarget.value);
                                e.currentTarget.value = '';
                            }
                        }}
                    />
                    <button 
                        onClick={handleStopAgent}
                        disabled={!['thinking', 'executing-tool'].includes(state.status)}
                    >
                        Stop
                    </button>
                    <button 
                        onClick={handleResetAgent}
                        disabled={state.status === 'thinking' || state.status === 'executing-tool'}
                    >
                        Reset
                    </button>
                </div>
                <div className="agent-status">
                    Status: <span className={`status-${state.status}`}>{state.status}</span>
                    {state.error && <span className="error-message">Error: {state.error}</span>}
                </div>
            </header>
            
            <div className="workspace-content">
                <div className="workspace-main">
                    <ReasoningVisualizer 
                        thoughts={state.thoughts}
                        toolCalls={state.toolCalls}
                        activeThoughtId={state.thoughts.length > 0 ? state.thoughts[state.thoughts.length - 1].id : undefined}
                    />
                </div>
                
                <div className="workspace-sidebar">
                    <GoalProgress goals={state.goals} />
                    <ToolExecutionPanel toolCalls={state.toolCalls} />
                </div>
            </div>
        </div>
    );
};

export default AgentWorkspace;
```

### API Services

```javascript
// src/services/api.js

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Start the agent with a goal
export const startAgent = async (goal, context = {}) => {
    try {
        const response = await fetch(`${API_BASE_URL}/agent/start`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ goal, context }),
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to start agent');
        }
        
        return await response.json();
    } catch (error) {
        console.error('Error starting agent:', error);
        throw error;
    }
};

// Stop the agent
export const stopAgent = async () => {
    try {
        const response = await fetch(`${API_BASE_URL}/agent/stop`, {
            method: 'POST',
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to stop agent');
        }
        
        return await response.json();
    } catch (error) {
        console.error('Error stopping agent:', error);
        throw error;
    }
};

// Reset the agent
export const resetAgent = async () => {
    try {
        const response = await fetch(`${API_BASE_URL}/agent/reset`, {
            method: 'POST',
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to reset agent');
        }
        
        return await response.json();
    } catch (error) {
        console.error('Error resetting agent:', error);
        throw error;
    }
};

// Get the current agent state
export const getAgentState = async () => {
    try {
        const response = await fetch(`${API_BASE_URL}/agent/state`);
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to get agent state');
        }
        
        return await response.json();
    } catch (error) {
        console.error('Error getting agent state:', error);
        throw error;
    }
};
```

### WebSocket Service

```javascript
// src/services/websocket.js

const WS_URL = process.env.REACT_APP_WS_URL || 'ws://localhost:8000/agent/ws';

export const connectWebSocket = () => {
    const ws = new WebSocket(WS_URL);
    
    ws.onopen = () => {
        console.log('WebSocket connection established');
    };
    
    ws.onerror = (error) => {
        console.error('WebSocket error:', error);
    };
    
    return ws;
};

export const sendWebSocketCommand = (ws, command) => {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify(command));
    } else {
        console.error('WebSocket is not connected');
    }
};
```

## Main Application Entry Point

```python
# main.py

import uvicorn
from fastapi import FastAPI
from app.api.routes import router
from app.agent.llm_service import LLMService
from app.agent.tool_orchestrator import ToolOrchestrator
from app.agent.react_agent import ReActAgent
from app.tools.tool_registry import ToolRegistry
from app.tools.specialized.environmental_assessment import SiteAnalysisTool, EmissionsCalculatorTool
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="ReAct Agent Framework")

# Add routes
app.include_router(router)

# Initialize services and agent
def initialize_agent():
    # Get configuration from environment
    llm_api_key = os.getenv("LLM_API_KEY")
    llm_endpoint = os.getenv("LLM_ENDPOINT")
    llm_model = os.getenv("LLM_MODEL")
    
    # Create LLM service
    llm_service = LLMService(
        api_key=llm_api_key,
        endpoint=llm_endpoint,
        model=llm_model
    )
    
    # Create tool registry and register tools
    tool_registry = ToolRegistry()
    
    # Register environmental assessment tools
    tool_registry.register_tool(SiteAnalysisTool())
    tool_registry.register_tool(EmissionsCalculatorTool())
    
    # Create tool orchestrator
    tool_orchestrator = ToolOrchestrator(tool_registry)
    
    # Create ReAct agent
    agent = ReActAgent(llm_service, tool_orchestrator)
    
    return agent

# Create a global agent instance
agent_instance = initialize_agent()

# Provide the agent instance to the router
router.dependency_overrides[get_agent] = lambda: agent_instance

# Run the app if executed directly
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
```

## Application Setup and Deployment

### Python Backend Setup

1. Create a virtual environment and install dependencies:

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install fastapi uvicorn pydantic python-dotenv aiohttp pandas numpy tenacity websockets
```

2. Create the project structure:

```bash
mkdir -p backend/app/agent backend/app/tools/specialized backend/app/api backend/app/utils
touch backend/app/agent/__init__.py backend/app/tools/__init__.py backend/app/api/__init__.py backend/app/utils/__init__.py
touch backend/config.py backend/main.py backend/requirements.txt
```

3. Set up environment variables:

```
# .env file
LLM_API_KEY=your_api_key_here
LLM_ENDPOINT=https://api.anthropic.com/v1/complete
LLM_MODEL=claude-3-opus-20240229
```

### JavaScript Frontend Setup

1. Create a React app and install dependencies:

```bash
# Create a React app
npx create-react-app frontend

# Navigate to the project directory
cd frontend

# Install dependencies
npm install react-router-dom axios recharts
```

2. Set up environment variables:

```
# .env file
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000/agent/ws
```

### Docker Deployment

Create Docker configuration for easy deployment:

```dockerfile
# backend/Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```dockerfile
# frontend/Dockerfile
FROM node:14-alpine as build

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

Docker Compose for local development:

```yaml
# docker-compose.yml
version: '3'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    env_file:
      - .env
    volumes:
      - ./backend:/app

  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    depends_on:
      - backend
```

## Conclusion

This specification provides a comprehensive blueprint for building a ReAct agent specialized in environmental impact assessment with:

1. **Python Backend**: Leveraging Python's strengths for data processing and API integrations
2. **JavaScript Frontend**: Creating an intuitive UI for visualizing agent reasoning
3. **ReAct Paradigm**: Implementing the Reasoning → Acting → Observing → Deciding cycle
4. **Specialized Tools**: Environmental analysis tools with clearly defined interfaces
5. **Real-time Visualization**: WebSocket-based updates for seeing agent reasoning as it happens

The agent architecture supports extension to other domains by adding new specialized tools while maintaining the core ReAct loop that provides transparency into the agent's reasoning process.
            "flat": 1,
            "hilly": 2,
            "mountainous": 3,
            "coastal": 4,
            "wetland": 5
        }
        score += terrain_scores.get(terrain_type.lower(), 2)
        
        # Vegetation factors (more vegetation types = more sensitive)
        score += min(len(vegetation), 3)
        
        # Area factors (larger area = potentially more sensitive)
        if area > 10000:  # > 1 hectare
            score += 2
        elif area > 5000:
            score += 1
        
        # Convert score to rating
        if score >= 8:
            return "high"
        elif score >= 5:
            return "medium"
        else:
            return "low"
    
    def _get_nearby_water_bodies(self, location: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get nearby water bodies based on location"""
        # Mock data - in a real implementation, this would query GIS databases
        water_bodies_by_region = {
            "Seattle": [
                {"name": "Lake Washington", "distance": 1200, "type": "lake"},
                {"name": "Puget Sound", "distance": 3500, "type": "sound"}
            ],
            "Austin": [
                {"name": "Colorado River", "distance": 800, "type": "river"},
                {"name": "Lake Travis", "distance": 15000, "type": "lake"}
            ],
            "New York": [
                {"name": "Hudson River", "distance": 1500, "type": "river"},
                {"name": "East River", "distance": 2000, "type": "river"}
            ]
        }
        
        # Get city from location if available
        city = location.get("city", "")
        if city in water_bodies_by_region:
            return water_bodies_by_region[city]
        
        # Default mock water bodies
        return [
            {"name": "Small Creek", "distance": 450, "type": "creek"},
            {"name": "Unnamed Pond", "distance": 1200, "type": "pond"}
        ]
    
    def _get_soil_data(self, terrain_type: str) -> Dict[str, Any]:
        """Get soil data based on terrain type"""
        # Mock data based on terrain
        soil_types = {
            "flat": {
                "type": "alluvial",
                "permeability": "moderate to high",
                "erosionRisk": "low"
            },
            "hilly": {# ReAct Agent Framework Development Specifications