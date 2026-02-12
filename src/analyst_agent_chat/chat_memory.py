from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class ChatMemory:
    messages: List[Dict[str, str]] = field(default_factory=list)
    user_profile: Dict[str, str] = field(default_factory=dict)

    def add_user(self, content: str):
        self.messages.append({"role": "user", "content": content})
        self._extract_profile_info(content)

    def add_assistant(self, content: str):
        self.messages.append({"role": "assistant", "content": content})

    def _extract_profile_info(self, text: str):
        # naive example (we’ll improve later)
        if "my name is" in text.lower():
            name = text.split("is")[-1].strip()
            self.user_profile["name"] = name

    def get_context(self):
        return {
            "messages": self.messages,
            "profile": self.user_profile
        }
