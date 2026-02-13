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


def llm_reason(prompt: str, context: list[dict]) -> str:
    """"
    Use the LLM with optional chat history context.
    Context must be a list of chat-style message dicts.
    """

    messages = []

    # Only include context if it looks like valid chat history
    if context:
        for msg in context:
            if isinstance(msg, dict) and "role" in msg and "content" in msg:
                messages.append(msg)

    # Add current user message
    messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=messages,
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


def search_web(query: str, context=None) -> str:
    """
    Perform web search and return structured results.
    """
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



def read_file(path: str, context=None) -> str:
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

