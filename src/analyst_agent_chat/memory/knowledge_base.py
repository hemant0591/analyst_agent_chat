import json
import os
from datetime import datetime, timezone
from analyst_agent_chat.core.llm import get_embeddings, cosine_similarity

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
        embedding = get_embeddings(task)
        entry = {
            "task": task,
            "result": result,
            "embedding": embedding,
            "metadata": metadata or {},
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        self.data.append(entry)
        self._persist()

    def _persist(self):
        with open(self.path, "w") as f:
            json.dump(self.data, f, indent=2)

    def search(self, query, threshold=0.85):
        query_embedding = get_embeddings(query)

        best_match = None
        best_score = 0

        for entry in self.data:
            score = cosine_similarity(entry["embedding"], query_embedding)
            if score > best_score:
                best_match = entry
                best_score = score

        if best_score >= threshold:
            return best_match

        return None