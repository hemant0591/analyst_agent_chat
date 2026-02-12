from dataclasses import dataclass, field
from typing import List, Dict

# this stores conversation
@dataclass
class ChatMemory:
    messages: List[Dict[str,str]] = field(default_factory=list)

    def add_user(self, content: str):
        self.messages.append({"role": "user", "content": content})

    def add_assistant(self, content: str):
        self.messages.append({"role": "assistant", "content": content})