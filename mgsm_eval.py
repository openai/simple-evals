"""
MGSM: Multilingual Grade School Math Benchmark (MGSM) is a benchmark of grade-school math problems. 
Language Models are Multilingual Chain-of-Thought Reasoners
Freda Shi, Mirac Suzgun, Markus Freitag, Xuezhi Wang, Suraj Srivats, Soroush Vosoughi, Hyung Won Chung, Yi Tay, Sebastian Ruder, Denny Zhou, Dipanjan Das, Jason Wei
https://arxiv.org/abs/2210.03057 reference: https://github.com/google-research/url-nlp 
"""

import re
from typing import Optional
import pathlib
import urllib.request

import common
from mmlu_eval import HTML_JINJA
from eval_types import Eval, EvalResult, SamplerBase, SingleEvalResult

ALL_LANGUAGES = ["bn", "de", "en", "es", "fr", "ja", "ru", "sw", "te", "th", "zh"]
LATIN_LANGUAGES = ["de", "en", "es", "fr", "sw"]
NON_LATIN_LANGUAGES = ["bn", "ja", "ru", "te", "th", "zh"]

LANG_TO_FPATH = {
    "bn": "https://openaipublic.blob.core.windows.net/simple-evals/mgsm_bn.tsv",
    "de": "https://openaipublic.blob.core.windows.net/simple-evals/mgsm_de.tsv",
    "en": "https://openaipublic.blob.core.windows.net/simple-evals/mgsm_en.tsv",
    "es": "https://openaipublic.blob.core.windows.net/simple-evals/mgsm_es.tsv",
    "fr": "https://openaipublic.blob.core.windows.net/simple-evals/mgsm_fr.tsv",
    "ja": "https://openaipublic.blob.core.windows.net/simple-evals/mgsm_ja.tsv",
    "ru": "https://openaipublic.blob.core.windows.net/simple-evals/mgsm_ru.tsv",
    "sw": "https://openaipublic.blob.core.windows.net/simple-evals/mgsm_sw.tsv",
    "te": "https://openaipublic.blob.core.windows.net/simple-evals/mgsm_te.tsv",
    "th": "https://openaipublic.blob.core.windows.net/simple-evals/mgsm_th.tsv",
    "zh": "https://openaipublic.blob.core.windows.net/simple-evals/mgsm_zh.tsv",
}
LANG_TO_INSTRUCTIONS = {
    "en": """Solve this math problem. Give the reasoning steps before giving the final answer on the last line by itself in the format of "Answer:". Do not add anything other than the integer answer after "Answer:".

{input}""",
    "bn": """এই গণিতের সমস্যাটি সমাধান করুন। চূড়ান্ত উত্তর দেওয়ার আগে যুক্তিসম্পন্ন পদক্ষেপ প্রদান করুন। চূড়ান্ত উত্তরটি একক সংখ্যা হিসাবে "উত্তর:" এর পরে শেষ লাইনে দিন। "উত্তর:" এর পরে অন্য কিছু যুক্ত করবেন না।.

{input}""",
    "de": """Löse dieses Mathematikproblem. Gib die Schritte zur Begründung an, bevor du die endgültige Antwort in der letzten Zeile alleine im Format "Antwort:" gibst. Füge nichts anderes als die ganzzahlige Antwort nach "Antwort:" hinzu.

{input}""",
    "es": """Resuelve este problema matemático. Proporciona los pasos de razonamiento antes de dar la respuesta final en la última línea por sí misma en el formato de "Respuesta:". No añadas nada más que la respuesta entera después de "Respuesta:".

{input}""",
    "fr": """Résolvez ce problème de mathématiques. Donnez les étapes de raisonnement avant de fournir la réponse finale sur la dernière ligne elle-même dans le format de "Réponse:". N'ajoutez rien d'autre que la réponse entière après "Réponse:".

{input}""",
    "ja": """の数学の問題を解いてください。最終的な答えを出す前に、解答の推論過程を記述してください。そして最後の行には "答え:" の形式で答えを記述し、その後には整数の答え以外何も追加しないでください。

{input}""",
    "ru": """Решите эту математическую задачу. Объясните шаги рассуждения перед тем, как дать окончательный ответ в последней строке сам по себе в формате "Ответ:". Не добавляйте ничего, кроме целочисленного ответа после "Ответ:".

{input}""",
    "sw": """Suluhisha tatizo hili la hesabu. Toa hatua za mantiki kabla ya kutoa jibu la mwisho kwenye mstari wa mwisho peke yake katika muundo wa "Jibu:". Usiongeze chochote kingine isipokuwa jibu la integer baada ya "Jibu:".

{input}""",
    "te": """ఈ గణిత సమస్యను పరిష్కరించండి. చివరి సమాధానాన్ని ఇవ్వదానికి ముందు తర్కాత్మక అదుగులను ఇవ్వండి. చివరి పంక్తిలో మాత్రమే 'సమాధానం:' అనే ఆకారంలో చివరి సమాధానాద్ని ఇవ్వండి సమాధానం: తర్వాత పూర్ణాంక సమాధానానికి తప్పించి ఎదేనా చేర్చవద్దు.

{input}""",
    "th": """แก้ปัญหาคณิตศาสตร์นี้ ให้ให้ขั้นตอนการใช้เหตุผลก่อนที่จะให้คำตอบสุดท้ายในบรรทัดสุดท้ายโดยอยู่ในรูปแบบ "คำตอบ:" ไม่ควรเพิ่มอะไรนอกจากคำตอบที่เป็นจำนวนเต็มหลังจาก "คำตอบ:"

{input}""",
    "zh": """解决这个数学问题。在最后一行给出答案前，请提供推理步骤。最后一行应该以 "答案: " 的形式独立给出答案。在 "答案：" 后不要添加除整数答案之外的任何内容。

{input}""",
}

LANG_TO_ANSWER_PREFIX = {
    "en": "Answer",
    "bn": "উত্তর",
    "de": "Antwort",
    "es": "Respuesta",
    "fr": "Réponse",
    "ja": "答え",
    "ru": "Ответ",
    "sw": "Jibu",
    "te": "సమాధానం",
    "th": "คำตอบ",
    "zh": "答案",
}

CACHE_DIR = pathlib.Path(".simple_evals_cache")

def parse_answer(answer: str, answer_prefix: str) -> str:
    if answer_prefix not in answer:
        return ""

    answer_text = answer.split(answer_prefix)[-1].strip()

    # find all the numbers (including decimals) in the string
    numbers = re.findall(r"\d+\.?\d*", answer_text.replace(",", ""))

    # return the first number (removing trailing decimal point if present),
    # or an empty string if there were no numbers
    return numbers[-1].rstrip(".") if numbers else ""


def score_mgsm(target: str, prediction: str) -> bool:
    if "." in prediction:
        prediction = prediction.rstrip("0").rstrip(".")

    target = target.replace(",", "")
    prediction = prediction.replace(",", "")

    return target == prediction


def get_lang_examples(lang: str) -> list[dict[str, str]]:
    fpath = LANG_TO_FPATH[lang]
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    file_name = fpath.split("/")[-1]
    cached_file_path = CACHE_DIR / file_name

    if not cached_file_path.exists():
        print(f"Downloading MGSM data for lang '{lang}' from {fpath} to {cached_file_path}")
        urllib.request.urlretrieve(fpath, str(cached_file_path))
    else:
        print(f"Loading cached MGSM data for lang '{lang}' from {cached_file_path}")

    examples = []
    with open(cached_file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            inputs, targets = line.split("\t")
            if "." in targets:
                raise ValueError(f"targets {targets} contains a decimal point.")
            examples.append({"inputs": inputs, "targets": targets, "lang": lang})
    return examples


def get_all_examples() -> list[dict[str, str]]:
    examples = []
    for lang in ALL_LANGUAGES:
        if lang != "en":
            continue
        examples += get_lang_examples(lang)
    return examples


class MGSMEval(Eval):
    def __init__(
        self,
        num_examples_per_lang: int = 250,  # restrict to a subset of the data for debugging
        languages: Optional[list[str]] = ALL_LANGUAGES,
        batch_size: int = 20, # Default batch size
        checkpoint_file: str | None = None, # Path to the checkpoint file
    ):
        if languages is None:
            languages = ALL_LANGUAGES
        else:
            for language in languages:
                if language not in ALL_LANGUAGES:
                    raise ValueError(
                        f"language {language} is not a valid language. "
                        f"It should be one in {ALL_LANGUAGES}"
                    )
        self._languages = languages
        self._num_examples_per_lang = num_examples_per_lang

        examples = []
        for lang in self._languages:
            lang_examples = get_lang_examples(lang)
            examples.extend(lang_examples[: self._num_examples_per_lang])
        self.examples = examples
        
        self.batch_size = batch_size
        self.checkpoint_file = checkpoint_file
        self.processed_results: list[SingleEvalResult] = []

        if self.checkpoint_file:
            self.processed_results = common.load_checkpoint(self.checkpoint_file)

    def __call__(self, sampler: SamplerBase) -> EvalResult:
        def fn(example: dict[str, str]):
            language = example["lang"]
            latin_language = "group_latin" if language in LATIN_LANGUAGES else "group_non_latin"
            correct_answer = example["targets"]
            instruction = LANG_TO_INSTRUCTIONS[language]
            prompt_messages = [
                sampler._pack_message(
                    content=instruction.format(input=example["inputs"]), role="user"
                )
            ]
            try:
                response_text = sampler(prompt_messages)
            except Exception as e:
                response_text = ""

            answer_prefix = LANG_TO_ANSWER_PREFIX[language]
            extracted_answer = parse_answer(response_text, answer_prefix)

            score = score_mgsm(correct_answer, extracted_answer)
            html = common.jinja_env.from_string(HTML_JINJA).render(
                prompt_messages=prompt_messages,
                next_message=dict(content=response_text, role="assistant"),
                score=score,
                correct_answer=correct_answer,
                extracted_answer=extracted_answer or None,
            )
            convo = prompt_messages + [dict(content=response_text, role="assistant")]
            return SingleEvalResult(
                html=html,
                score=score,
                convo=convo,
                metrics={language: score, latin_language: score},
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

        print(f"Starting MGSM evaluation. Total examples: {num_total_examples_in_run}. Already processed: {num_already_processed}. Remaining: {len(examples_to_process_this_run)}.")

        for i in range(0, len(examples_to_process_this_run), self.batch_size):
            batch_examples = examples_to_process_this_run[i : i + self.batch_size]
            if not batch_examples:
                continue

            current_global_start_index_for_batch = num_already_processed + i
            
            batch_start_num_display = current_global_start_index_for_batch + 1
            batch_end_num_display = min(current_global_start_index_for_batch + len(batch_examples), num_total_examples_in_run)
            
            print(f"Processing batch: examples {batch_start_num_display}-{batch_end_num_display} of {num_total_examples_in_run} (Batch size: {self.batch_size})")
            
            batch_new_results: list[SingleEvalResult] = common.map_with_progress(fn, batch_examples)
            self.processed_results.extend(batch_new_results)
            
            if self.checkpoint_file and batch_new_results:
                common.save_checkpoint(self.checkpoint_file, batch_new_results)
        
        print(f"MGSM evaluation finished. Processed {len(self.processed_results)} results in total out of {num_total_examples_in_run} examples.")
        return common.aggregate_results(self.processed_results, default_stats=("mean", "std"))
