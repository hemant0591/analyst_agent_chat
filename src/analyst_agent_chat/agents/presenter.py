from analyst_agent_chat.memory.agent_memory import AgentMemory
from analyst_agent_chat.core.tools import llm_reason
import json


class Presenter:
    def __init__(self, tool_registry):
        self.tool_registry = tool_registry

    def run(self, memory: AgentMemory) -> AgentMemory:

        if not memory.analysis_notes:
            memory.final_output = "No analysis available."
            return memory

        analysis = memory.analysis_notes[-1]

        summary_prompt = f"""
            You are a presentation assistant.

            Convert the following structured analysis into a concise,
            clear answer suitable for a chatbot response.

            Do NOT mention reviewer feedback.
            Do NOT mention confidence score.
            Do NOT mention internal system steps.

            Keep it:
            - Clear
            - Direct
            - Helpful
            - Under 200 words

            Analysis:
            {json.dumps(analysis, indent=2)}

            Return plain text only.
        """
        reasoning_tool = self.tool_registry.get("llm_reason")
        summary = reasoning_tool.execute(summary_prompt, [])

        memory.final_output = summary

        return memory
