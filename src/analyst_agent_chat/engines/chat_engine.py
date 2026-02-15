from analyst_agent_chat.engines.base_engine import BaseEngine

class ChatEngine(BaseEngine):
    def __init__(self, tool_registry):
        self.tool_registry = tool_registry

    def run(self, task: str, context: str | None = None):
        reasoning_tool = self.tool_registry.get("llm_reason")
        result = reasoning_tool.execute(task, context)
        return {
            "final_output": result,
            "confidance_score": 10
        }