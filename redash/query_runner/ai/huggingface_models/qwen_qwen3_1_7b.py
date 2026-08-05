import logging

from outlines.inputs import Chat

from redash.query_runner.ai.huggingface_models import HuggingFaceModelBase

# from redash.query_runner.ai.huggingface_models.device import device

logger = logging.getLogger(__name__)


class HuggingFaceModelsQwenQwen317B(HuggingFaceModelBase):
    def __init__(self, query_runner, max_new_tokens=128, token=None):
        super(HuggingFaceModelsQwenQwen317B, self).__init__(query_runner, "Qwen/Qwen3-1.7B", token, max_new_tokens)
        self.model_data = None

    def load(self):
        from transformers import AutoModelForCausalLM, AutoTokenizer

        tokenizer = AutoTokenizer.from_pretrained(self.model_name, token=self.token or None)

        model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            device_map="auto",
            token=self.token or None,
        )
        # .to(device)
        self.token = None  # Prevent token from being stored in memory after initialization

        return {
            "model": model,
            "tokenizer": tokenizer,
            "pipe": None,
            "eos_token_id": None,
        }

    def template(self, query_text):
        pass

    def generate(self, model, query_text: str) -> str:
        pass

    def prompt(self, model, prompt: str, system_message: str, examples: list[str] = None) -> str:
        chat = Chat()
        chat.add_system_message(system_message)

        if examples:
            for example in examples:
                chat.add_user_message(example["user"])
                chat.add_assistant_message(example["assistant"])

        chat.add_user_message(prompt)

        res = model["generator"](chat, model["validation_class"], max_new_tokens=self.max_new_tokens)

        try:
            return model["validation_class"].model_validate_json(res).to_dict()
        except Exception as e:
            logger.error("Failed to parse response: %s", e)
            logger.error("Raw output was: %s", res)
            raise e
