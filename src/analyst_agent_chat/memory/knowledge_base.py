import json
import os
import numpy as np
from datetime import datetime, timezone
from analyst_agent_chat.core.llm import get_embeddings

META_PATH = "knowledge_meta.json"
VECTOR_PATH = "knowledge_vectors.npy"

class KnowledgeBase:
    def __init__(self):
        self.entries = []
        self.embeddings = None
        self._load()        

    def _load(self):
        if os.path.exists(META_PATH):
            with open(META_PATH, "r") as f:
                self.entries = json.load(f)

        if os.path.exists(VECTOR_PATH):
            self.embeddings = np.load(VECTOR_PATH)
        else:
            self.embeddings = None
        
    def save_entry(self, task, result, intent, confidence):
        if confidence < 8:
            return
        
        embedding = np.array(get_embeddings(task), dtype=np.float32)
        embedding = self._normalize(embedding)

        entry = {
            "task": task,
            "result": result,
            "intent": intent,
            "confidence": confidence,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        self.entries.append(entry)

        if not self.embeddings:
            self.embeddings = embedding.reshape(1,-1)
        else:
            self.embeddings = np.vstack([self.embeddings, embedding])

        self._persist()

    def _persist(self):
        with open(META_PATH, "w") as f:
            json.dump(self.entries, f, indent=2)

        if self.embeddings is not None:
            np.save(VECTOR_PATH, self.embeddings)

    def _normalize(self, vec):
        norm = np.linalg.norm(vec)
        if norm == 0:
            return vec
        return vec / norm

    def search(self, query, intent, threshold=0.85):
        if self.embeddings is None or len(self.entries) == 0:
            return None
        
        query_embedding = np.array(get_embeddings(query), dtype=np.float32)
        query_embedding = self._normalize(query_embedding)

        similarities = self.embeddings @ query_embedding

        valid_indices = [i for i, entry in enumerate(self.entries) if entry["intent"] == intent]

        if not valid_indices:
            return None
        
        best_idx = None
        best_score = -1

        for i in valid_indices:
            score = similarities[i]
            if score > best_score:
                best_score = score
                best_idx = i

        print(f"[KB] Best similarity: {best_score:.3f}")

        if best_score >= threshold:
            return self.entries[best_idx]["result"]

        return None