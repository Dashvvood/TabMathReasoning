
EXEMPLE_MESSAGE = [
    {
        "role": "system",
        "content": 
            "You are an expert assistant that provides concise and accurate answers."
            "Provide a concise answer."
            "Answer the question with short words."
    },
    {
        "role": "user",
        "content": "What is the capital of France?"
    }
]

import gradio as gr

import torch
import transformers

from transformers import AutoTokenizer, AutoModelForCausalLM
from accelerate import infer_auto_device_map,  dispatch_model
from accelerate.utils import get_balanced_memory
from sentence_transformers import SentenceTransformer
import argparse
import json

parser = argparse.ArgumentParser(description="Run the RAG-llama3 model.")
parser.add_argument('--model', type=str, default="meta-llama/Llama-3.2-3B-Instruct", help='Model name or path')
parser.add_argument('--dtype', type=str, default="torch.bfloat16", help='Data type for model')
parser.add_argument('--device', type=str, default="cuda", help='Device to run the model on')
parser.add_argument('--port', type=int, default=17700, help='Port number for the server')
opts, missing = parser.parse_known_args()
print(f"{opts = }")
print(f"{missing = }")

if opts.dtype == "torch.bfloat16":
    model_dtype = torch.bfloat16
elif opts.dtype == "torch.float32":
    model_dtype = torch.float32
elif opts.dtype == "torch.float16":
    model_dtype = torch.float16
else:
    raise ValueError(f"Unknown data type: {opts.dtype}")

pipe = transformers.pipeline(
    "text-generation", model=opts.model, 
    model_kwargs={"torch_dtype": torch.bfloat16}, 
    device=opts.device
)

def generate_text(
    message,
    do_sample=True,
    return_full_text=True,
    top_p=0.9,
    temperature=0.6,
    max_new_tokens=200,
):  
    try:
        if type(message) == str:
            message = json.loads(message)

        response = pipe(
            message,
            return_full_text=return_full_text,
            do_sample=do_sample,
            top_p=top_p,
            temperature=temperature,
            max_new_tokens=max_new_tokens,
            pad_token_id=pipe.tokenizer.eos_token_id,
        )
        
    except Exception as e:
        return str(e), None
    return str(response[0]["generated_text"]), response


iface = gr.Interface(
    fn=generate_text,
    inputs = [
        gr.Textbox(lines=2, placeholder=str(EXEMPLE_MESSAGE), label="Message"),
        gr.Checkbox(value=True, label="Do Sample"),
        gr.Checkbox(value=True, label="Return Full Text"),
        gr.Slider(minimum=0.0, maximum=1.0, value=0.9, label="Top P"),
        gr.Slider(minimum=0.0, maximum=1.0, value=0.6, label="Temperature"),
        gr.Slider(minimum=1, maximum=1024, value=512, label="Max New Tokens"),
    ],
    
    outputs = [
        gr.Textbox(label="Generated Text"),
        gr.JSON(label="Generated Text"),
    ],

    title="Llama3 Text Generation",
    description="Example Input: " + str(EXEMPLE_MESSAGE)
)

iface.queue()

iface.launch(server_port=opts.port)
