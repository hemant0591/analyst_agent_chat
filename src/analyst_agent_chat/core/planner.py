import os
from openai import OpenAI
import json

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def create_plan(task: str, tool_registry, system_prompt: str | None = None) -> list[str]:
    """
    Use an LLM to convert a task into a step-by-step plan.
    """

    tools = tool_registry.get_all_tools()
    tool_descriptions = "\n\n".join([f"Tool: {tool.name}\nDescription: {tool.description}" for tool in tools])

    base_prompt = f"""
        You can use the following tools:

        {tool_descriptions}

        Break task into steps.

        Return a JSON array of objects like this:

        [
        {{
            "action": "<tool_name>",
            "input": "..."
        }}
        ]

        Even if there is only one step, still return an array.
        Do NOT return a single object.
        
        Only use the tool names listed above.
        Return valid JSON.
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
    # print("###########Text############")
    # print(text)
    cleaned = text.strip()

    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        cleaned = cleaned.replace("json", "").strip()


    steps = json.loads(cleaned)

    if isinstance(steps, dict):
        steps = [steps]    

    for step in steps:
        if "action" not in step or "input" not in step:
            raise ValueError("Invalid planner step format.")

        if not tool_registry.get(step["action"]):
            raise ValueError(f"Planner selected unknown tool: {step['action']}")

    if not steps:
        raise ValueError("Planner failed to produce steps")

    return steps

# not needed anymore
# def is_plan_complete(state) -> bool:
#     return state.current_step >= len(state.plan)
