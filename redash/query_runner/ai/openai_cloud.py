import openai

from redash.query_runner.ai.base_remote import AIBaseRemote


class AIOpenAICloud(AIBaseRemote):
    def __init__(self, query_runner, token=None, host=None, model_name=None):
        openai.api_key = token
        token = None  # Prevent token from being stored in memory after initialization

        super(AIOpenAICloud, self).__init__(
            client=openai,
            query_runner=query_runner,
            model_name=model_name or "gpt-5-mini",
        )

    def chat(self, messages: list[dict[str, str]]) -> str:
        return (
            openai.Completion.create(
                engine=self.model_name,
                prompt="\n".join([f"{m['role']}: {m['content']}" for m in messages]),
            )
            .choices[0]
            .text
        )

    @property
    def models(self):
        models = openai.Engine.list()
        return {model.id: model.name for model in models.data}
