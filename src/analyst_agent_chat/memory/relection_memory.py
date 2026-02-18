import os
import json
import uuid
import numpy as np
from datetime import datetime, timezone
from analyst_agent_chat.core.llm import get_embeddings

REFLECTION_META = "reflection_meta.json"
REFLECTION_VECTORS = "reflection_vectors.npy"

class ReflectionMemory:
    def __init__(self):
        self.entries = {}  # id : metadata
        self.id_to_index = {}  # id : index
        self.index_to_id = []
        self.embeddings = None
        self._load()

    def _load(self):
        if os.path.exists(REFLECTION_META):
            with open(REFLECTION_META, "r") as f:
                self.entries = json.load(f)

        if os.path.exists(REFLECTION_VECTORS):
            self.embeddings = np.load(REFLECTION_VECTORS)

        # rebuild index mappings
        if self.entries:
            self.id_to_index = {
                id: idx for idx, id in enumerate(self.entries.keys())
            }

            self.index_to_id = list(self.entries.keys())

    def _persist(self):
        with open(REFLECTION_META, "w") as f:
            json.dump(self.entries, f, indent=2)

        if self.embeddings is not None:
            np.save(REFLECTION_VECTORS, self.embeddings)

    def _normalize(self, vec):
        norm = np.linalg.norm(vec)

        if norm == 0:
            return vec
        
        return vec / norm
    
    def save_reflections(self, task, intent, review_dict):
        if review_dict.get("confidence_score", 10) >= 8:
            return
        
        embedding = np.array(get_embeddings(task), dtype=np.float32)
        embedding = self._normalize(embedding)
        
        entry_id = str(uuid.uuid4())

        self.entries[entry_id] = {
            "task": task,
            "intent": intent,
            "weaknesses": review_dict["weaknesses"],
            "suggested_improvements": review_dict["suggested_improvements"],
            "confidence": review_dict["confidence_score"],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        if self.embeddings is None:
            self.embeddings = embedding.reshape(1,-1)
        else:
            self.embeddings = np.vstack([self.embeddings, embedding])

        self.id_to_index[entry_id] = len(self.index_to_id)
        self.index_to_id.append(entry_id)

        self._persist()

    def search(self, task, intent, threshold=0.8, top_k=2):
        if self.embeddings is None:
            return
        
        query_embedding = np.array(get_embeddings(task), dtype=np.float32)
        query_embedding = self._normalize(query_embedding)

        similarities = self.embeddings @ query_embedding

        scored = []

        for entry_id, metadata in self.entries.items():
            if metadata["intent"] != intent:
                continue

            idx = self.id_to_index[entry_id]

            score = similarities[idx]

            if score >= threshold:
                scored.append((score, metadata))

        scored.sort(reverse=True, key=lambda x: x[0])

        return [item[1] for item in scored[:top_k]]
        