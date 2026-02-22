import json
from analyst_agent_chat.engines.base_engine import BaseEngine
from analyst_agent_chat.core.logger import get_logger

MAX_RETRY_STEPS = 6
CONFIDENCE_THRESHOLD = 8

logger = get_logger("autonomous_engine")

class AutonomousState:
    def __init__(self, task):
        self.task = task
        self.observations = []
        self.actions = []
        self.reflections = []
        self.steps = 0
        self.action_history = []

class AutonomousEngine(BaseEngine):
    def __init__(self, tool_registry, reflection_memory):
        self.tool_registry = tool_registry
        self.reflection_memory = reflection_memory
        self.is_cacheable = True

    def run(self, task:str, context: str | None = None):
        state = AutonomousState(task)

        while state.steps < MAX_RETRY_STEPS:
            state.steps += 1
            
            decision = self._decide_next_action(state)

            if self._is_repeating(state, decision):
                state.observations.append(
                   f"Detected repetition of {decision['action']}. Choose a different strategy."
                )
                continue

            if decision["action"] == "finish":
                final_answer = decision.get("final_answer", "")

                review = self._review_answer(state, final_answer)
                state.reflections.append(review)

                score = review.get("confidence_score", 5)

                if score >= CONFIDENCE_THRESHOLD:
                    return {
                        "final_output": final_answer,
                        "confidence_score": score
                    }
                                
                improvement_signal = f"""
                    In previous attempts, similar tasks had these weaknesses:
                    {review['weaknesses']}

                    Suggested improvements:
                    {review['suggested_improvements']}

                    Avoid repeating these mistakes.
                    """
                state.observations.append(improvement_signal)

                self.reflection_memory.save_reflections(task=state.task, intent="autonomous", review_dict=review)
                continue

            # tool execution
            tool = self.tool_registry.get(decision["action"])

            if not tool:
                return {
                    "final_output": "Unknown tool selected.",
                    "confidence_score": 3
                    }
            
            state.actions.append(decision)
            state.action_history.append(decision)

            result = tool.execute(decision["input"], state.observations)
            state.observations.append(result)

            logger.info(
                "Tool executed",
                extra={
                    "extra_data": {
                        "tool": decision["action"],
                        "input": decision["input"],
                    }
                },
            )

        # Fallback if max steps hit
        return {
            "final_output": self._summarize_state(state),
            "confidence_score": 6
        }


    def _decide_next_action(self, state):
        tools = self.tool_registry.get_all_tools()

        tool_descriptions = "\n\n".join([f"Tool: {tool.name}\nDescription: {tool.description}" for tool in tools])

        past_reflections = self.reflection_memory.search(task=state.task, intent="autonomous")

        prompt = f"""
        You are an autonomous reasoning engine.

        Task:
        {state.task}

        Observations so far:
        {state.observations}

        Available tools:
        {tool_descriptions}

        Previous similar task reflections (weaknesses and suggested improvements):
        {past_reflections}

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
    
    def _review_answer(self, state, answer):
        prompt = f"""
        Review the final answer for the task.

        Task:
        {state.task}

        Answer:
        {answer}

        Return ONLY valid JSON:

        {{
            "strengths": ["..."],
            "weaknesses": ["..."],
            "suggested_improvements": ["..."],
            "confidence_score": 1-10
        }}

        Do NOT wrap the JSON in markdown.
        Do NOT include any explanation.
        Return raw JSON only.
        """

        reasoning_tool = self.tool_registry.get("llm_reason")
        response = reasoning_tool.execute(prompt, [])

        cleaned = response.strip()
        
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`")
            cleaned = cleaned.replace("json", "").strip()

        try:
            return json.loads(cleaned)
        except:
            return {
                "strengths": [],
                "weaknesses": ["Review parsing failed"],
                "suggested_improvements": [],
                "confidence_score": 5
            }

    def _is_repeating(self, state, decision):
        """
        Detects repeated tool use pattern
        """
        if not state.action_history:
            return False
        
        last_action = state.action_history[-1]

        if (
            last_action["action"] == decision["action"] and 
            last_action["input"] == decision["input"]):
            return True
        
        return False