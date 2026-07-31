from redash.query_runner.ai_huggingface import AIHuggingFace
from redash.authentication import current_org

class AI:
    def __init__(self, query_runner):
        self.type = current_org.get_setting("ai_type", raise_on_missing=False) or "huggingface"
        self.token = current_org.get_setting("ai_token", raise_on_missing=False)

        if self.type == "huggingface":
            self.instance = AIHuggingFace(query_runner, token=self.token)
        else:
            raise NotImplementedError(f"AI type '{self.type}' is not implemented.")

    def apply_ai_query(self, query_text: str) -> str:
        return self.instance.apply_ai_query(query_text)
