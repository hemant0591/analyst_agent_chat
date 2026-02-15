from analyst_agent_chat.core.planner import create_plan
from analyst_agent_chat.core.tools import llm_reason
from analyst_agent_chat.memory.agent_memory import AgentMemory
import json

class Analyst:
    def __init__(self, tool_registry):
        self.tool_registry = tool_registry
        self.role_prompt = """
            You are an Analyst.

            Based on provided research observations:
            - Extract pros
            - Extract cons
            - Formulate a recommendation

            Do NOT perform SEARCH.
            Do NOT read files.
            Only reason from given observations.
        """

    def run(self, memory: AgentMemory):
        if not memory.research_notes:
            memory.add_analysis({
            "error": "No research available."
            })
            return memory
    
        context = "\n\n".join(memory.research_notes)

        prompt = f"""
            You are an Analyst.

            Based on the following research:

            {context}

            Return ONLY valid JSON in this exact format:

            {{
            "pros": ["..."],
            "cons": ["..."],
            "recommendation": "..."
            }}

            Do not include any explanation outside JSON.
            """
        reasoning_tool = self.tool_registry.get("llm_reason")
        result = reasoning_tool.execute(prompt, [])

        try:
            parsed = json.loads(result)
            memory.add_analysis(parsed)

        except Exception:
            # JSON repair attempt
            repair_prompt = f"""
                The following output was supposed to be valid JSON but is not.

                Fix it and return ONLY valid JSON in this format:

                {{
                "pros": ["..."],
                "cons": ["..."],
                "recommendation": "..."
                }}

                Output:
                {result}
            """

            repaired = reasoning_tool.execute(repair_prompt, [])
            try:
                parsed = json.loads(repaired)
                memory.add_analysis(parsed)
            except Exception:
                memory.add_analysis({
                    "error": "Invalid JSON",
                    "raw_output": result
                })

        return memory