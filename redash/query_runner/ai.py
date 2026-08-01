from redash.query_runner.ai_base import AIBase
from redash.query_runner.ai_huggingface import AIHuggingFace
from redash.authentication import current_org

class AI(AIBase):
    """
    AI class that serves as a wrapper for different AI implementations.
    It initializes the appropriate AI implementation based on the organization settings.
    """

    instance_types = {
        "huggingface": AIHuggingFace,
        # "ollama": AIOllama,
        # "kimi": AIKimiK,
        # "openai": AIOpenAI,
        # "claude": AIClaude,
        # "grok": AIGrok,
    }

    def __init__(self, query_runner):
        if query_runner:
            self.type = current_org.get_setting("ai_type", raise_on_missing=False) or "huggingface"

            if self.instance_types.get(self.type):
                token = current_org.get_setting("ai_token", raise_on_missing=False)
                self.instance = self.instance_types[self.type](query_runner, token=token)
                token = None # Prevent token from being stored in memory after initialization
            else:
                raise NotImplementedError(f"AI type '{self.type}' is not implemented.")
        else:
            self.instance = None

    def apply_ai_query(self, query_text: str) -> str:
        if self.instance:
            return self.instance.apply_ai_query(query_text)
        return query_text
