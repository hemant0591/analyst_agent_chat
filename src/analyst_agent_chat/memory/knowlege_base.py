import json
import os
from datetime import datetime, timezone

class KnowledgeBase:
    def __init__(self, path="knowledge.json"):
        self.path = path
        self.data = self._load()

    def _load(self):
        if not os.path.exists(self.path):
            return []
        
        with open(self.path, "r") as f:
            return json.load(f)
        
    def save_entry(self, task, result, metadata=None):
        entry = {
            "task": task,
            "result": result,
            "metadata": metadata or {},
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        self.data.append(entry)
        self._persist()

    def _persist(self):
        with open(self.path, "w") as f:
            json.dump(self.data, f, indent=2)

    def search(self, query):
        matches = []
        for entry in self.data:
            if query.lower() in entry["task"].lower():
                matches.append(entry)

        return matches    