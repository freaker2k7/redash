import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

from redash.query_runner.ai_base import AIBase

models = {}


class AIHuggingFace(AIBase):
    def __init__(self, query_runner, model_name: str = "defog/sqlcoder-7b-2", max_new_tokens=300):
        global models

        self.query_runner = query_runner

        if not models.get(model_name):
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)

            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                trust_remote_code=True,
                torch_dtype=torch.float16,
                device_map="auto",
                use_cache=True,
            )

            self.pipe = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                max_new_tokens=max_new_tokens,
                do_sample=False,
                return_full_text=False,  # added return_full_text parameter to prevent splitting issues with prompt
                num_beams=5,  # do beam search with 5 beams for high quality results
            )

            models[model_name] = (self.model, self.tokenizer, self.pipe)
        else:
            self.model, self.tokenizer, self.pipe = models[model_name]

        # make sure the model stops generating at triple ticks
        # eos_token_id = tokenizer.convert_tokens_to_ids(["```"])[0]
        self.eos_token_id = self.tokenizer.eos_token_id

    def generate_prompt(self, query_text: str) -> str:
        """
        Generate a prompt for the AI model based on the input query text.
        This is a placeholder method and should be implemented with actual prompt generation logic.
        """

        sql_type = self.query_runner.__class__.__name__

        return f"""### Task
Generate a {sql_type} query to answer [QUESTION]{query_text}[/QUESTION]

### Instructions
- If the whole message is already a valid {sql_type} query, return it as is.
- If you cannot answer the question with the available database schema, return '{getattr(self.query_runner, "noop_query", "SELECT 1")}' as the query.

### Database Schema
The query will run on a database with the following schema:
{self.query_runner.get_schema()}

### Answer
Given the database schema, here is the {sql_type} query that answers [QUESTION]{query_text}[/QUESTION]
[{sql_type}]"""

    def transform_query_with_ai(self, query_text: str) -> str:
        """
        Transform the query text using AI. This is a placeholder method and should be implemented
        with actual AI logic in subclasses.
        """
        query = (
            self.pipe(
                self.generate_prompt(query_text),
                num_return_sequences=1,
                eos_token_id=self.eos_token_id,
                pad_token_id=self.eos_token_id,
            )[0]["generated_text"]
            .split(";")[0]
            .split("```")[0]
            .strip()
            + ";"
        )

        print(f"?? Debug: AI generated query: '{query_text}' ==> '{query}'")

        return query
