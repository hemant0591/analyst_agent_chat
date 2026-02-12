from dataclasses import dataclass, field
from typing import List, Any

@dataclass
class AgentMemory:
    research_notes: List[str] = field(default_factory=list)
    analysis_notes: List[str] = field(default_factory=list)
    review_notes: List[str] = field(default_factory=list)
    final_output: str = ""

    def add_research(self, note: str):
        self.research_notes.append(note)

    def add_analysis(self, note: str):
        self.analysis_notes.append(note)

    def add_review(self, note: str):
        self.review_notes.append(note)