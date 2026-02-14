from analyst_agent_chat.planner import create_plan
from analyst_agent_chat.memory import AgentMemory

class Researcher:
    def __init__(self, tool_registry):
        self.tool_registry = tool_registry
        self.role_prompt = """
            You are a Research Specialist.

            Your job is to gather factual information using SEARCH and READ_FILE steps.
            Do NOT analyze or recommend.
            Only collect relevant information.
        """

    def run(self, task: str):
        memory = AgentMemory()
        plan = create_plan(task, self.tool_registry, system_prompt=self.role_prompt)

        observations = []

        for step in plan:
            if not self.tool_registry.get(step["action"]):
                raise ValueError("Planner selected unknown tool")
            tool = self.tool_registry.get(step["action"])
            result = tool.execute(step["input"], observations)
            memory.add_research(result)

        return memory
