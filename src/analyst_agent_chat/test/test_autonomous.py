from analyst_agent_chat.engines.autonomous_engine import AutonomousEngine
from analyst_agent_chat.core.registry import ToolRegistry
from analyst_agent_chat.core.tool import Tool
from analyst_agent_chat.core.tools import search_web, read_file, calculate, llm_reason

tool_registry = ToolRegistry()

tool_registry.register(
    Tool(
        name="search_web",
        description="Search the internet for current information.",
        function=search_web,
        allowed_modes=["autonomous"],
    )
)

tool_registry.register(
    Tool(
        name="read_file",
        description="Read a local file.",
        function=read_file,
        allowed_modes=["autonomous"],
    )
)

tool_registry.register(
    Tool(
        name="calculate",
        description="Evaluate a math expression.",
        function=calculate,
        allowed_modes=["autonomous"],
    )
)

tool_registry.register(
    Tool(
        name="llm_reason",
        description="Use the LLM for reasoning.",
        function=llm_reason,
        allowed_modes=["autonomous"],
    )
)

engine = AutonomousEngine(tool_registry)

result = engine.run("How much can I save using a small local LLM?")
print("\nFINAL RESULT:")
print(result)