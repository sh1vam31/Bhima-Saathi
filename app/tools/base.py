from pydantic import BaseModel
from typing import Literal, Dict, Any, Optional
from abc import ABC, abstractmethod

class ToolResult(BaseModel):
    status: Literal["success", "error"]
    data: Optional[Dict[str, Any]] = None
    error_code: Optional[str] = None
    request_id: str
    latency_ms: int

class TurnContext(BaseModel):
    conversation_id: str
    turn_id: str
    # Other context needed by tools

class Tool(ABC):
    name: str
    description: str
    args_model: type[BaseModel] # pydantic model -> JSON schema
    timeout_s: float = 10.0
    max_retries: int = 2
    
    @abstractmethod
    async def run(self, args: BaseModel, ctx: TurnContext) -> dict:
        ...

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Tool] = {}
        
    def register(self, tool: Tool):
        self._tools[tool.name] = tool
        
    def get(self, name: str) -> Optional[Tool]:
        return self._tools.get(name)
        
    def schemas(self) -> list[dict]:
        res = []
        for name, tool in self._tools.items():
            schema = tool.args_model.model_json_schema()
            res.append({
                "name": tool.name,
                "description": tool.description,
                "parameters": {
                    "type": "object",
                    "properties": schema.get("properties", {}),
                    "required": schema.get("required", [])
                }
            })
        return res

registry = ToolRegistry()
