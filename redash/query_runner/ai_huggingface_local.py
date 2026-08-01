import time

from redash.query_runner.ai_base import AIBase

device = "cpu"
models = {}


class AIHuggingFaceLocal(AIBase):
    def __init__(self, query_runner, model_name: str = "defog/sqlcoder-7b-2", max_new_tokens=300, token=None):
        self.query_runner = query_runner
        self.model_name = model_name
        self.max_new_tokens = max_new_tokens
        self.token = token
        self.model = None
        self.tokenizer = None
        self.pipe = None
        token = None  # Prevent token from being stored in memory after initialization

    def load_model(self):
        global device, models

        if not models.get(self.model_name, {}).get("loaded"):
            if not models.get(self.model_name):
                models[self.model_name] = {"loading": True}

                import torch
                from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

                if torch.cuda.is_available():
                    device = "cuda"
                elif torch.backends.mps.is_available():
                    device = "mps"
                else:
                    device = "cpu"

                tokenizer = AutoTokenizer.from_pretrained(self.model_name)

                model = AutoModelForCausalLM.from_pretrained(
                    self.model_name,
                    trust_remote_code=True,
                    torch_dtype=torch.float16,
                    use_cache=True,
                    token=self.token,  # TODO: Check if this is correct !!!!!!!!!!!!!!!!!!!!!!!!!!!!!
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

                models[self.model_name] = {
                    "model": model,
                    "tokenizer": tokenizer,
                    "pipe": pipe,
                    "eos_token_id": eos_token_id,
                    "loaded": True,
                }
            else:
                while models[self.model_name].get("loading"):
                    time.sleep(1)

    # TODO: This should be templates per query_runner + model !!!!!!!!!!!!
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
- If you cannot answer the question with the available database schema, return 'NO ANSWER'.

### Database Schema
The query will run on a database with the following schema:
{self.query_runner.get_schema()}

### Answer
Given the database schema, here is the {sql_type} query that answers [QUESTION]{query_text}[/QUESTION]
[{sql_type}]"""

    def apply_ai_query(self, query_text: str) -> str:
        """
        Transform the query text using AI. This is a placeholder method and should be implemented
        with actual AI logic in subclasses.
        """

        self.load_model()

        query = (
            models[self.model_name]
            .pipe(
                self.generate_prompt(query_text),
                num_return_sequences=1,
                eos_token_id=models[self.model_name]["eos_token_id"],
                pad_token_id=models[self.model_name]["eos_token_id"],
            )[0]["generated_text"]
            .split(";")[0]
            .split("```")[0]
            .strip()
            + ";"
        )

        print(f"?? Debug: AI generated query: '{query_text}' ==> '{query}'")

        return query
