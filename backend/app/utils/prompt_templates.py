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
        # Add input schema details for clearer understanding
        tools_description += "  Inputs:\n"
        for param_name, param_info in tool['input_schema'].items():
            required = "required" if param_info["required"] else "optional"
            tools_description += f"    - {param_name} ({param_info['type']}, {required}): {param_info['description']}\n"
    
    # Format context
    context_str = "\n".join([f"{key}: {value}" for key, value in context.items()])
    
    # Create the full prompt
    prompt = f"""
# Environmental Impact Assessment ReAct Agent

You are a ReAct (Reasoning + Acting) agent specialized in environmental impact assessment. You solve problems by thinking step-by-step and using specialized environmental assessment tools when needed.

## Goal
{goal}

## Context
{context_str}

## Available Tools
{tools_description}

## Previous Steps
{thought_history}

## Instructions
1. Think through the environmental assessment step-by-step
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

5. If you believe the goal is complete, say so explicitly in your thought: "Goal completed: [summary of findings]"

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
# Environmental Impact Assessment Tool Selection

## Goal
{goal}

## Current Thought
{thought}

## Available Tools
{tools_description}

Based on the current thought about environmental assessment, decide whether to use a tool and which one.

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

Think carefully about which tool is most appropriate for the current assessment step.

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