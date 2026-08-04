from abc import ABC, abstractmethod


class HuggingFaceModelBase(ABC):
    def __init__(
        self,
        query_runner,
        model_name: str,
        token: str = None,
        max_new_tokens: int = 512,
    ):
        self.model_name = model_name
        self.token = token
        self.max_new_tokens = max_new_tokens
        self.query_runner = query_runner

    @abstractmethod
    def load(self):
        pass

    @abstractmethod
    def template(self, query_text: str) -> str:
        pass

    @abstractmethod
    def generate(self, model, query_text: str) -> str:
        pass
