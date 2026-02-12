from analyst_agent_chat.planner import create_plan
from analyst_agent_chat.tools import execute_step
from analyst_agent_chat.memory import AgentMemory

class Researcher:
    def __init__(self):
        self.role_prompt = """
            You are a Research Specialist.

            Your job is to gather factual information using SEARCH and READ_FILE steps.
            Do NOT analyze or recommend.
            Only collect relevant information.
        """

    def run(self, task: str):
        memory = AgentMemory()
        plan = create_plan(task=task, system_prompt=self.role_prompt)

        observations = []

        for step in plan:
            result = execute_step(step, observations)
            memory.add_research(result)

        return memory
