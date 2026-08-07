import logging

from anthropic import Anthropic

from redash.query_runner.ai.base_remote import AIBaseRemote

logger = logging.getLogger(__name__)


class AIClaudeCloud(AIBaseRemote):
    def __init__(self, query_runner, token=None, host=None, model_name=None):
        try:
            anthropic = Anthropic(api_key=token)
        except Exception as e:
            logger.error(f"Failed to initialize Anthropic client: {e}")
            anthropic = None
        finally:
            token = None  # Prevent token from being stored in memory after initialization

        super(AIClaudeCloud, self).__init__(
            client=anthropic,
            query_runner=query_runner,
            model_name=model_name or "claude-opus-5",
        )

    def chat(self, messages: list[dict[str, str]]) -> str:
        if not self.client:
            logger.error("Anthropic client is not initialized.")
            return ""

        response = self.client.messages.create(
            model=self.model_name,
            max_tokens=self.max_new_tokens,
            messages=messages,
        )

        result = ""
        for block in response.content:
            if block.type == "text":
                result += block.text
        return result

    @property
    def models(self):
        if not self.client:
            logger.error("Anthropic client is not initialized.")
            return {}

        return {model.id: model.display_name for model in self.client.models.list().data}
