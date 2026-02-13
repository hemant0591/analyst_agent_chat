from typing import Callable, List

class Tool:
    def __init__(self, name: str, description: str, function: Callable, allowed_modes: List[str]):
       self.name = name
       self.description = description
       self.function = function
       self.allowed_modes = allowed_modes

    def execute(self, *args, **kwargs):
        return self.function(*args, **kwargs) 