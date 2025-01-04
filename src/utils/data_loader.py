import json
import random
import os
import numpy as np
from deprecated import deprecated
from PIL import Image

class ProblemPromptMixin:
    @staticmethod
    def get_table_text(problem: dict) -> str:
        table = problem.get('table', '')
        title = problem.get('table_title', '')
        if title:
            table = f"[TITLE]: {title}\n{table}"
        return table

    @staticmethod
    def get_question_text(problem: dict, option_inds: list) -> str:
        question = problem.get('question', '')
        unit = problem.get('unit', '')
        if unit:
            question += f" (Unit: {unit})"

        choices = problem.get('choices', [])
        if choices:
            options = " ".join(f"({option_inds[i]}) {choice}" for i, choice in enumerate(choices))
            question += f"\nOptions: {options}"

        return question

    @staticmethod
    def get_answer(problem: dict) -> str:
        return problem.get('answer', '')

    @staticmethod
    def get_solution_text(problem: dict) -> str:
        return problem.get('solution', '').replace("\n", "\\n")

    @staticmethod
    def create_one_example(format: str, table: str, question: str, answer: str, solution: str, test_example: bool = True) -> str:
        input_format, output_format = format.split("-")  # e.g., "TQ-A"
        elements = {
            "Q": f"Question: {question}",
            "T": f"Table: {table}",
            "A": f"Answer: {answer}",
            "S": f"Solution: {solution}",
        }

        input_text = "\n".join(elements[label] for label in input_format)
        output_text = "\n".join(elements[label] for label in output_format) if not test_example else ""

        example = input_text + (f"\n\n{output_text}" if output_text else "")
        return example.strip()


    def build_prompt(
        self, 
        problems: dict, 
        shot_pids: list, 
        test_pid: int,
        option_inds: list = ["A", "B", "C", "D", "E", "F"],
        prompt_format: str = "TQ-A",
    ) -> str:
        examples = []
        pids = shot_pids + [test_pid]

        for pid in pids:
            problem = problems[pid]
            table = self.get_table_text(problem)
            question = self.get_question_text(problem, option_inds)
            answer = self.get_answer(problem)
            solution = self.get_solution_text(problem)

            test_example = (pid == test_pid)

            example = self.create_one_example(
                prompt_format, table, question, answer, solution, test_example
            )
            examples.append(example)

        prompt_input = '\n\n'.join(examples)
        return prompt_input


class TabMWP(ProblemPromptMixin):
    def __init__(
        self, 
        problem_path, 
        tab_img_path, 
        shot_number=0,
        shot_pids=None,
    ):
        self.problem_path = problem_path
        self.tab_img_path = tab_img_path

        
        self.problems = json.load(open(problem_path))  # problem data
        self.pids = list(self.problems.keys())
        
        if shot_pids == None:
            assert shot_number >= 0 and shot_number <= 32
            shot_pids = random.sample(self.pids, shot_number)  # random sample
        else:
            shot_pids = [str(pid) for pid in shot_pids]
            for pid in shot_pids:
                assert pid in self.pids  # check shot_pids
                
        self.shot_pids = shot_pids
        print("training question ids for prompting: ", self.shot_pids, "\n")
        
        
    def _get_tab_img(self, pid):
        tab_img = Image.open(os.path.join(self.tab_img_path, f'{pid}.png'))
        return np.array(tab_img)
    
    def _get_prompt(self, 
        pid,
        option_inds: list = ["A", "B", "C", "D", "E", "F"],
        prompt_format: str = "TQ-A",
    ):
        examples = []
        pids = self.shot_pids + [pid]
        
        for pid_ in pids:
            problem = self.problems[pid_]
            table = self.get_table_text(problem)
            question = self.get_question_text(problem, option_inds)
            answer = self.get_answer(problem)
            solution = self.get_solution_text(problem)

            test_example = (pid == pid_)

            example = self.create_one_example(
                prompt_format, table, question, answer, solution, test_example
            )
            examples.append(example)

        prompt_input = '\n\n'.join(examples)
        return prompt_input
    
    def get_prompt_by_id(self, idx):
        pid = self.pids[idx]
        return self._get_prompt(pid)
    
    def get_img_by_id(self, idx):
        pid = self.pids[idx]
        return self._get_tab_img(pid)
    
    def __len__(self):
        return len(self.pids)
    
    def __getitem__(self, idx):
        pid = self.pids[idx]
        problem = self.problems[pid]
        return problem

    @deprecated(reason="N/A")
    def _load_data(args):
        problems = json.load(open(os.path.join(args.data_root, f'problems_train.json')))

        pids = list(problems.keys())

        samples = random.sample(pids, args.train_number + args.cand_number)  # random sample
        train_pids = samples[:args.train_number]
        cand_pids = samples[args.train_number:]

        return problems, cand_pids, train_pids
    