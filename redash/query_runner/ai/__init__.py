from redash.query_runner.ai.base import AIBase
from redash.query_runner.ai.huggingface_local import AIHuggingFaceLocal
from redash.settings.organization import settings as org_settings


class AI(AIBase):
    """
    AI class that serves as a wrapper for different AI implementations.
    It initializes the appropriate AI implementation based on the organization settings.
    """

    instance_types = {
        "huggingface-local": AIHuggingFaceLocal,
        # "huggingface-remote": AIHuggingFaceRemote,
        # "ollama-remote": AIOllamaRemote,
        # "kimi-k3-remote": AIKimiK3Remote,
        # "openai-remote": AIOpenAIRemote,
        # "claude-remote": AIClaudeRemote,
        # "grok-remote": AIGrokRemote,
    }

    def __init__(self, query_runner=None):
        if query_runner:
            self.type = org_settings.get("ai_type", "huggingface-local")

            if self.instance_types.get(self.type):
                token = org_settings.get("ai_token")
                self.instance = self.instance_types[self.type](query_runner, token=token)
                token = None  # Prevent token from being stored in memory after initialization
            else:
                raise NotImplementedError(f"AI type '{self.type}' is not implemented.")
        else:
            self.instance = None

    def apply_ai_query(self, query_text: str) -> str:
        if self.instance:
            return self.instance.apply_ai_query(query_text)
        return query_text
