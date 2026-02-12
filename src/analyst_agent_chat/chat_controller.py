from analyst_agent_chat.chat_memory import ChatMemory
from analyst_agent_chat.tools import llm_reason
from analyst_agent_chat.coordinator import Coordinator
from analyst_agent_chat.agents.router import Router

class ChatController:
    def __init__(self):
        self.memory = ChatMemory()
        self.coordinator = Coordinator()
        self.route = Router()

    def handle_message(self, user_message: str) -> str:

        route = self.route.route(user_message)

        if route in ["analyze", "research"]:
            memory = self.coordinator.run(user_message)
            response = memory.final_output
        else:
            response = llm_reason(user_message, self.memory.messages)

        self.memory.add_user(user_message)
        self.memory.add_assistant(response)

        return response
