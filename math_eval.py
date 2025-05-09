"""
Measuring Mathematical Problem Solving With the MATH Dataset
Dan Hendrycks, Collin Burns, Saurav Kadavath, Akul Arora, Steven Basart, Eric Tang, Dawn Song, Jacob Steinhardt
https://arxiv.org/abs/2103.03874
"""

import random
import re
import os
import json
import pathlib
import urllib.request
from typing import Literal

import pandas

import common
from common import ANSWER_PATTERN, HTML_JINJA, check_equality
from eval_types import Eval, EvalResult, SamplerBase, SingleEvalResult

QUERY_TEMPLATE = """
Solve the following math problem step by step. The last line of your response should be of the form Answer: $ANSWER (without quotes) where $ANSWER is the answer to the problem.

{Question}

Remember to put your answer on its own line after "Answer:", and you do not need to use a \\boxed command.
""".strip()

CACHE_DIR = pathlib.Path(".simple_evals_cache")

class MathEval(Eval):
    def __init__(
        self,
        equality_checker: SamplerBase,
        num_examples: int | None = None,
        n_repeats: int = 16,
        split: Literal["math_test", "math_500_test"] = "math_test",
        batch_size: int = 20,
        checkpoint_file: str | None = None,
    ):
        url = f"https://openaipublic.blob.core.windows.net/simple-evals/{split}.csv"
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        file_name = url.split("/")[-1]
        cached_file_path = CACHE_DIR / file_name

        if cached_file_path.exists():
            print(f"Loading cached MATH data from {cached_file_path}")
            df = pandas.read_csv(cached_file_path)
        else:
            print(f"Downloading MATH data from {url} to {cached_file_path}")
            urllib.request.urlretrieve(url, str(cached_file_path))
            df = pandas.read_csv(cached_file_path)
            
        examples = [row.to_dict() for _, row in df.iterrows()]
        if num_examples:
            assert n_repeats == 1, "n_repeats only supported for num_examples = None"
            rng = random.Random(0)
            examples = rng.sample(examples, num_examples)
        self.examples = examples * n_repeats
        self.equality_checker = equality_checker
        self.batch_size = batch_size
        self.checkpoint_file = checkpoint_file
        self.processed_results: list[SingleEvalResult] = []

        if self.checkpoint_file:
            self.processed_results = common.load_checkpoint(self.checkpoint_file)

    def __call__(self, sampler: SamplerBase) -> EvalResult:
        def fn(row: dict):
            prompt_messages = [
                sampler._pack_message(content=QUERY_TEMPLATE.format(**row), role="user")
            ]
            response_text = sampler(prompt_messages)
            match = re.search(ANSWER_PATTERN, response_text)
            extracted_answer = match.group(1) if match else None
            score = float(check_equality(self.equality_checker, row["Answer"], extracted_answer))
            html = common.jinja_env.from_string(HTML_JINJA).render(
                prompt_messages=prompt_messages,
                next_message=dict(content=response_text, role="assistant"),
                score=score,
                correct_answer=row["Answer"],
                extracted_answer=extracted_answer,
            )
            convo = prompt_messages + [dict(content=response_text, role="assistant")]
            return SingleEvalResult(html=html, score=score, convo=convo)

        num_already_processed = len(self.processed_results)
        num_total_examples = len(self.examples)

        if num_already_processed >= num_total_examples:
            if not self.examples: # No examples to run at all
                print("No examples to evaluate.")
                return common.aggregate_results([])
            print("All examples were already processed according to checkpoint.")
            return common.aggregate_results(self.processed_results)

        examples_to_process_this_run = self.examples[num_already_processed:]
        
        print(f"Starting Math evaluation. Total examples (including repeats): {num_total_examples}. Already processed: {num_already_processed}. Remaining: {len(examples_to_process_this_run)}.")

        for i in range(0, len(examples_to_process_this_run), self.batch_size):
            batch_examples = examples_to_process_this_run[i : i + self.batch_size]
            if not batch_examples:
                continue

            current_global_start_index_for_batch = num_already_processed + i
            batch_start_num_display = current_global_start_index_for_batch + 1
            batch_end_num_display = min(current_global_start_index_for_batch + len(batch_examples), num_total_examples)
            
            print(f"Processing batch: examples {batch_start_num_display}-{batch_end_num_display} of {num_total_examples} (Batch size: {self.batch_size})")
            
            # Note: map_with_progress will show its own progress bar for the batch
            batch_new_results = common.map_with_progress(fn, batch_examples)
            
            self.processed_results.extend(batch_new_results)
            
            if self.checkpoint_file and batch_new_results:
                common.save_checkpoint(self.checkpoint_file, batch_new_results)
        
        print(f"Math evaluation finished. Processed {len(self.processed_results)} results in total out of {num_total_examples} examples.")
        return common.aggregate_results(self.processed_results)
