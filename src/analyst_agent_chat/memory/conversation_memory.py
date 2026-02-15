from dataclasses import dataclass, field
from typing import List, Dict, Optional
from analyst_agent_chat.core.tools import llm_reason

MAX_RECENT_MESSAGES = 8

@dataclass
class ChatMemory:
    recent_messages: List[Dict[str, str]] = field(default_factory=list)
    conversation_summary: str = ''
    user_profile: Dict[str, str] = field(default_factory=dict)

    def add_user(self, content: str):
        self._extract_profile_info(content)
        self._add_message({"role": "user", "content": content})

    def add_assistant(self, content: str):
        self._add_message({"role": "assistant", "content": content})

    def _add_message(self, message: Dict[str, str]):
        self.recent_messages.append(message)

        if len(self.recent_messages) > MAX_RECENT_MESSAGES:
            self._summarize_and_trim()

    def _summarize_and_trim(self):
        "Keep only the recent messages, summarize the older ones."

        old_messages = self.recent_messages[:-4]
        recent_kept = self.recent_messages[-4:]

        summary_prompt = f"""
        Summarize the following conversation history concisely.

        Previous summary:
        {self.conversation_summary}

        New messages to summarize:
        {old_messages}
        Produce an updated summary preserving important context.
        """

        updated_summary = llm_reason(summary_prompt, [])
        
        self.conversation_summary = updated_summary
        self.recent_messages = recent_kept

    def _extract_profile_info(self, text: str):
        if "my name is" in text.lower():
            name = text.split("is")[-1].strip()
            self.user_profile["name"] = name

    def get_context_for(self, engine_type: str):
        """
        Return execution context tailored to engine type.
        """
        if engine_type == "chat":
            return self._get_chat_context()
        if engine_type == "lookup":
            return self._get_lookup_context()
        if engine_type == "deep_analysis":
            return self._get_analysis_context()
        if engine_type == "autonomous":
            return self._get_autonomous_context()
        
        return self.get_llm_context()


    def get_llm_context(self):
        """
        Build structured context for LLM calls.
        """
        messages = []

        if self.conversation_summary:
            messages.append({"role": "system", "content": f"Conversation summary so far:\n{self.conversation_summary}"})

        messages.extend(self.recent_messages)

        return messages
    
    # this is now redundant
    def get_intent_context(self):
        """
        Get context for intent resolver
        """
        intent_messages = []

        if self.conversation_summary:
            intent_messages.append({"role":"system", "content": f"Conversation summary so far:\n{self.conversation_summary}"})

        intent_messages.extend(self.recent_messages[-2:])

        return intent_messages
    
    def _get_chat_context(self):
        context = []
        
        if self.conversation_summary:
            context.append({"role":"system", "content": f"Conversation summary so far:\n{self.conversation_summary}"})
        
        context.extend(self.recent_messages[-4:])

        return context
    
    def _get_lookup_context(self):
        context = []
        
        if self.conversation_summary:
            context.append({"role":"system", "content": f"Conversation summary so far:\n{self.conversation_summary}"})
        
        context.extend(self.recent_messages[-2:])

        return context

    def _get_analysis_context(self):
    # Usually resolved_task is standalone (enhance later with knowledge base)
        return []
    
    def _get_autonomous_context(self):
        context = []
        
        if self.conversation_summary:
            context.append({"role":"system", "content": f"Conversation summary so far:\n{self.conversation_summary}"})
        
        context.extend(self.recent_messages[-6:])

        return context 