from analyst_agent_chat.agents.researcher import Researcher
from analyst_agent_chat.agents.analyst import Analyst
from analyst_agent_chat.agents.reviewer import Reviewer
from analyst_agent_chat.agents.presenter import Presenter
from analyst_agent_chat.engines.base_engine import BaseEngine
import json

MAX_RETRIES = 2
CONFIDENCE_THRESHOLD = 8

class DeepAnalysisEngine(BaseEngine):
    def __init__(self, tool_registry):
        self.tool_registry = tool_registry

    def run(self, task: str, context: str | None = None):
        retries = 0
        original_task = task

        while retries <= MAX_RETRIES:
            # retry logic
            if retries > 0:
                task = f"""
                        This is retry attempt #{retries}.

                        The previous attempt had low confidence.

                        Please:
                        - Be more thorough.
                        - Use broader search queries.
                        - Avoid unsupported claims.
                        - Provide clearer justification.

                        Original task:
                        {original_task}
                    """
            else:
                task = original_task

            researcher = Researcher(self.tool_registry)
            analyst = Analyst(self.tool_registry)
            reviewer = Reviewer(self.tool_registry)
            presenter = Presenter(self.tool_registry)

            memory = researcher.run(task)
            memory = analyst.run(memory)
            memory = reviewer.run(memory)

            last_review = memory.review_notes[-1]

            if isinstance(last_review, dict) and "confidence_score" in last_review:
                score = int(last_review["confidence_score"])
            else:
                score = 10

            if score < CONFIDENCE_THRESHOLD:
                analysis_object = memory.analysis_notes[-1]

                if isinstance(analysis_object, dict) and "error" in analysis_object:
                    retries += 1
                    continue

                refinement_prompt = f"""
                    The reviewer provided this critique:

                    {json.dumps(last_review, indent=2)}

                    Here is the previous analysis:

                    {json.dumps(analysis_object, indent=2)}

                    Improve the analysis accordingly.

                    Return ONLY valid JSON in this format:

                    {{
                        "pros": ["..."],
                        "cons": ["..."],
                        "recommendation": "..."
                    }}
                """

                reasoning_tool = self.tool_registry.get("llm_reason")
                improved = reasoning_tool.execute(refinement_prompt, [])

                try:
                    parsed = json.loads(improved)
                    memory.analysis_notes.append(parsed)
                except:
                    print("Refinement returned invalid json")

                # re-review after refinement
                memory = reviewer.run(memory)

                last_review = memory.review_notes[-1]

                if isinstance(last_review, dict) and "confidence_score" in last_review:
                    score = int(last_review["confidence_score"])
                else:
                    score = 10

            # check final confidance
            if score >= CONFIDENCE_THRESHOLD:
                memory = presenter.run(memory)
                return {
                   "final_output": memory.final_output,
                    "confidence_score": memory.review_notes[-1].get("confidence_score", 10)
                    }

            retries += 1

        memory = presenter.run(memory)
        return {
            "final_output": memory.final_output,
            "confidence_score": memory.review_notes[-1].get("confidence_score", 10)
        }




