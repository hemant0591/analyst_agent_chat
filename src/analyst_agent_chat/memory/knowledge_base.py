import os
import json
import uuid
import numpy as np
from datetime import datetime, timezone
from analyst_agent_chat.core.llm import get_embeddings

META_PATH = "knowledge_meta.json"
VECTOR_PATH = "knowledge_vectors.npy"
INDEX_PATH = "knowledge_index.json"

class KnowledgeBase:
    def __init__(self):
        self.entries = {}  # id: metadata
        self.id_to_index = {}  # id: row_index
        self.index_to_id = []  # row_index -> id
        self.embeddings = None
        self._load()        

    def _load(self):
        if os.path.exists(META_PATH):
            with open(META_PATH, "r") as f:
                self.entries = json.load(f)

        if os.path.exists(INDEX_PATH):
            with open(INDEX_PATH, "r") as f:
                self.id_to_index = json.load(f)
                self.index_to_id = [None] * len(self.id_to_index)
                for id_, idx in self.id_to_index.items():
                    self.index_to_id[idx] = id_

        if os.path.exists(VECTOR_PATH):
            self.embeddings = np.load(VECTOR_PATH)
        else:
            self.embeddings = None
        
    def save_entry(self, task, result, intent, confidence):
        if confidence < 8:
            return
        
        embedding = np.array(get_embeddings(task), dtype=np.float32)
        embedding = self._normalize(embedding)

        entry_id = str(uuid.uuid4())

        metadata = {
            "task": task,
            "result": result,
            "intent": intent,
            "confidence": confidence,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        self.entries[entry_id] = metadata

        if self.embeddings is None:
            self.embeddings = embedding.reshape(1,-1)
            row_index = 0
        else:
            row_index = len(self.embeddings)
            self.embeddings = np.vstack([self.embeddings, embedding])

        self.id_to_index[entry_id] = row_index
        self.index_to_id.append(entry_id)

        self._persist()

    def _persist(self):
        with open(META_PATH, "w") as f:
            json.dump(self.entries, f, indent=2)

        with open(INDEX_PATH, "w") as f:
            json.dump(self.id_to_index, f, indent=2)

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
        
        query = query.lower().strip()
        query_embedding = np.array(get_embeddings(query), dtype=np.float32)
        query_embedding = self._normalize(query_embedding)

        similarities = self.embeddings @ query_embedding
        
        best_id = None
        best_score = -1

        for entry_id, metadata in self.entries.items():
            if metadata["intent"] != intent:
                continue

            idx = self.id_to_index[entry_id]
            score = similarities[idx]

            if score > best_score:
                best_score = score
                best_id = entry_id

        #print(f"[KB] Best similarity: {best_score:.3f}")

        if best_score >= threshold and best_id:
            return self.entries[best_id]["result"]

        return None