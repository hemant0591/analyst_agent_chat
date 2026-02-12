from analyst_agent_chat.planner import create_plan
from analyst_agent_chat.tools import llm_reason
from analyst_agent_chat.memory import AgentMemory
import json

class Analyst:
    def __init__(self):
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
        
        result = llm_reason(prompt, [])

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

            repaired = llm_reason(repair_prompt, [])
            try:
                parsed = json.loads(repaired)
                memory.add_analysis(parsed)
            except Exception:
                memory.add_analysis({
                    "error": "Invalid JSON",
                    "raw_output": result
                })

        return memory