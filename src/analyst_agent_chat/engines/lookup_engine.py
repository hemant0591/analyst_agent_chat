from analyst_agent_chat.engines.base_engine import BaseEngine

class LookupEngine(BaseEngine):
    def __init__(self, tool_registry):
        self.tool_registry = tool_registry

    def run(self, task: str, context: str | None = None):
        search_tool = self.tool_registry.get("search_web")
        search_results = search_tool.execute(task, [])

        prompt = f"""
            You must answer using ONLY the search results provided.

            If the search results do not contain reliable, recent information,
            say that verification is inconclusive.

            Search results:
            {search_results}

            Question:
            {task}

            Return a short factual answer.
            Do NOT rely on prior knowledge.
            """

        reasoning_tool = self.tool_registry.get("llm_reason")
        result = reasoning_tool.execute(prompt, context)

        return {
            "final_output": result,
            "confidance_score": 10
        }