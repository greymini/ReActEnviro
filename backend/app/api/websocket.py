from fastapi import WebSocket, WebSocketDisconnect
import json
import asyncio
from typing import Dict, List, Any
from app.agent.react_agent import ReActAgent

# Store active connections
active_connections = []
agent_instance = None

def setup_agent_websocket(agent):
    """Set up the agent instance for the WebSocket connections"""
    global agent_instance
    agent_instance = agent

async def state_listener(event_type: str, data: Dict[str, Any]):
    """Listener for agent state updates"""
    # Broadcast to all connected clients
    for connection in active_connections:
        await connection.send_text(json.dumps({
            "event_type": event_type,
            "data": data
        }))

async def handle_websocket_connection(websocket: WebSocket):
    """Handle a WebSocket connection"""
    # Accept the connection
    await websocket.accept()
    
    # Add to active connections
    active_connections.append(websocket)
    
    try:
        # Add state listener to agent
        if agent_instance:
            agent_instance.add_state_listener(state_listener)
            
        # Wait for commands from the client
        while True:
            # Receive data from the client
            data = await websocket.receive_text()
            command = json.loads(data)
            
            # Process commands
            if command.get("type") == "start":
                # Start the agent
                if agent_instance:
                    goal = command.get("goal", "")
                    context = command.get("context", {})
                    
                    # Start the agent in a background task
                    asyncio.create_task(agent_instance.start(goal, context))
                    
            elif command.get("type") == "stop":
                # Stop the agent
                if agent_instance:
                    asyncio.create_task(agent_instance.stop())
                    
            elif command.get("type") == "reset":
                # Reset the agent
                if agent_instance:
                    asyncio.create_task(agent_instance.reset())
    
    except WebSocketDisconnect:
        # Remove from active connections
        active_connections.remove(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        # Remove from active connections if not already removed
        if websocket in active_connections:
            active_connections.remove(websocket) 