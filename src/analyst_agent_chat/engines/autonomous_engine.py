import json
from analyst_agent_chat.engines.base_engine import BaseEngine

MAX_RETRY_STEPS = 6

class AutonomousState:
    def __init__(self, task):
        self.task = task
        self.observations = []
        self.reasoning_trace = []
        self.steps = 0

class AutonomousEngine(BaseEngine):
    def __init__(self, tool_registry):
        self.tool_registry = tool_registry

    def run(self, task:str, context: str | None = None):
        state = AutonomousState(task)

        while state.steps < MAX_RETRY_STEPS:
            state.steps += 1
            
            decision = self._decide_next_action(state)

            if decision["action"] == "finish":
                return {
                    "final_output": decision["final_answer"],
                    "condidence_score": 9
                }

            tool = self.tool_registry.get(decision["action"])

            if not tool:
                return {
                    "final_output": "Unknown tool selected.",
                    "condidence_score": 3
                    }

            result = tool.execute(decision["input"], [])

            state.observations.append(result)

        # Fallback if max steps hit
        return {
            "final_output": self._summarize_state(state),
            "condidence_score": 6
        }


    def _decide_next_action(self, state):
        tools = self.tool_registry.get_all_tools()

        tool_descriptions = "\n\n".join([f"Tool: {tool.name}\nDescription: {tool.description}" for tool in tools])

        prompt = f"""
        You are an autonomous reasoning engine.

        Task:
        {state.task}

        Observations so far:
        {state.observations}

        Available tools:
        {tool_descriptions}

        Decide next step.

        You may:
        - Use a tool
        - Or finish and provide final answer

        Return JSON:

        {{
            "action": "<tool_name or finish>",
            "input": "...",
            "final_answer": "..." (only if finish)
        }}
        """

        reasoning_tool = self.tool_registry.get("llm_reason")
        response = reasoning_tool.execute(prompt, [])
        
        return json.loads(response)

    def _summarize_state(self, state):
        prompt = f"""
        Based on the task and observations, provide the best possible answer.

        Task:
        {state.task}

        Observations:
        {state.observations}
        """
        reasoning_tool = self.tool_registry.get("llm_reason")
        response = reasoning_tool.execute(prompt, []) 
        return response