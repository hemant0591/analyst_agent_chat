import os
from openai import OpenAI
import json

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def create_plan(task: str, system_prompt: str | None = None) -> list[str]:
    """
    Use an LLM to convert a task into a step-by-step plan.
    """

    base_prompt = f"""
        Break task into steps.

        Return a JSON array of objects with this structure:
        {{
            "action": "search_web" | "read_file" | "calculate" | "llm_reason",
            "input": "..."
        }}
        Only return valid JSON.
        No explanation.
    """

    if system_prompt:
        full_prompt = system_prompt + "\n\n" + base_prompt + f"\nTask: {task}"
    else:
        full_prompt = base_prompt + f"\nTask: {task}"

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": full_prompt}],
        temperature=0.2,
    )

    text = response.choices[0].message.content.strip()

    steps = json.loads(text)

    if not steps:
        raise ValueError("Planner failed to produce steps")

    return steps

# not needed anymore
# def is_plan_complete(state) -> bool:
#     return state.current_step >= len(state.plan)
