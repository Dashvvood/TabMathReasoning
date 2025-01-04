class ProblemPromptBuilder:
    def __init__(self):
        pass

    @staticmethod
    def get_table_text(problem: dict) -> str:
        """
        Extract and format the table text from the problem dictionary.
        """
        table = problem.get('table', '')
        title = problem.get('table_title', '')
        if title:
            table = f"[TITLE]: {title}\n{table}"
        return table

    @staticmethod
    def get_question_text(problem: dict, option_inds: list) -> str:
        """
        Construct the question text with optional unit and choices.
        """
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
        """
        Retrieve the answer from the problem dictionary.
        """
        return problem.get('answer', '')

    @staticmethod
    def get_solution_text(problem: dict) -> str:
        """
        Format the solution text by replacing line breaks.
        """
        return problem.get('solution', '').replace("\n", "\\n")

    @staticmethod
    def create_one_example(format: str, table: str, question: str, answer: str, solution: str, test_example: bool = True) -> str:
        """
        Create a single formatted example based on the input-output format.
        """
        input_format, output_format = format.split("-")  # e.g., "TQ-A"
        elements = {
            "Q": f"Question: {question}",
            "T": f"Table: {table}",
            "A": f"Answer: {answer}",
            "S": f"Solution: {solution}",
        }

        # Build input and output texts
        input_text = "\n".join(elements[label] for label in input_format)
        output_text = "\n".join(elements[label] for label in output_format) if not test_example else ""

        # Combine input and output
        example = input_text + (f"\n\n{output_text}" if output_text else "")
        return example.strip()
    
    @staticmethod
    def build_prompt(self, problems: dict, shot_pids: list, test_pid: int, args) -> str:
        """
        Build a prompt input string using provided problems and arguments.
        """
        examples = []
        pids = shot_pids + [test_pid]

        for pid in pids:
            problem = problems[pid]
            table = self.get_table_text(problem)
            question = self.get_question_text(problem, args.option_inds)
            answer = self.get_answer(problem)
            solution = self.get_solution_text(problem)

            # Determine if the example is for testing
            test_example = (pid == test_pid)

            # Create formatted example
            example = self.create_one_example(
                args.prompt_format, table, question, answer, solution, test_example
            )
            examples.append(example)

        # Combine all examples into a single prompt
        prompt_input = '\n\n'.join(examples)
        return prompt_input
