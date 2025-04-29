from typing import Dict, List, Optional, Any, Callable
import asyncio
import logging
from datetime import datetime
from app.agent.types import ThoughtStep, ToolCall, AgentGoal, AgentState, AgentStatus
from app.agent.llm_service import LLMService
from app.agent.tool_orchestrator import ToolOrchestrator
from app.utils.prompt_templates import create_react_prompt, create_tool_decision_prompt

# Set up logging
logger = logging.getLogger(__name__)

class ReActAgent:
    def __init__(self, llm_service: LLMService, tool_orchestrator: ToolOrchestrator):
        self.llm_service = llm_service
        self.tool_orchestrator = tool_orchestrator
        self.state = AgentState()
        self.state_listeners = []
        logger.info("ReActAgent initialized")
    
    def add_state_listener(self, listener: Callable[[str, Dict[str, Any]], None]):
        """Add a listener function that will be called on state updates"""
        self.state_listeners.append(listener)
        logger.debug(f"Added state listener. Total listeners: {len(self.state_listeners)}")
    
    async def _notify_listeners(self, event_type: str, data: Dict[str, Any]):
        """Notify all listeners of a state update"""
        logger.debug(f"Notifying listeners of event: {event_type}")
        for listener in self.state_listeners:
            try:
                if asyncio.iscoroutinefunction(listener):
                    await listener(event_type, data)
                else:
                    listener(event_type, data)
            except Exception as e:
                logger.error(f"Error notifying listener: {e}")
    
    async def start(self, goal: str, initial_context: Dict[str, Any] = None):
        """Start the agent with a goal"""
        logger.info(f"Starting agent with goal: {goal}")
        # Create a new goal
        new_goal = AgentGoal(description=goal)
        self.state.goals = [new_goal]
        self.state.status = "thinking"
        
        if initial_context:
            self.state.context = initial_context
        
        await self._notify_listeners("goal_set", {"goal": new_goal.dict()})
        await self._notify_listeners("status_changed", {"status": self.state.status})
        
        try:
            # Start the ReAct loop
            await self._react_loop()
        except Exception as e:
            logger.error(f"Error in ReAct loop: {str(e)}", exc_info=True)
            self.state.error = str(e)
            self.state.status = "failed"
            await self._notify_listeners("error", {"error": str(e)})
            await self._notify_listeners("status_changed", {"status": self.state.status})
    
    async def _react_loop(self):
        """Main ReAct loop: Reason → Act → Observe → Decide"""
        logger.info("Starting ReAct loop")
        while self.state.status not in ["completed", "failed"]:
            try:
                # REASON: Generate the next thought
                logger.info("Generating next thought")
                thought = await self._generate_thought()
                self.state.thoughts.append(thought)
                await self._notify_listeners("thought_added", {"thought": thought.dict()})
                
                # Check if goal is completed
                if "goal completed" in thought.content.lower() or "task completed" in thought.content.lower():
                    logger.info("Goal completed")
                    self.state.goals[0].completed = True
                    self.state.status = "completed"
                    await self._notify_listeners("goal_completed", {"goal_id": self.state.goals[0].id})
                    await self._notify_listeners("status_changed", {"status": self.state.status})
                    break
                
                # ACT: Decide if we need to use a tool
                logger.info("Deciding on tool usage")
                tool_decision = await self._decide_tool(thought.id)
                
                # If no tool needed, continue reasoning
                if tool_decision is None:
                    logger.info("No tool needed, continuing to next thought")
                    continue
                    
                # Execute the tool
                logger.info(f"Tool selected: {tool_decision['tool_name']}")
                self.state.status = "executing-tool"
                await self._notify_listeners("status_changed", {"status": self.state.status})
                
                # Create a tool call
                tool_call = ToolCall(
                    tool_name=tool_decision["tool_name"],
                    inputs=tool_decision["inputs"],
                    thought_id=thought.id
                )
                
                self.state.tool_calls.append(tool_call)
                await self._notify_listeners("tool_started", {"tool_call": tool_call.dict()})
                
                # OBSERVE: Execute the tool and observe results
                try:
                    logger.info(f"Executing tool: {tool_call.tool_name} with inputs: {tool_call.inputs}")
                    tool_result = await self.tool_orchestrator.execute_tool(
                        tool_call.tool_name, 
                        tool_call.inputs
                    )
                    
                    # Update the tool call with results
                    tool_call.outputs = tool_result
                    tool_call.end_time = datetime.now().timestamp()
                    logger.info(f"Tool execution completed: {tool_call.tool_name}")
                    
                    await self._notify_listeners("tool_completed", {
                        "tool_call_id": tool_call.id,
                        "outputs": tool_result
                    })
                    
                except Exception as e:
                    # Handle tool execution error
                    error_msg = f"Error executing tool '{tool_call.tool_name}': {str(e)}"
                    logger.error(error_msg, exc_info=True)
                    tool_call.error = error_msg
                    tool_call.end_time = datetime.now().timestamp()
                    
                    await self._notify_listeners("tool_failed", {
                        "tool_call_id": tool_call.id,
                        "error": error_msg
                    })
                
                # Return to thinking
                self.state.status = "thinking"
                await self._notify_listeners("status_changed", {"status": self.state.status})
                
            except Exception as e:
                logger.error(f"Error in ReAct loop iteration: {str(e)}", exc_info=True)
                self.state.error = str(e)
                self.state.status = "failed"
                await self._notify_listeners("error", {"error": str(e)})
                await self._notify_listeners("status_changed", {"status": self.state.status})
                break
    
    async def _generate_thought(self) -> ThoughtStep:
        """Generate the next thought using the LLM"""
        # Get the most recent thought if it exists
        parent_id = self.state.thoughts[-1].id if self.state.thoughts else None
        
        # Create the ReAct prompt
        try:
            prompt = create_react_prompt(
                goal=self.state.goals[0].description,
                thoughts=[t.dict() for t in self.state.thoughts],
                tool_calls=[tc.dict() for tc in self.state.tool_calls],
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
        except Exception as e:
            logger.error(f"Error generating thought: {str(e)}", exc_info=True)
            raise Exception(f"Failed to generate thought: {str(e)}")
    
    async def _decide_tool(self, thought_id: str) -> Optional[Dict[str, Any]]:
        """Decide if we need to use a tool and which one"""
        # Find the thought
        thought = next((t for t in self.state.thoughts if t.id == thought_id), None)
        if not thought:
            error_msg = f"Thought with ID {thought_id} not found"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        try:
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
                logger.info("Decision: No tool needed")
                return None
                
            logger.info(f"Tool decision: {tool_decision['tool_name']}")
            return {
                "tool_name": tool_decision["tool_name"],
                "inputs": tool_decision["inputs"]
            }
        except Exception as e:
            logger.error(f"Error deciding tool: {str(e)}", exc_info=True)
            raise Exception(f"Failed to decide tool: {str(e)}")
    
    def get_state(self) -> Dict[str, Any]:
        """Get the current state of the agent"""
        return {
            "goals": [g.dict() for g in self.state.goals],
            "thoughts": [t.dict() for t in self.state.thoughts],
            "tool_calls": [tc.dict() for tc in self.state.tool_calls],
            "status": self.state.status,
            "error": self.state.error
        }
    
    async def stop(self):
        """Stop the agent"""
        logger.info("Stopping agent")
        if self.state.status in ["thinking", "executing-tool"]:
            self.state.status = "idle"
            await self._notify_listeners("status_changed", {"status": self.state.status})
    
    async def reset(self):
        """Reset the agent state"""
        logger.info("Resetting agent state")
        self.state = AgentState()
        await self._notify_listeners("state_reset", {}) 