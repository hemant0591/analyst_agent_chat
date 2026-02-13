import json
from analyst_agent_chat.agents.researcher import Researcher
from analyst_agent_chat.agents.analyst import Analyst
from analyst_agent_chat.agents.reviewer import Reviewer
from analyst_agent_chat.agents.presenter import Presenter
from analyst_agent_chat.tools import llm_reason

MAX_RETRIES = 2
CONFIDENCE_THRESHOLD = 8


class Coordinator:
    def __init__(self, tool_registry):
        self.tool_registry = tool_registry
        
    def run(self, task: str):
        retries = 0
        original_task = task

        while retries <= MAX_RETRIES:

            # -------- Retry Injection --------
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

            # -------- Run Core Pipeline --------
            researcher = Researcher(self.tool_registry)
            analyst = Analyst(self.tool_registry)
            reviewer = Reviewer(self.tool_registry)
            presenter = Presenter(self.tool_registry)

            memory = researcher.run(task)
            memory = analyst.run(memory)
            memory = reviewer.run(memory)

            # -------- Reflection Loop --------
            last_review = memory.review_notes[-1]

            if isinstance(last_review, dict) and "confidence_score" in last_review:
                score = int(last_review["confidence_score"])
            else:
                score = 10

            # If confidence low → refine once
            if score < CONFIDENCE_THRESHOLD:

                #print(f"Low confidence ({score}). Attempting refinement...")

                analysis_obj = memory.analysis_notes[-1]

                if isinstance(analysis_obj, dict) and "error" in analysis_obj:
                    #print("Analysis invalid. Skipping refinement and retrying full pipeline.")
                    retries += 1
                    continue

                refinement_prompt = f"""
                    The reviewer provided this critique:

                    {json.dumps(last_review, indent=2)}

                    Here is the previous analysis:

                    {json.dumps(analysis_obj, indent=2)}

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
                    print("Refinement returned invalid JSON.")

                # Re-review after refinement
                memory = reviewer.run(memory)

                last_review = memory.review_notes[-1]

                if isinstance(last_review, dict) and "confidence_score" in last_review:
                    score = int(last_review["confidence_score"])
                else:
                    score = 10

            # -------- Check Final Confidence --------
            if score >= CONFIDENCE_THRESHOLD:
                #print(f"Final confidence: {score}")
                memory = presenter.run(memory)
                return memory

            #print(f"Confidence still low ({score}). Retrying full pipeline...")
            retries += 1

        #print("Max retries reached. Returning best attempt.")
        memory = presenter.run(memory)
        return memory
