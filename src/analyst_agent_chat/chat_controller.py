from analyst_agent_chat.chat_memory import ChatMemory
from analyst_agent_chat.tools import llm_reason
from analyst_agent_chat.coordinator import Coordinator

class ChatController:
    def __init__(self):
        self.memory = ChatMemory()
        self.coordinator = Coordinator()

    def handle_message(self, user_message: str) -> str:
        self.memory.add_user(user_message)

        if "analyze" in user_message or "pros and cons" in user_message:
            memory = self.coordinator.run(user_message)
            response = memory.final_output
        else:
            response = llm_reason(user_message, [])
            
        self.memory.add_assistant(response)

        return response
