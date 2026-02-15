from abc import ABC, abstractmethod

class BaseEngine(ABC):
    @abstractmethod
    def run(self, task:str, context=None):
        """
        Execute a task and return structured result
        """
        pass