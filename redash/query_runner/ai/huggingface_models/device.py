import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

if torch.cuda.is_available():
    device = "cuda"
elif torch.backends.mps.is_available():
    device = "mps"
else:
    device = "cpu"