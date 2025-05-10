"""
HumanEval: Evaluating Large Language Models Trained on Code
Mark Chen and Jerry Tworek and Heewoo Jun and Qiming Yuan and Henrique Ponde de Oliveira Pinto and Jared Kaplan and Harri Edwards and Yuri Burda and Nicholas Joseph and Greg Brockman and Alex Ray and Raul Puri and Gretchen Krueger and Michael Petrov and Heidy Khlaaf and Girish Sastry and Pamela Mishkin and Brooke Chan and Scott Gray and Nick Ryder and Mikhail Pavlov and Alethea Power and Lukasz Kaiser and Mohammad Bavarian and Clemens Winter and Philippe Tillet and Felipe Petroski Such and Dave Cummings and Matthias Plappert and Fotios Chantzis and Elizabeth Barnes and Ariel Herbert-Voss and William Hebgen Guss and Alex Nichol and Alex Paino and Nikolas Tezak and Jie Tang and Igor Babuschkin and Suchir Balaji and Shantanu Jain and William Saunders and Christopher Hesse and Andrew N. Carr and Jan Leike and Josh Achiam and Vedant Misra and Evan Morikawa and Alec Radford and Matthew Knight and Miles Brundage and Mira Murati and Katie Mayer and Peter Welinder and Bob McGrew and Dario Amodei and Sam McCandlish and Ilya Sutskever and Wojciech Zaremba 
https://arxiv.org/abs/2107.03374 https://github.com/openai/human-eval/ 
"""

import json
import logging
import multiprocessing
import random
import re
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from io import BytesIO
from typing import Any, Tuple

import human_eval_windows_patch

from human_eval.data import HUMAN_EVAL, read_problems
from human_eval.evaluation import estimate_pass_at_k
from human_eval.execution import check_correctness  # , unsafe_execute

import common
from common import HTML_JINJA
from eval_types import Eval, EvalResult, SamplerBase, SingleEvalResult


def evaluate_functional_correctness(
    sample: dict[str, str],
    completions: list[str],
    n_workers: int = 4,
    timeout: float = 30.0,
):
    """
    Evaluates the functional correctness of generated samples, and writes
    results to f"{sample_file}_results.jsonl.gz"
    """
    import copy

    # Check the generated samples against test suites.
    with ThreadPoolExecutor(max_workers=n_workers) as executor:
        futures = []
        for i, completion in enumerate(completions):
            args = (sample, completion, timeout, i)
            future = executor.submit(check_correctness, *args)
            futures.append(future)
        results = []
        for i, future in enumerate(as_completed(futures)):
            result = future.result()
            results.append(result)
            if result.get("result") == "timed out":
                print(f"Completion {i} for sample {sample.get('task_id', 'unknown')} timed out.")
    passed = [int(r["passed"]) for r in results]
    return passed


class HumanEval(Eval):
    def __init__(
        self,
        num_examples: int = 250,  # restrict to a subset of the data for debugging
        num_samples_per_task: int = 3,
        ks_passes: list[int] = [1, 2, 5],
        timeout: int = 120,
        batch_size: int = 20, # Default batch size
        checkpoint_file: str | None = None, # Path to the checkpoint file
    ):
        self.seed = 0
        self.examples = read_problems()
        self.examples = list(self.examples.values())

        self._num_examples = num_examples
        if self._num_examples:
            self.examples = random.Random(self.seed).sample(self.examples, num_examples)
        self._num_samples_per_task = num_samples_per_task
        self._ks_passes = ks_passes
        self._timeout = timeout
        self.batch_size = batch_size
        self.checkpoint_file = checkpoint_file
        self.processed_results: list[SingleEvalResult] = []

        if self.checkpoint_file:
            self.processed_results = common.load_checkpoint(self.checkpoint_file)

    def __call__(self, sampler: SamplerBase) -> EvalResult:
        instruction = "Read the following function signature and docstring, and fully implement the function described. Your response should only contain the code for this function.\n"

        def find_code(completion):
            pattern = re.compile(r"```python\n(.*?)```", re.DOTALL)
            matches = pattern.findall(completion)
            extracted_answer = matches[0] if len(matches) >= 1 else completion
            extracted_answer = extracted_answer[
                extracted_answer.find(":\n    ") + 2 :
            ]  # remove signature
            return extracted_answer

        def fn(sample: dict[str, str]):
            prompt_messages = [
                sampler._pack_message(role="user", content=instruction + sample["prompt"])
            ]
            completions = [
                find_code(sampler(prompt_messages)) for _ in range(self._num_samples_per_task)
            ]
            results = evaluate_functional_correctness(sample, completions)
            total = len(results)
            correct = sum(results)
            score = sum(results) / len(results)
            html = common.jinja_env.from_string(HTML_JINJA).render(
                prompt_messages=prompt_messages,
                next_message=dict(content=completions[0], role="assistant"),
                score=score,
                correct_answer=[1] * len(results),
                extracted_answer=results,
            )
            convo = prompt_messages + [
                dict(content=completion, role="assistant") for completion in completions
            ]
            return SingleEvalResult(
                html=html,
                score=score,
                convo=convo,
                metrics={
                    f"pass@{k}": estimate_pass_at_k([total], [correct], k).tolist()
                    # this will be aggrated so no need of .mean()
                    for k in self._ks_passes
                    if total >= k
                },
            )

        num_already_processed = len(self.processed_results)

        if num_already_processed >= len(self.examples):
            if not self.examples:  # No examples to run at all
                print("No examples to evaluate.")
                return common.aggregate_results([])  # Return empty aggregated result
            print("All examples were already processed according to checkpoint.")
            return common.aggregate_results(self.processed_results)

        examples_to_process_this_run = self.examples[num_already_processed:]
        num_total_examples_in_run = len(self.examples)

        print(
            f"Starting evaluation. Total examples: {num_total_examples_in_run}. "
            f"Already processed: {num_already_processed}. "
            f"Remaining: {len(examples_to_process_this_run)}."
        )

        for i in range(0, len(examples_to_process_this_run), self.batch_size):
            batch_examples = examples_to_process_this_run[i : i + self.batch_size]
            if not batch_examples:
                continue

            current_global_start_index_for_batch = num_already_processed + i

            batch_start_num_display = current_global_start_index_for_batch + 1
            batch_end_num_display = min(
                current_global_start_index_for_batch + len(batch_examples),
                num_total_examples_in_run,
            )

            print(
                f"Processing batch: examples {batch_start_num_display}-"
                f"{batch_end_num_display} of {num_total_examples_in_run} "
                f"(Batch size: {self.batch_size})"
            )

            batch_new_results: list[SingleEvalResult] = common.map_with_progress(
                fn, batch_examples, num_threads=3
            )
            self.processed_results.extend(batch_new_results)  # Add new results to the main list

            if self.checkpoint_file and batch_new_results:  # Only save if there are new results
                common.save_checkpoint(
                    self.checkpoint_file, batch_new_results
                )  # Append only the newly processed results

        print(
            f"Evaluation finished. Processed {len(self.processed_results)} results in total out of {num_total_examples_in_run} examples."
        )
        return common.aggregate_results(self.processed_results)
