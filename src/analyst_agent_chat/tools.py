import os
from openai import OpenAI
from ddgs import DDGS
from pathlib import Path
import re

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_file_path(step: str) -> str | None:
    """
    Extract file paths like report.txt, data.csv, notes.md from a step.
    """
    match = re.search(r"\b[\w\-./]+\.(txt|md|csv)\b", step)
    if match:
        return match.group(0)
    return None


def llm_reason(prompt: str, context: list[str]) -> str:
    """
    Use the LLM to reason about a single step.
    """

    full_prompt = f"""
        {prompt}

        Previous reasoning context:
        {context}
    """

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )

    return response.choices[0].message.content.strip()


def calculate(expression: str) -> str:
    """
    Safely evaluate simple arithmetic expressions.
    """
    try:
        result = eval(expression, {"__builtins__": {}})
        return f"Calculation result: {result}"
    except Exception as e:
        return f"Calculation error: {e}"


def search_web(query: str) -> str:
    """
    Perform web search and return structured results.
    """
    from ddgs import DDGS

    results = []

    with DDGS() as ddgs:
        for r in ddgs.text(query, max_results=3):
            results.append({
                "title": r["title"],
                "snippet": r["body"],
                "url": r.get("href", "")
            })

    if not results:
        return "No search results found."

    formatted = "\n\n".join(
        f"Title: {r['title']}\nSnippet: {r['snippet']}\nURL: {r['url']}"
        for r in results
    )

    return f"Search Results:\n\n{formatted}"



def read_file(path: str) -> str:
    """
    Read a file and return its contents
    """
    try:
        filepath = Path(path)
        if not filepath.exists():
            return "File doesn't exists in this path."
        
        return filepath.read_text()[:3000]
    
    except Exception as e:
        return f"Could not open file: {e}"



def execute_step(step: str, observations: list[str]) -> str:
    step = step.strip()

    if 'SEARCH' in step:
        query = step.replace("SEARCH:", "").strip()
        return search_web(query)

    if 'READ_FILE' in step:
        file_path = step.replace("READ_FILE:", "").strip()
        return read_file(file_path)

    if 'CALCULATE' in step:
        expression = step.replace("CALCULATE:", "").strip()
        return calculate(expression)

    return llm_reason(step, observations)