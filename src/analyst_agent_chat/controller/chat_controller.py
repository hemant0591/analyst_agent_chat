from analyst_agent_chat.memory.conversation_memory import ChatMemory
from analyst_agent_chat.core.tools import llm_reason, search_web, read_file
from analyst_agent_chat.routing.intent_resolver import IntentResolver
from analyst_agent_chat.core.tool import Tool
from analyst_agent_chat.core.registry import ToolRegistry
from analyst_agent_chat.engines.autonomous_engine import AutonomousEngine
from analyst_agent_chat.core.engine_registry import EngineRegistry

class ChatController:
    def __init__(self):
        self.tool_registry = ToolRegistry()
        self.engine_registry = EngineRegistry(self.tool_registry)

        self.tool_registry.register(
            Tool(
                name="search_web",
                description="Search the internet for current information.",
                function=search_web,
                allowed_modes=["lookup", "autonomous", "deep_analysis"],
            )
        )

        self.tool_registry.register(
            Tool(
                name="read_file",
                description="Read a file from disk.",
                function=read_file,
                allowed_modes=["autonomous", "deep_analysis"],
            )
        )

        self.tool_registry.register(
            Tool(
                name="llm_reason",
                description="Use the LLM for reasoning.",
                function=llm_reason,
                allowed_modes=["chat", "lookup", "autonomous", "deep_analysis"],
            )
        )

        self.memory = ChatMemory()
        self.resolver = IntentResolver()
        self.autonomous_engine = AutonomousEngine(self.tool_registry)

    def handle_message(self, user_message: str) -> str:
        intent_messages = self.memory.get_intent_context()
        resolution = self.resolver.resolve(user_message, intent_messages)

        intent = resolution["intent"]
        resolved_task = resolution["resolved_task"]

        execution_context = self.memory.get_context_for(intent)
        #print("Intent: ", intent) # comment out later
        engine = self.engine_registry.get(intent)
        result = engine.run(resolved_task, execution_context)
        response = result["final_output"]

        self.memory.add_user(user_message)
        self.memory.add_assistant(response)

        return response
    
    def simple_lookup(self, task: str) -> str:
        """
        Lightweight factual lookup without full pipeline.
        """
        search_tool = self.tool_registry.get("search_web")
        search_results = search_tool.execute(task)

        #print("Search results: ", search_results) # comment out later

        prompt = f"""
            You must answer using ONLY the search results provided.

            If the search results do not contain reliable, recent information,
            say that verification is inconclusive.

            Search results:
            {search_results}

            Question:
            {task}

            Return a short factual answer.
            Do NOT rely on prior knowledge.
            """

        return llm_reason(prompt, [])


