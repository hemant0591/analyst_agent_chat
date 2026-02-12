import json
from analyst_agent_chat.tools import llm_reason

class Router:
    def route(self, user_message: str) -> str:
        prompt = f"""
            You are a routing classifier.

            Classify the user request into ONE of these categories:

            - chat → simple conversation or short answer
            - analysis → requires structured multi-agent deep analysis
            - research → requires web search or data gathering

            Return ONLY valid JSON in this format:

            {{
            "route": "chat" | "analysis" | "research"
            }}

            User request:
            {user_message}
        """
         
        result = llm_reason(prompt, [])

        try:
            parsed = json.loads(result)
            return parsed.get("route", "chat")
        except:
            return "chat"

    