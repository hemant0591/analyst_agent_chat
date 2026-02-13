from analyst_agent_chat.memory import AgentMemory
from analyst_agent_chat.tools import llm_reason
import json

class Reviewer:
    def __init__(self, tool_regustry):
        self.tool_registry = tool_regustry
        self.role_prompt = """
            You are a critical reviewer.

            Your job is to:
            - Identify weak arguments
            - Detect unsupported claims
            - Highlight missing perspectives
            - Suggest improvements

            Do NOT perform new research.
            Only critique the provided analysis.
        """

    def run(self, memory: AgentMemory):
        if not memory.analysis_notes:
            memory.add_review("No analysis available to review.")
            return memory

        analysis_obj = memory.analysis_notes[-1] if memory.analysis_notes else {}

        analysis_text = json.dumps(analysis_obj, indent=2)

        review_prompt = f"""
            {self.role_prompt}

            Here is the analysis to review:

            {analysis_text}

            Return a JSON object in this exact format:

            {{
            "strengths": ["..."],
            "weaknesses": ["..."],
            "suggested_improvements": ["..."],
            "confidence_score": <number 1-10>
            }}

            Return only valid JSON.
        """

        reasoning_tool = self.tool_registry.get("llm_reason")
        critique = reasoning_tool.execute(review_prompt, memory.analysis_notes)

        try:
            parsed = json.loads(critique)
            memory.add_review(parsed)
        except Exception:
            memory.add_review({"error": "Invalid JSON", "raw_output": critique})

        return memory