"""
GPQA: A Graduate-Level Google-Proof Q&A Benchmark
David Rein, Betty Li Hou, Asa Cooper Stickland, Jackson Petty, Richard Yuanzhe Pang, Julien Dirani, Julian Michael, Samuel R. Bowman
https://arxiv.org/abs/2311.12022
"""

import random
import re
import pathlib
import urllib.request

import pandas

import common
from common import ANSWER_PATTERN_MULTICHOICE, HTML_JINJA, format_multichoice_question
from eval_types import Eval, EvalResult, MessageList, SamplerBase, SingleEvalResult

CACHE_DIR = pathlib.Path(".simple_evals_cache")

class GPQAEval(Eval):
    def __init__(
        self,
        n_repeats: int = 4,
        variant: str = "diamond",
        num_examples: int | None = None,  # restrict to a subset of the data for debugging
        batch_size: int = 20, # Default batch size, can be configured
        checkpoint_file: str | None = None,  # Path to the checkpoint file
    ):
        rng = random.Random(0)  
        url = f"https://openaipublic.blob.core.windows.net/simple-evals/gpqa_{variant}.csv"
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        file_name = url.split("/")[-1]
        cached_file_path = CACHE_DIR / file_name

        if cached_file_path.exists():
            print(f"Loading cached GPQA data from {cached_file_path}")
            df_repeated = pandas.read_csv(cached_file_path)
        else:
            print(f"Downloading GPQA data from {url} to {cached_file_path}")
            urllib.request.urlretrieve(url, str(cached_file_path))
            df_repeated = pandas.read_csv(cached_file_path)
            
        all_examples_from_csv = [row.to_dict() for _, row in df_repeated.iterrows()]
        
        if num_examples:
            # If num_examples is used, n_repeats is 1 (assertion exists)
            # Sample *before* adding permutations.
            final_examples_base = rng.sample(all_examples_from_csv, num_examples)
        else:
            # Use all examples, then repeat
            final_examples_base = all_examples_from_csv * n_repeats

        # Now, assign a unique, deterministic permutation to each *instance* in final_examples_base
        # To make this deterministic across runs (even with checkpointing), we need a seed for each permutation.
        # We can use the index in this final_examples_base list.
        self.examples = []
        for i, ex in enumerate(final_examples_base):
            # Seed the RNG for permutation with a combination of global seed and instance index
            perm_rng = random.Random(i) # Using i as seed for this specific permutation
            self.examples.append(ex | {"permutation": perm_rng.sample(range(4), 4)})

        self.n_repeats = n_repeats # Though less directly used if num_examples is set
        self.batch_size = batch_size
        self.checkpoint_file = checkpoint_file
        self.processed_results: list[SingleEvalResult] = []

        if self.checkpoint_file:
            self.processed_results = common.load_checkpoint(self.checkpoint_file)

    def __call__(self, sampler: SamplerBase) -> EvalResult:
        def fn(row: dict):
            choices = [
                row["Correct Answer"],
                row["Incorrect Answer 1"],
                row["Incorrect Answer 2"],
                row["Incorrect Answer 3"],
            ]
            # Permutation is now pre-assigned and part of the 'row'
            choices = [choices[i] for i in row["permutation"]]
            correct_index = choices.index(row["Correct Answer"])
            correct_answer = "ABCD"[correct_index]
            choices_dict = dict(
                A=choices[0], B=choices[1], C=choices[2], D=choices[3], Question=row["Question"]
            )
            prompt_messages = [
                sampler._pack_message(
                    content=format_multichoice_question(choices_dict), role="user"
                )
            ]
            response_text = sampler(prompt_messages)
            match = re.search(ANSWER_PATTERN_MULTICHOICE, response_text)
            extracted_answer = match.group(1) if match else None
            score = 1.0 if extracted_answer == correct_answer else 0.0
            html = common.jinja_env.from_string(HTML_JINJA).render(
                prompt_messages=prompt_messages,
                next_message=dict(content=response_text, role="assistant"),
                score=score,
                correct_answer=correct_answer,
                extracted_answer=extracted_answer,
            )
            convo = prompt_messages + [dict(content=response_text, role="assistant")]
            return SingleEvalResult(
                html=html, score=score, convo=convo, metrics={"chars": len(response_text)}
            )

        num_already_processed = len(self.processed_results)
        
        if num_already_processed >= len(self.examples):
            if not self.examples: # No examples to run at all
                print("No examples to evaluate.")
                return common.aggregate_results([]) # Return empty aggregated result
            print("All examples were already processed according to checkpoint.")
            return common.aggregate_results(self.processed_results)

        examples_to_process_this_run = self.examples[num_already_processed:]
        num_total_examples_in_run = len(self.examples)

        print(f"Starting GPQA evaluation. Total examples: {num_total_examples_in_run}. Already processed: {num_already_processed}. Remaining: {len(examples_to_process_this_run)}.")

        for i in range(0, len(examples_to_process_this_run), self.batch_size):
            batch_examples = examples_to_process_this_run[i : i + self.batch_size]
            if not batch_examples:
                continue
            
            current_global_start_index_for_batch = num_already_processed + i
            batch_start_num_display = current_global_start_index_for_batch + 1
            batch_end_num_display = min(current_global_start_index_for_batch + len(batch_examples), num_total_examples_in_run)
            
            print(f"Processing batch: examples {batch_start_num_display}-{batch_end_num_display} of {num_total_examples_in_run} (Batch size: {self.batch_size})")
            
            # batch_new_results: list[SingleEvalResult] = [] # Not needed, common.map_with_progress returns a new list
            batch_new_results = common.map_with_progress(fn, batch_examples)
            self.processed_results.extend(batch_new_results)
            
            if self.checkpoint_file and batch_new_results:
                common.save_checkpoint(self.checkpoint_file, batch_new_results)
        
        print(f"GPQA evaluation finished. Processed {len(self.processed_results)} results in total out of {num_total_examples_in_run} examples.")
        return common.aggregate_results(self.processed_results)
