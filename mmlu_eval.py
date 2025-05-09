"""
Measuring Massive Multitask Language Understanding
Dan Hendrycks, Collin Burns, Steven Basart, Andy Zou, Mantas Mazeika, Dawn Song, Jacob Steinhardt
https://arxiv.org/abs/2009.03300
"""

import random
import re
import os
import json
import pathlib
import urllib.request

import pandas

import common
from common import (
    HTML_JINJA,
    MULTILINGUAL_ANSWER_PATTERN_TEMPLATE,
    MULTILINGUAL_ANSWER_REGEXES,
    format_multichoice_question,
    normalize_extracted_answer,
    normalize_response,
)
from eval_types import Eval, EvalResult, SamplerBase, SingleEvalResult

subject2category = {
    "abstract_algebra": "stem",
    "anatomy": "other",
    "astronomy": "stem",
    "business_ethics": "other",
    "clinical_knowledge": "other",
    "college_biology": "stem",
    "college_chemistry": "stem",
    "college_computer_science": "stem",
    "college_mathematics": "stem",
    "college_medicine": "other",
    "college_physics": "stem",
    "computer_security": "stem",
    "conceptual_physics": "stem",
    "econometrics": "social_sciences",
    "electrical_engineering": "stem",
    "elementary_mathematics": "stem",
    "formal_logic": "humanities",
    "global_facts": "other",
    "high_school_biology": "stem",
    "high_school_chemistry": "stem",
    "high_school_computer_science": "stem",
    "high_school_european_history": "humanities",
    "high_school_geography": "social_sciences",
    "high_school_government_and_politics": "social_sciences",
    "high_school_macroeconomics": "social_sciences",
    "high_school_mathematics": "stem",
    "high_school_microeconomics": "social_sciences",
    "high_school_physics": "stem",
    "high_school_psychology": "social_sciences",
    "high_school_statistics": "stem",
    "high_school_us_history": "humanities",
    "high_school_world_history": "humanities",
    "human_aging": "other",
    "human_sexuality": "social_sciences",
    "international_law": "humanities",
    "jurisprudence": "humanities",
    "logical_fallacies": "humanities",
    "machine_learning": "stem",
    "management": "other",
    "marketing": "other",
    "medical_genetics": "other",
    "miscellaneous": "other",
    "moral_disputes": "humanities",
    "moral_scenarios": "humanities",
    "nutrition": "other",
    "philosophy": "humanities",
    "prehistory": "humanities",
    "professional_accounting": "other",
    "professional_law": "humanities",
    "professional_medicine": "other",
    "professional_psychology": "social_sciences",
    "public_relations": "social_sciences",
    "security_studies": "social_sciences",
    "sociology": "social_sciences",
    "us_foreign_policy": "social_sciences",
    "virology": "other",
    "world_religions": "humanities",
}

CACHE_DIR = pathlib.Path(".simple_evals_cache")

class MMLUEval(Eval):
    def __init__(
        self,
        num_examples: int | None = None,
        language: str = "EN-US",
        batch_size: int = 20,  # Default batch size, can be configured
        checkpoint_file: str | None = None,  # Path to the checkpoint file
    ):
        if language != "EN-US":
            url = f"https://openaipublic.blob.core.windows.net/simple-evals/mmlu_{language}.csv"
        else:
            url = "https://openaipublic.blob.core.windows.net/simple-evals/mmlu.csv"
        
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        file_name = url.split("/")[-1]
        cached_file_path = CACHE_DIR / file_name

        if cached_file_path.exists():
            print(f"Loading cached MMLU data from {cached_file_path}")
            df = pandas.read_csv(cached_file_path)
        else:
            print(f"Downloading MMLU data from {url} to {cached_file_path}")
            urllib.request.urlretrieve(url, str(cached_file_path))
            df = pandas.read_csv(cached_file_path)
            
        all_examples_from_csv = [row.to_dict() for _, row in df.iterrows()]

        if num_examples is not None and num_examples > 0:
            # Deterministic sampling if num_examples is specified
            k = min(num_examples, len(all_examples_from_csv))
            self.examples = random.Random(0).sample(all_examples_from_csv, k)
        else:
            # Use all examples if num_examples is None, 0, or negative
            self.examples = all_examples_from_csv
        
        self.batch_size = batch_size
        self.checkpoint_file = checkpoint_file
        self.processed_results: list[SingleEvalResult] = [] # Initialize empty

        if self.checkpoint_file:
            self.processed_results = common.load_checkpoint(self.checkpoint_file)

    def __call__(self, sampler: SamplerBase) -> EvalResult:
        def process_example(row: dict) -> SingleEvalResult:
            prompt_messages = [
                sampler._pack_message(
                    content=format_multichoice_question(row), role="user"
                )
            ]
            response_text = normalize_response(sampler(prompt_messages))
            extracted_answer = None
            for answer_regex in MULTILINGUAL_ANSWER_REGEXES:
                regex = MULTILINGUAL_ANSWER_PATTERN_TEMPLATE.format(answer_regex)
                match = re.search(regex, response_text)
                if match:
                    extracted_answer = normalize_extracted_answer(match.group(1))
                    break
            score = 1.0 if extracted_answer == row["Answer"] else 0.0
            html = common.jinja_env.from_string(HTML_JINJA).render(
                prompt_messages=prompt_messages,
                next_message=dict(content=response_text, role="assistant"),
                score=score,
                correct_answer=row["Answer"],
                extracted_answer=extracted_answer,
            )
            convo = prompt_messages + [dict(content=response_text, role="assistant")]
            category = subject2category.get(row["Subject"], "other")
            return SingleEvalResult(
                html=html, score=score, metrics={category: score}, convo=convo
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

        print(f"Starting evaluation. Total examples: {num_total_examples_in_run}. Already processed: {num_already_processed}. Remaining: {len(examples_to_process_this_run)}.")

        for i in range(0, len(examples_to_process_this_run), self.batch_size):
            batch_examples = examples_to_process_this_run[i : i + self.batch_size]
            if not batch_examples:
                continue

            current_global_start_index_for_batch = num_already_processed + i
            
            batch_start_num_display = current_global_start_index_for_batch + 1
            batch_end_num_display = min(current_global_start_index_for_batch + len(batch_examples), num_total_examples_in_run)
            
            print(f"Processing batch: examples {batch_start_num_display}-{batch_end_num_display} of {num_total_examples_in_run} (Batch size: {self.batch_size})")

            batch_new_results: list[SingleEvalResult] = []
            batch_new_results = common.map_with_progress(process_example, batch_examples)
            self.processed_results.extend(batch_new_results) # Add new results to the main list
            
            if self.checkpoint_file and batch_new_results: # Only save if there are new results
                common.save_checkpoint(self.checkpoint_file, batch_new_results) # Append only the newly processed results
        
        print(f"Evaluation finished. Processed {len(self.processed_results)} results in total out of {num_total_examples_in_run} examples.")
        return common.aggregate_results(self.processed_results)
