"""
Measuring Massive Multitask Language Understanding
Dan Hendrycks, Collin Burns, Steven Basart, Andy Zou, Mantas Mazeika, Dawn Song, Jacob Steinhardt
https://arxiv.org/abs/2009.03300
"""

import random
import re
import pandas
from typing import Any, Dict, Optional, List

from common import ANSWER_PATTERN_MULTICHOICE, format_multichoice_question, map_with_progress, aggregate_results
from typings import EvalResult, SingleEvalResult

from models.base import SamplerBase
from evals.base import EvalBase

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

MMLU_CSV_URL = "https://openaipublic.blob.core.windows.net/simple-evals/mmlu.csv"
RANDOM_SEED = 0

class MMLUEval(EvalBase):
    def __init__(self, num_examples: Optional[int] = None, k_shots: int = 0):
        self.k_shots = k_shots

        df = pandas.read_csv(MMLU_CSV_URL)
        examples = [row.to_dict() for _, row in df.iterrows()]
        
        self.examples = examples

        if k_shots > 0:
            print(f"Sampling {k_shots} shots per example")
        k_shot_samples_per_example = [self.sample_k_shots(row, self.k_shots) for row in self.examples]
        self.examples = [
            {**row, "k_shots": k_shot_samples} for row, k_shot_samples in zip(self.examples, k_shot_samples_per_example)
        ]

        if num_examples:
            self.examples = random.Random(RANDOM_SEED).sample(self.examples, num_examples)
        
    def sample_k_shots(self, row: Dict[str, Any], k_shots: int) -> List[Dict[str, Any]]:
        sample = random.sample(self.examples, k_shots)
        # Assert that the sample does not contain the row itself
        while row in sample:
            sample.remove(row)
            sample.append(random.choice(self.examples))
        return sample

    def __call__(self, sampler: SamplerBase) -> EvalResult:
        def get_single_eval_result(row: Dict[str, Any]) -> SingleEvalResult:
            k_shot_messages = [
                sampler._pack_message(content=format_multichoice_question(row), role="user")
                for row in row["k_shots"]
            ]
            prompt_messages = k_shot_messages + [
                sampler._pack_message(content=format_multichoice_question(row), role="user")
            ]
            response_text = sampler(prompt_messages)

            match = re.search(ANSWER_PATTERN_MULTICHOICE, response_text)
            extracted_answer = match.group(1) if match else None
            score = 1.0 if extracted_answer == row["Answer"] else 0.0
            
            convo = prompt_messages + [dict(content=response_text, role="assistant")]
            
            category = subject2category.get(row["Subject"], "other")
            
            return SingleEvalResult(score=score, metrics={category: score}, convo=convo)

        results = map_with_progress(get_single_eval_result, self.examples)
        return aggregate_results(results)
