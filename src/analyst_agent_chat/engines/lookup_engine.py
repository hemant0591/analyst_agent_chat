from analyst_agent_chat.engines.base_engine import BaseEngine

class LookupEngine(BaseEngine):
    def __init__(self, tool_registry):
        self.tool_registry = tool_registry

    def run(self, task: str, context: str | None = None):
        search_tool = self.tool_registry.get("search_web")
        search_results = search_tool.execute(task, [])

        prompt = f"""
            You are a factual QA system.

            Answer the question clearly and directly.

            If search results contain a definitive answer, state it confidently.

            If multiple sources agree, assume the information is correct.

            Question:
            {task}

            Search Results:
            {search_results}

            Provide a short direct answer in one sentence.
            Do not say "verification inconclusive" unless absolutely no relevant information exists.

            Do NOT rely on prior knowledge.
            """

        reasoning_tool = self.tool_registry.get("llm_reason")
        result = reasoning_tool.execute(prompt, context)

        return {
            "final_output": result,
            "confidence_score": 10
        }