import json

class AutonomousEngine:
    def __init__(self, tool_registry, max_retry_steps=6):
        self.tool_registry = tool_registry
        self.max_retry_steps = max_retry_steps

    def run(self, task:str):
        observations = []
        curr_steps = 0

        while curr_steps < self.max_retry_steps:
            # execution logic
            prompt = self._build_prompt(task, observations)

            reasoning_tool = self.tool_registry.get("llm_reason")
            decision_raw = reasoning_tool.execute(prompt, [])

            # parse decision
            try:
                decision = json.loads(decision_raw)
            except Exception:
                return f"Failed to parse decision JSON:\n{decision_raw}"
            
            if "action" not in decision:
                return "Invalid decision: missing 'action'."
            
            action = decision["action"]

            if action == "finish":
                return decision.get("final_answer", "No final answer provided.")
            
            tool = self.tool_registry.get(action)

            if not tool:
                return "Invalid decision: missing 'action'."
            
            result = tool.execute(decision.get("input", ""), observations)

            observations.append(result)

            curr_steps += 1

        return "Max_steps reached without conclusion"
    
    def _build_prompt(self, task: str, observations: list[str]) -> str:
        tools = self.tool_registry.get_all_tools()

        tool_descriptions = "\n\n".join([f"Tool: {tool.name}\nDescription: {tool.description}" for tool in tools])

        return f"""
            You are an autonomous AI agent.

            Task:
            {task}

            Observations so far:
            {observations if observations else "None"}

            Available tools:
            {tool_descriptions}

            Choose ONE action.

            Return JSON in this format:

            {{
            "action": "<tool_name>" OR "finish",
            "input": "...",
            "final_answer": "..." (only if finishing)
            }}

            Do not explain.
            Return valid JSON only.
            """