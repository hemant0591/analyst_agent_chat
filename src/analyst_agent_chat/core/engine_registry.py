from analyst_agent_chat.engines.chat_engine import ChatEngine
from analyst_agent_chat.engines.lookup_engine import LookupEngine
from analyst_agent_chat.engines.deep_analysis_engine import DeepAnalysisEngine
from analyst_agent_chat.engines.autonomous_engine import AutonomousEngine

class EngineRegistry:
    def __init__(self, tool_registry, reflection_memory):
        self.engine = {
            "chat": ChatEngine(tool_registry),
            "lookup": LookupEngine(tool_registry),
            "deep_analysis": DeepAnalysisEngine(tool_registry, reflection_memory),
            "autonomous": AutonomousEngine(tool_registry, reflection_memory)
        }

    def get(self, intent: str):
        return self.engine.get(intent)

    
