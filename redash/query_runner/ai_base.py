from abc import ABC, abstractmethod

class AIBase(ABC):
    @abstractmethod
    def apply_ai_query(self, query_text: str) -> str:
        """
        Apply AI transformation to the query text. This is a placeholder method
		and should be implemented with actual AI logic in subclasses.
        """
        pass
