from fastapi import WebSocket, WebSocketDisconnect
import json
import asyncio
from typing import Dict, List, Any, Optional
from app.agent.react_agent import ReActAgent
import logging
from datetime import datetime
from starlette.websockets import WebSocketState

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables
active_connections: List[WebSocket] = []
agent_instance = None

def setup_agent_websocket(agent_instance_param):
    """Set up the WebSocket connection for the agent"""
    global agent_instance
    agent_instance = agent_instance_param
    
    # Register state listener with the agent
    if agent_instance:
        agent_instance.add_state_listener(state_listener)
        logger.info("Agent state listener registered with agent")
    else:
        logger.error("Cannot register state listener: agent_instance is None")
        
    logger.info("Agent WebSocket setup complete")

async def state_listener(event_type: str, data: Dict[str, Any]):
    """Listener for agent state updates"""
    # Broadcast to all connected clients
    clients_to_remove = []
    for connection in active_connections:
        try:
            if connection.client_state == WebSocketState.CONNECTED:
                # Format the message in the way the frontend expects
                # The frontend expects { event_type: string, data: object }
                logger.info(f"Broadcasting event: {event_type} to clients")
                await connection.send_text(json.dumps({
                    "event_type": event_type,
                    "data": data
                }))
            else:
                clients_to_remove.append(connection)
        except Exception as e:
            logger.error(f"Error sending to client: {str(e)}")
            clients_to_remove.append(connection)
    
    # Clean up any disconnected clients
    for client in clients_to_remove:
        if client in active_connections:
            active_connections.remove(client)
            logger.info("Removed disconnected client from active connections")

async def handle_websocket_connection(websocket: WebSocket):
    """Handle a WebSocket connection"""
    # Accept the connection
    await websocket.accept()
    
    # Add to active connections
    active_connections.append(websocket)
    logger.info("WebSocket connection accepted in handle_websocket_connection from %s", websocket.client.host)
    
    # Keep track of the listener function for cleanup
    listener_function = None
    
    try:
        # Add state listener to agent
        if agent_instance:
            listener_function = state_listener
            agent_instance.add_state_listener(listener_function)
            
        # Wait for commands from the client
        while True:
            # Receive data from the client
            data = await websocket.receive_json()
            logger.info("Received message in handle_websocket_connection: %s", data)
            
            # Check for ping message
            if data.get('type') == 'ping':
                logger.info("Received ping in handle_websocket_connection, sending pong")
                await websocket.send_json({
                    'type': 'pong',
                    'timestamp': datetime.now().isoformat()
                })
                continue
                
            command = data
            
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
        # Remove state listener
        if agent_instance and listener_function:
            if listener_function in agent_instance.state_listeners:
                agent_instance.state_listeners.remove(listener_function)
                logger.info("Removed state listener from agent after disconnect")
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        # Remove from active connections if not already removed
        if websocket in active_connections:
            active_connections.remove(websocket)
        # Remove state listener on error
        if agent_instance and listener_function:
            if listener_function in agent_instance.state_listeners:
                agent_instance.state_listeners.remove(listener_function)
                logger.info("Removed state listener from agent after error")

class AgentConnection:
    def __init__(self, websocket, agent):
        self.websocket = websocket
        self.agent = agent
        self.agent_started = False
        
    async def handle_message(self, message_data):
        try:
            message_type = message_data.get("type")
            
            if message_type == "start":
                goal = message_data.get("goal", "")
                if not goal:
                    await self.send_error("Goal is required")
                    return
                
                # Start the agent if not already started
                if not self.agent_started:
                    self.agent_started = True
                    # Add this connection as a listener
                    self.agent.add_state_listener(self.on_state_update)
                    # Start the agent
                    asyncio.create_task(self.agent.start(goal))
                else:
                    await self.send_error("Agent already started")
            
            elif message_type == "stop":
                # Stop the agent
                await self.agent.stop()
                await self.send_message({
                    "type": "status",
                    "status": "stopped"
                })
                
            elif message_type == "reset":
                # Reset the agent
                await self.agent.reset()
                self.agent_started = False
                await self.send_message({
                    "type": "status",
                    "status": "reset"
                })
                
            elif message_type == "user_input":
                # Handle user input
                input_data = message_data.get("data", {})
                request_id = message_data.get("requestId", "")
                
                # Mark the request as fulfilled
                if request_id:
                    self.agent.state.mark_request_fulfilled(request_id)
                
                # Provide the input to the agent
                await self.agent.provide_user_input(input_data)
                await self.send_message({
                    "type": "input_received",
                    "requestId": request_id
                })
            
            else:
                await self.send_error(f"Unknown message type: {message_type}")
                
        except Exception as e:
            logger.error(f"Error handling WebSocket message: {str(e)}", exc_info=True)
            await self.send_error(f"Error: {str(e)}")
            
    async def on_state_update(self, event_type=None, data=None):
        """Handle state updates from the agent"""
        try:
            # Convert the entire state to a serializable dict
            state_dict = self._state_to_dict()
            
            # Add the specific event type and data
            message = {
                "type": "state_update",
                "eventType": event_type,
                "eventData": data,
                "state": state_dict
            }
            
            # Check if the agent is waiting for user input
            if self.agent.is_awaiting_user_input():
                active_request = self.agent.state.get_active_user_request()
                if active_request:
                    message["userInputRequest"] = active_request
            
            # Log important state updates before sending them
            if event_type in ["thought_added", "tool_started", "tool_completed", "tool_failed", "goal_completed", "status_changed"]:
                logger.debug(f"Sending state update to client: {event_type} with data: {data}")
            
            await self.send_message(message)
            
        except Exception as e:
            logger.error(f"Error sending state update: {str(e)}", exc_info=True)
            await self.send_error(f"Failed to send state update: {str(e)}")
            
    def _state_to_dict(self):
        """Convert agent state to a serializable dict"""
        state = self.agent.state
        
        # Create a serializable representation of the state
        state_dict = {
            "status": state.status,
            "error": state.error,
            "thoughts": [self._thought_to_dict(t) for t in state.thoughts],
            "toolCalls": [self._tool_call_to_dict(tc) for tc in state.tool_calls],
            "userInputRequests": state.user_input_requests
        }
        
        return state_dict
    
    def _thought_to_dict(self, thought):
        """Convert a thought to a serializable dict"""
        return {
            "id": thought.id,
            "text": thought.content,
            "timestamp": datetime.fromtimestamp(thought.timestamp).isoformat() if hasattr(thought, "timestamp") and thought.timestamp else None
        }
    
    def _tool_call_to_dict(self, tool_call):
        """Convert a tool call to a serializable dict"""
        return {
            "id": tool_call.id,
            "tool": tool_call.tool_name,
            "inputs": tool_call.inputs,
            "result": tool_call.outputs,
            "error": tool_call.error,
            "timestamp": tool_call.start_time if hasattr(tool_call, "start_time") else None
        }
    
    async def send_message(self, message):
        """Send a message to the WebSocket client"""
        try:
            # Check if the websocket is still open before sending
            if self.websocket.client_state == WebSocketState.CONNECTED:
                await self.websocket.send_json(message)
            else:
                logger.warning("Attempted to send message on closed websocket")
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}", exc_info=True)
    
    async def send_error(self, error_message):
        """Send an error message to the WebSocket client"""
        await self.send_message({
            "type": "error",
            "error": error_message
        })

    async def cleanup(self):
        """Clean up when a connection closes"""
        # Remove this instance from agent listeners to prevent sending messages to closed connections
        if self.agent and self.agent.state_listeners:
            if self.on_state_update in self.agent.state_listeners:
                self.agent.state_listeners.remove(self.on_state_update)
                logger.info("Removed state listener from agent")

async def agent_websocket_endpoint(websocket: WebSocket):
    """Handle WebSocket connections for the agent"""
    if agent_instance is None:
        logger.error("Agent not initialized")
        return
    
    # Create agent connection handler
    connection = AgentConnection(websocket, agent_instance)
    
    try:
        # Accept the connection
        await websocket.accept()
        active_connections.append(websocket)
        logger.info("WebSocket connection accepted from %s", websocket.client.host)
        
        # Listen for messages
        while True:
            data = await websocket.receive_json()
            logger.info("Received WebSocket message: %s", data)
            
            # Check for ping message
            if data.get('type') == 'ping':
                logger.info("Received ping, sending pong")
                await websocket.send_json({
                    'type': 'pong',
                    'timestamp': datetime.now().isoformat()
                })
                continue
                
            await connection.handle_message(data)
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
        await connection.cleanup()
    except Exception as e:
        logger.error(f"Error in WebSocket connection: {str(e)}", exc_info=True)
        await connection.cleanup()
    finally:
        # Clean up
        if websocket in active_connections:
            active_connections.remove(websocket) 