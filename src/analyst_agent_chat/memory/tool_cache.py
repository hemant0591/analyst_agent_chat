import os
import json
import hashlib

CACHE_FILE = "tool_cache.json"

class ToolCache:
    def __init__(self):
        self.cache = {}
        self._load()

    def _load(self):
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, "r") as f:
                self.cache = json.load(f)

    def _persist(self):
        with open(CACHE_FILE, "w") as f:
            json.dump(self.cache, f, indent=2)

    def _make_key(self, tool_name, tool_input):
        key = f"{tool_name}:{tool_input}"
        return hashlib.sha256(key.encode()).hexdigest()
    
    def get(self, tool_name, tool_input):
        key = self._make_key(tool_name, tool_input)
        return self.cache.get(key)
    
    def set(self, tool_name, tool_input, result):
        key = self._make_key(tool_name, tool_input)
        self.cache[key] = result
        self._persist()