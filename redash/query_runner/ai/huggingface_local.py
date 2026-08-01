import time

from redash.query_runner.ai.base import AIBase

device = "cpu"
models = {}


class AIHuggingFaceLocal(AIBase):
    def __init__(self, query_runner, token=None):
        self.query_runner = query_runner
        self.token = token
        self.model = None
        self.tokenizer = None
        self.pipe = None
        token = None  # Prevent token from being stored in memory after initialization

    def load_model(self):
        global device, models

        if not models.get(self.query_runner.supports_ai_query_type, {}).get("loaded"):
            if not models.get(self.query_runner.supports_ai_query_type):
                models[self.query_runner.supports_ai_query_type] = {"loading": True}

                if self.query_runner.supports_ai_query_type == "sql":
                    from redash.query_runner.ai.huggingface_models.defog_sqlcoder_7b_2 import (
                        HuggingFaceModelsDefogSQLCoder7B2,
                    )

                    model_instance = HuggingFaceModelsDefogSQLCoder7B2(self.query_runner, token=self.token)

                    models[self.query_runner.supports_ai_query_type]["model_data"] = model_instance.load()
                    models[self.query_runner.supports_ai_query_type]["model_instance"] = model_instance
                    models[self.query_runner.supports_ai_query_type]["loaded"] = True
                elif self.query_runner.supports_ai_query_type == "nosql":
                    from redash.query_runner.ai.huggingface_models.qwen_qwen3_coder_next import (
                        HuggingFaceModelsQwenQwen3CoderNext,
                    )

                    model_instance = HuggingFaceModelsQwenQwen3CoderNext(self.query_runner, token=self.token)

                    models[self.query_runner.supports_ai_query_type]["model_data"] = model_instance.load()
                    models[self.query_runner.supports_ai_query_type]["model_instance"] = model_instance
                    models[self.query_runner.supports_ai_query_type]["loaded"] = True
                else:
                    raise NotImplementedError(
                        f"AI query type '{self.query_runner.supports_ai_query_type}' is not supported for HuggingFaceLocal."
                    )
            else:
                while models[self.query_runner.supports_ai_query_type].get("loading"):
                    time.sleep(1)

    def apply_ai_query(self, query_text: str) -> str:
        """
        Transform the query text using AI. This is a placeholder method and should be implemented
        with actual AI logic in subclasses.
        """

        self.load_model()

        query = models[self.query_runner.supports_ai_query_type]["model_instance"].generate(query_text)

        print(f"?? Debug: AI generated query: '{query_text}' ==> '{query}'")

        return query
