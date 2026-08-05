from redash.query_runner.ai.huggingface_models import HuggingFaceModelBase
from redash.query_runner.ai.huggingface_models.device import device


class HuggingFaceModelsDefogSQLCoder7B2(HuggingFaceModelBase):
    def __init__(self, query_runner, max_new_tokens=300, token=None):
        super(HuggingFaceModelsDefogSQLCoder7B2, self).__init__(
            query_runner, "defog/sqlcoder-7b-2", token, max_new_tokens
        )
        self.model_data = None

    def load(self):
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

        tokenizer = AutoTokenizer.from_pretrained(self.model_name, token=self.token or None)

        model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            trust_remote_code=True,
            dtype=torch.float16,
            use_cache=True,
            token=self.token or None,
        ).to(device)
        self.token = None  # Prevent token from being stored in memory after initialization

        pipe = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            max_new_tokens=self.max_new_tokens,
            do_sample=False,
            return_full_text=False,  # added return_full_text parameter to prevent splitting issues with prompt
            num_beams=5,  # do beam search with 5 beams for high quality results
        )

        # make sure the model stops generating at triple ticks
        # eos_token_id = tokenizer.convert_tokens_to_ids(["```"])[0]
        eos_token_id = tokenizer.eos_token_id

        return {
            "model": model,
            "tokenizer": tokenizer,
            "pipe": pipe,
            "eos_token_id": eos_token_id,
        }

    def template(self, query_text):
        sql_data_source_type = self.query_runner.__class__.__name__

        return f"""### Task
Generate a {sql_data_source_type} query to answer [QUESTION]{query_text}[/QUESTION]

### Instructions
- If the whole message is already a valid {sql_data_source_type} query, return it as is.
- If you cannot answer the question with the available database schema, return 'NO ANSWER'.

### Database Schema
The query will run on a database with the following schema:
{self.query_runner.get_schema()}

### Answer
Given the database schema, here is the {sql_data_source_type} query that answers [QUESTION]{query_text}[/QUESTION]
[{sql_data_source_type}]"""

    def generate(self, model, query_text: str) -> str:
        return (
            model["pipe"](
                self.template(query_text),
                num_return_sequences=1,
                eos_token_id=model["eos_token_id"],
                pad_token_id=model["eos_token_id"],
            )[0]["generated_text"]
            .split(";")[0]
            .split("```")[0]
            .strip()
            + ";"
        )
