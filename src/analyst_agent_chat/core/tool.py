from typing import Callable, List

class Tool:
    def __init__(self, name: str, description: str, function: Callable, allowed_modes: List[str], cache=None, is_cacheable=True):
       self.name = name
       self.description = description
       self.function = function
       self.allowed_modes = allowed_modes
       self.cache = cache
       self.is_cacheable = is_cacheable

    def execute(self, *args, **kwargs):
        tool_input = args[0] if args else ""

        # check cache
        if self.is_cacheable and self.cache:
            cached = self.cache.get(self.name, tool_input)
            if cached is not None:
                #print(f"[Cache hit] {self.name}")
                return cached
            
        # execute tool
        result = self.function(*args, **kwargs)

        # store cache
        if self.is_cacheable and self.cache:
            self.cache.set(self.name, tool_input, result)

        return result