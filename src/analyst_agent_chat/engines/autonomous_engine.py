import json
from analyst_agent_chat.engines.base_engine import BaseEngine

MAX_RETRY_STEPS = 6

class AutonomousEngine(BaseEngine):
    def __init__(self, tool_registry):
        self.tool_registry = tool_registry

    def run(self, task:str, context: str | None = None):
        observations = []
        curr_steps = 0

        while curr_steps < MAX_RETRY_STEPS:
            # execution logic
            prompt = self._build_prompt(task, observations)

            reasoning_tool = self.tool_registry.get("llm_reason")
            decision_raw = reasoning_tool.execute(prompt, [])

            # parse decision
            try:
                decision = json.loads(decision_raw)
            except Exception:
                return {
                    "final_output": f"Failed to parse decision JSON:\n{decision_raw}",
                    "confidance_score": 0,
                        }
            
            if "action" not in decision:
                return {
                    "final_output": "Invalid decision: missing 'action'.",
                    "confidance_score": 0,
                }
            
            action = decision["action"]

            if action == "finish":
                return {
                    "final_output": decision.get("final_answer", "No final answer provided."),
                    "confidance_score": 9,
                    }
            
            tool = self.tool_registry.get(action)

            if not tool:
                return {
                    "final_output": "Invalid decision: missing 'action'.",
                    "confidance_score": 0,
                        }
            
            # print(f"Step: {curr_steps + 1}")
            # print(f"Chosen action: {action}")
            
            result = tool.execute(decision.get("input", ""), observations)

            # print("Tool result (truncated):", result[:300])

            if observations and decision.get("input") in observations[-1]:
                return {
                    "final_output": "Repeated action detected. Stopping.",
                    "confidance_score": 0,
                        }

            observations.append(result)

            curr_steps += 1

        return {
            "final_output": "Max_steps reached without conclusion",
            "confidance_score": 0,
                }
    
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