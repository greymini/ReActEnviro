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