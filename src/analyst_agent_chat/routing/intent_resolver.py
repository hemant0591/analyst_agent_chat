import json
from analyst_agent_chat.core.tools import llm_reason

class IntentResolver:
    def resolve(self, user_message: str, conversation_history: list[dict]) -> dict:
        prompt = f"""
            You are an intent and task resolution system.

            Conversation so far:
            {conversation_history}

            Latest user message:
            {user_message}

            Your job:

            1. Determine intent:
            - chat → casual conversation or simple explanation
            - lookup → factual query, current events, time-sensitive info
            - deep_analysis → structured analytical report such as pros/cons, comparisons, advantages/disadvantages, and formal recommendations.
            - autonomous → strategic planning, estimation, forecasting, cost modeling, roadmap design, optimization, or open-ended multi-step problem solving.
                Examples:
                - "How much money could I save if..."
                - "Create a 6-month roadmap..."
                - "Compare X vs Y in depth"
                - "Design a strategy for..."
                - "Evaluate long-term impact of..."

            If the user asks for pros/cons or comparison → prefer deep_analysis.

            If the user asks for strategy, roadmap, cost estimation, or time-based planning → prefer autonomous.

            If question asks:
            - Who is...
            - What is the current...
            - When did...
            - Latest...
            - Today's...
            - Real-time facts

            Then intent MUST be "lookup".

            2. If the user message depends on earlier context,
            rewrite it into a fully standalone task.

            Return ONLY valid JSON:

            {{
            "intent": "...",
            "resolved_task": "..."
            }}
            """
        
        result = llm_reason(prompt, [])

        try:
            return json.loads(result)
        except:
            return {
                "intent": "chat",
                "resolved_task": user_message
            }