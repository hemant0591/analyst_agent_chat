from analyst_agent_chat.memory import AgentMemory
from analyst_agent_chat.tools import llm_reason
import json


class Presenter:
    def run(self, memory: AgentMemory) -> AgentMemory:
        analysis = memory.analysis_notes[-1] if memory.analysis_notes else {}
        review = memory.review_notes[-1] if memory.review_notes else {}

        summary_prompt = f"""
            You are a presentation assistant.

            Summarize the following structured analysis and review into a concise, 
            clear executive summary under 200 words.

            Analysis:
            {json.dumps(analysis, indent=2)}

            Review:
            {json.dumps(review, indent=2)}

            Keep it:
            - Short
            - Clear
            - Actionable
            - Non-technical

            Return plain text only.
        """

        summary = llm_reason(summary_prompt, [])

        memory.final_output = summary

        return memory
