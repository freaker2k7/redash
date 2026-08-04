import logging
from typing import Any

from ollama import ChatResponse, Client

from redash.query_runner.ai.base import AIBase

logger = logging.getLogger(__name__)


class AIOllamaRemote(AIBase):
    def __init__(self, query_runner, token=None, host=None, model_name="gemma3"):
        """
        NOTE: `host` parameter is not used in this class, but it's included for compatibility with other AI implementations that may require a host.
        """
        self.model_name = model_name
        self.query_runner = query_runner
        self.client = Client(
            host=host or "https://ollama.com",
            headers={"Authorization": "Bearer " + token},
        )
        token = None  # Prevent token from being stored in memory after initialization

    def load_model(self):
        pass

    def apply_ai_query(self, query_text: str) -> str:
        """
        Transform the query text using AI. This is a placeholder method and should be implemented
        with actual AI logic in subclasses.
        """

        query: ChatResponse = self.client.chat(model=self.model_name, messages=[
            {
                'role': 'system',
                'content': f"""### Task
Generate a {self.query_runner.__class__.__name__} query to answer [QUESTION]{query_text}[/QUESTION]

### Instructions
- If the whole message is already a valid {self.query_runner.__class__.__name__} query, return it as is.
- If you cannot answer the question with the available database schema, return 'NO ANSWER'.

### Database Schema
The query will run on a database with the following schema:
{self.query_runner.get_schema()}"""
            },
            {
                'role': 'user',
                'content': f"""Given the database schema, here is the {self.query_runner.__class__.__name__} query that answers [QUESTION]{query_text}[/QUESTION]
[{self.query_runner.__class__.__name__}]"""
            },
        ])

        return query.message.content or "NO ANSWER"

    def prompt(
        self,
        validation_class: Any,
        prompt: str,
        system_message: str,
        examples: list[str] = None,
    ) -> str:
        """
        Generate a response from the AI model based on the provided prompt and system message.
        """

        messages=[{ 'role': 'system', 'content': system_message }]

        if examples:
            for example in examples:
                messages.append({ 'role': 'user', 'content': example['user'] })
                messages.append({ 'role': 'assistant', 'content': example['assistant'] })

        messages.append({ 'role': 'user', 'content': prompt })

        response: ChatResponse = self.client.chat(model=self.model_name, messages=messages)

        trials = 3
        for trial in range(trials):
            try:
                return validation_class.model_validate_json(response.message.content).dict()
            except Exception as e:
                logger.error("Validation failed for AI response: %s", e)
                if trial == trials - 1:
                    raise ValueError(f"Validation failed for AI response: {e}")
