from analyst_agent_chat.memory.conversation_memory import ChatMemory
from analyst_agent_chat.core.tools import llm_reason, search_web, read_file
from analyst_agent_chat.routing.intent_resolver import IntentResolver
from analyst_agent_chat.core.tool import Tool
from analyst_agent_chat.core.registry import ToolRegistry
from analyst_agent_chat.engines.autonomous_engine import AutonomousEngine
from analyst_agent_chat.core.engine_registry import EngineRegistry
from analyst_agent_chat.memory.knowledge_base import KnowledgeBase

class ChatController:
    def __init__(self):
        self.tool_registry = ToolRegistry()
        self.engine_registry = EngineRegistry(self.tool_registry)
        self.knowledge_base = KnowledgeBase()

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
        if engine.is_cacheable:
            cached = self.knowledge_base.search(resolved_task, intent)
            if cached:
                #print("Getting cached result")
                return cached
        result = engine.run(resolved_task, execution_context)
        if engine.is_cacheable:
            self.knowledge_base.save_entry(
                task= resolved_task,
                result= result["final_output"],
                intent=intent,
                confidence=result["confidence_score"]
            )
        response = result["final_output"]

        self.memory.add_user(user_message)
        self.memory.add_assistant(response)

        return response


