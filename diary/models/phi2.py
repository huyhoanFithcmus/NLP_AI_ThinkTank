import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

def make_pipeline():
    model = AutoModelForCausalLM.from_pretrained("microsoft/phi-2", torch_dtype="auto", 
                                             device_map="cuda", trust_remote_code=True)
    tokenizer = AutoTokenizer.from_pretrained("microsoft/phi-2", trust_remote_code=True)
    pipe = pipeline(
        task = "text-generation",
        model=model,
        tokenizer=tokenizer,
        max_length = 200
    )
    return pipe
