"""
python run_llama3.py --index 0 --offset 2500 --output part1.json --url http://127.0.0.1:17701/
"""
import motti
motti.append_current_dir(".")

from model.llama3 import LlamaClient
from template import TEMPLATE01
import random
random.seed(1)
import os
import json
import argparse
from src import (
    TabMWP,
    extract_prediction, 
    normalize_answer,
)

o_d = motti.o_d()

from tqdm import tqdm

parser = argparse.ArgumentParser()

parser.add_argument(
    "--hostname",
    type=str,
    default="127.0.0.1",
    help="The hostname of the server"
)
parser.add_argument(
    "--port",
    type=int,
    default=17700,
    help="The port of the server"
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
    "--output_dir",
    type=str,
    default="../output/",
    help="Path to the output file",
)


args = parser.parse_args()

name_wo_ext = __file__.split("/")[-1].split(".")[0]
output_dir = os.path.join(args.output_dir, name_wo_ext)
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, f"{name_wo_ext}_{args.index:05d}_{args.offset:05d}.json")
print(f"Saving results to {output_path}")

with open(output_path, "w") as f:
    f.write(f"// {o_d} {args}\n")

trainD = TabMWP(
    problem_path="../data/tabmwp/problems_train.json",
    tab_img_path="../data/tabmwp/tables/",
    shot_number=3,
)

shot_pids = trainD.shot_pids


D = TabMWP(
    problem_path="../data/tabmwp/problems_test1k.json",
    tab_img_path="../data/tabmwp/tables/",
    shot_pids=shot_pids,
)


L = LlamaClient(url=f"http://{args.hostname}:{args.port}/", template=TEMPLATE01)
print(L.dry_run())

correct = 0
total = 0

start = args.index
end = min(start + args.offset, len(D))

progess_bar = tqdm(range(start, end))

for i in progess_bar:
    total += 1
    pid, problem = D[i]
    answer = problem["answer"]
    options = problem["choices"]
    unit = problem["unit"]
    prompt = D.get_prompt_by_pid(pid, trainD=trainD)

    job = L.submit(prompt, return_full_text=False, max_new_tokens=1024, top_p=1, do_sample=False)
    output = job.result()[0]


    raw_prediction = output.split("Answer: ")[-1].strip()
    prediction = extract_prediction(raw_prediction, options=options, option_inds=D.option_inds)
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
        
    acc = correct / total * 100
    
    progess_bar.set_postfix(acc=f"{acc:.4f}%")
    
    with open(output_path, "a") as f:
        f.write(json.dumps(results) + "\n")
