"""
python run_llama3.py --index 0 --offset 2500 --output part1.json --url http://127.0.0.1:17701/
"""
import json
import os
from utils import TabMWP, Logger
import argparse
import gradio_client
from utils import (
    extract_prediction, 
    normalize_answer,
)

from llama3 import LlamaClient
from tqdm import tqdm

parser = argparse.ArgumentParser()

parser.add_argument(
    "--url",
    type=str,
    default="http://127.0.0.1:7860/",
    help="URL of the Gradio client",
)
parser.add_argument(
    "--index",
    type=int,
    default=0,
    help="Starting index for processing problems",
)

parser.add_argument(
    "--offset",
    type=int,
    default=10,
    help="Number of problems to process",
)

parser.add_argument(
    "--output",
    type=str,
    default="results.json",
    help="Path to the output file",
)

args = parser.parse_args()


D = TabMWP(
    problem_path="../data/tabmwp/problems_test.json",
    tab_img_path="../data/tabmwp/tables/",
)

client = gradio_client.Client(args.url)
client.view_api()

L = LlamaClient(client)
job = L.submit("Hello", return_full_text=False, max_new_tokens=512, top_p=1, do_sample=False)
print(job.result()[0])

results = {}
correct = 0

start = args.index
end = min(start + args.offset, len(D))

progess_bar = tqdm(range(start, end))

for i in progess_bar:
    pid, problem = D[i]
    answer = problem["answer"]
    options = problem["choices"]
    unit = problem["unit"]
    prompt = D._get_prompt(pid)

    job = L.submit(prompt, return_full_text=False, max_new_tokens=512, top_p=1, do_sample=False)
    output = job.result()[0]
    
    prediction = extract_prediction(output, options=options, option_inds=D.option_inds)
    answer_norm = normalize_answer(answer, unit)
    prediction_norm = normalize_answer(prediction, unit)
    
    results = {}
    results["pid"] = pid
    results["answer"] = answer
    results["answer_norm"] = answer_norm
    results["output"] = output
    results["prediction"] = prediction
    results["prediction_norm"] = prediction_norm
    
    # correct or not
    if answer_norm.lower() == prediction_norm.lower():
        correct += 1
        results["true_false"] = True
    else:
        results["true_false"] = False
        
    acc = correct / (i + 1) * 100
    
    progess_bar.set_postfix(acc=f"{acc:.2f}%")
    
    with open(args.output, "a") as f:
        f.write(json.dumps(results) + "\n")
