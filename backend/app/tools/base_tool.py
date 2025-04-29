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