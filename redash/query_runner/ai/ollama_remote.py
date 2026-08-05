from ollama import ChatResponse, Client

from redash.query_runner.ai.base_remote import AIBaseRemote


class AIOllamaRemote(AIBaseRemote):
    def __init__(self, query_runner, token=None, host=None, model_name=None):
        super(AIOllamaRemote, self).__init__(
            client=Client(host=host or "https://ollama.com", headers={"Authorization": "Bearer " + token}),
            query_runner=query_runner,
            model_name=model_name or "gemma3",
        )
        token = None  # Prevent token from being stored in memory after initialization

    def chat(self, messages: list[dict[str, str]]) -> str:
        return self.client.chat(model=self.model_name, messages=messages).message.content

    @property
    def models(self):
        return {engine.model: engine.model.title() for engine in self.client.list().models if engine.model}
