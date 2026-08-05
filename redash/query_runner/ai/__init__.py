import logging
from typing import Any

from redash.query_runner.ai.base import AIBase
from redash.query_runner.ai.huggingface_local import AIHuggingFaceLocal
from redash.query_runner.ai.ollama_remote import AIOllamaRemote
from redash.query_runner.ai.openai_cloud import AIOpenAICloud

logger = logging.getLogger(__name__)

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
        "openai-cloud": AIOpenAICloud,
        # "claude-cloud": AIClaudeCloud,
        # "grok-cloud": AIGrokCloud,
    }

    def __init__(self, query_runner=None, ai_type=None, ai_host=None, ai_token=None):
        if query_runner:
            self.type = ai_type or query_runner.configuration.get("ai_type") or "huggingface-local"

            logger.info(
                f"Initializing AI instance of type '{self.type}' for query runner '{query_runner.__class__.__name__}'; host='{query_runner.configuration.get('ai_host')}', token='{query_runner.configuration.get('ai_token')}'."
            )

            if self.instance_types.get(self.type):
                model_name = query_runner.configuration.get("ai_model") if not ai_type else None
                host = ai_host or query_runner.configuration.get("ai_host")
                token = ai_token or query_runner.configuration.get("ai_token")
                self.instance = self.instance_types[self.type](
                    query_runner, token=token, host=host, model_name=model_name
                )
                token = None  # Prevent token from being stored in memory after initialization
                ai_token = None  # Prevent token from being stored in memory after initialization
            else:
                raise NotImplementedError(f"AI type '{self.type}' is not implemented.")
        else:
            self.instance = None

    def apply_ai_query(self, query_text: str) -> str:
        if self.instance:
            return self.instance.apply_ai_query(query_text)
        return query_text

    def prompt(
        self,
        validation_class: Any,
        prompt: str,
        system_message: str,
        examples: list[str] = None,
    ) -> str:
        if self.instance:
            return self.instance.prompt(validation_class, prompt, system_message, examples)
        raise NotImplementedError(f"AI type '{self.type}' does not support prompt generation.")

    @property
    def models(self):
        if self.instance:
            return self.instance.models
        return {}

    @property
    def supported_types(self) -> dict[str, dict[str, Any]]:
        return {
            "huggingface-local": {
                "name": "HuggingFace (Local)",
                "enabled": True,
            },
            "huggingface-remote": {
                "name": "HuggingFace (Remote) [Coming Soon]",
            },
            "kimi-k3-remote": {
                "name": "Kimi K3 (Remote) [Coming Soon]",
            },
            "ollama-remote": {
                "name": "Ollama (Remote)",
                "enabled": True,
            },
            "openai-cloud": {
                "name": "OpenAI (Cloud)",
                "enabled": True,
            },
            "claude-cloud": {
                "name": "Claude (Cloud) [Coming Soon]",
            },
            "grok-cloud": {
                "name": "Grok (Cloud) [Coming Soon]",
            },
        }
