from typing import Any

from redash.query_runner.ai.base import AIBase
from redash.query_runner.ai.huggingface_local import AIHuggingFaceLocal
from redash.query_runner.ai.ollama_remote import AIOllamaRemote
from redash.settings.organization import settings as org_settings


class AI(AIBase):
    """
    AI class that serves as a wrapper for different AI implementations.
    It initializes the appropriate AI implementation based on the organization settings.
    """

    instance_types = {
        "huggingface-local": AIHuggingFaceLocal,
        # "huggingface-remote": AIHuggingFaceRemote,
        "ollama-remote": AIOllamaRemote,
        # "kimi-k3-remote": AIKimiK3Remote,
        # "openai-cloud": AIOpenAICloud,
        # "claude-cloud": AIClaudeCloud,
        # "grok-cloud": AIGrokCloud,
    }

    def __init__(self, query_runner=None):
        if query_runner:
            self.type = org_settings.get("ai_type", "huggingface-local")

            if self.instance_types.get(self.type):
                host = org_settings.get("ai_host")
                model_name = org_settings.get("ai_model")
                token = org_settings.get("ai_token")
                self.instance = self.instance_types[self.type](query_runner, token=token, host=host, model_name=model_name)
                token = None  # Prevent token from being stored in memory after initialization
            else:
                raise NotImplementedError(f"AI type '{self.type}' is not implemented.")
        else:
            self.instance = None

    def apply_ai_query(self, query_text: str) -> str:
        if self.instance:
            return self.instance.apply_ai_query(query_text)
        return query_text

    def prompt(self, validation_class: Any, prompt: str, system_message: str, examples: list[str] = None) -> str:
        if self.instance:
            return self.instance.prompt(validation_class, prompt, system_message, examples)
        raise NotImplementedError(f"AI type '{self.type}' does not support prompt generation.")
