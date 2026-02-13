from analyst_agent_chat.chat_memory import ChatMemory
from analyst_agent_chat.tools import llm_reason, search_web, read_file
from analyst_agent_chat.coordinator import Coordinator
from analyst_agent_chat.agents.intent_resolver import IntentResolver
from analyst_agent_chat.core.tool import Tool
from analyst_agent_chat.core.tool_registry import ToolRegistry

class ChatController:
    def __init__(self):
        self.tool_registry = ToolRegistry()
        
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

        self.coordinator = Coordinator(self.tool_registry)
        self.memory = ChatMemory()
        self.resolver = IntentResolver()

    def handle_message(self, user_message: str) -> str:
        intent_messages = self.memory.get_intent_context()
        resolution = self.resolver.resolve(user_message, intent_messages)

        intent = resolution["intent"]
        resolved_task = resolution["resolved_task"]

        #print("Intent: ", intent) # comment out later

        if intent == "deep_analysis":
            memory = self.coordinator.run(resolved_task)
            response = memory.final_output
        elif intent == "lookup":
            response = self.simple_lookup(resolved_task)
        else:
            response = response = llm_reason(resolved_task, self.memory.get_llm_context())

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


