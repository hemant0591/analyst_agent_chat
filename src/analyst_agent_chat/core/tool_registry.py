from typing import Dict, List
from .tool import Tool

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Tool] = {}

    def register(self, tool: Tool):
       self._tools[tool.name] = tool

    def get(self, name: str) -> Tool:
        return self._tools.get(name)
    
    def list_tools(self):
        return list(self._tools.keys())
    
    def get_tools_for_mode(self, mode: str) -> List[Tool]:
        return [tool for tool in self._tools if mode in tool.allowed_modes]