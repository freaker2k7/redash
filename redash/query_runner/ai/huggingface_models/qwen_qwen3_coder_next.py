from . import HuggingFaceModelBase


class HuggingFaceModelsQwenQwen3CoderNext(HuggingFaceModelBase):
    def __init__(self, query_runner, max_new_tokens=512, token=None):
        super().__init__(query_runner, "Qwen/Qwen3-Coder-Next", token, max_new_tokens)
        self.model_data = None

    def load(self):
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        if torch.cuda.is_available():
            device = "cuda"
        elif torch.backends.mps.is_available():
            device = "mps"
        else:
            device = "cpu"

        tokenizer = AutoTokenizer.from_pretrained(self.model_name, token=self.token or None)

        model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype="auto",
            token=self.token or None,
        ).to(device)
        self.token = None  # Prevent token from being stored in memory after initialization

        return {
            "model": model,
            "tokenizer": tokenizer,
            "pipe": None,
            "eos_token_id": None,
        }

    def template(self, query_text):
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

    def generate_prompt(self, model, query_text: str) -> str:
        text = model["tokenizer"].apply_chat_template(
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that translates natural language questions into SQL queries. You are given a database schema and a question. Your task is to generate a valid SQL query that answers the question based on the provided schema. If you cannot answer the question with the available database schema, return 'NO ANSWER'. Do not include any explanations or additional text, only provide the SQL query or 'NO ANSWER'.",
                },
                {
                    "role": "user",
                    "content": self.template(query_text),
                },
            ],
            tokenize=False,
            add_generation_prompt=True,
        )
        model_inputs = model["tokenizer"]([text], return_tensors="pt").to(model["model"].device)

        # conduct text completion
        generated_ids = model["model"].generate(**model_inputs, max_new_tokens=self.max_new_tokens)
        output_ids = generated_ids[0][len(model_inputs.input_ids[0]) :].tolist()

        return model["tokenizer"].decode(output_ids, skip_special_tokens=True)
