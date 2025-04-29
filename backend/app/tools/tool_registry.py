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