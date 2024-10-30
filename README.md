# Overview
This repository contains a lightweight library for evaluating language models.
We are open sourcing it so we can be transparent about the accuracy numbers we're publishing alongside our latest models.

## Benchmark Results

| Model                        | Prompt        | MMLU   | GPQA   | MATH   | HumanEval | MGSM[^5] | DROP[^5]<br>(F1, 3-shot) | SimpleQA 
|:----------------------------:|:-------------:|:------:|:------:|:------:|:---------:|:------:|:--------------------------:|:---------:| 
| **o1**                       |               |        |        | MATH-500[^6] |          |        |                           |          
| o1-preview                   | n/a[^7]       |  90.8  |  73.3  |  85.5  | **`92.4`** |  90.8  |  74.8                      | **`42.4`** | 
| o1-mini                      | n/a           |  85.2  |  60.0  |  90.0  | **`92.4`** |  89.9  |  83.9                      | 7.6        |  
| o1 (work in progress)        | n/a           | **`92.3`** | **`77.3`** | **`94.8`** |   n/a    |   n/a  |   n/a            |   n/a 
| **GPT-4o**                   |               |        |        |        |           |        |                        |
| gpt-4o-2024-08-06            | assistant[^2] |  88.7  |  53.1  |  75.9  |   90.2    |  90.0  |  79.8                       | 40.1       |  
| gpt-4o-2024-05-13            | assistant     |  87.2  |  49.9  |  76.6  |   91.0    |  89.9  |  83.7                       | 39.0       |
| gpt-4o-mini-2024-07-18       | assistant     |  82.0  |  40.2  |  70.2  |   87.2    |  87.0  |  79.7                       | 9.5        | 
| **GPT-4 Turbo and GPT-4**     |               |        |        |        |           |        |                            |
| gpt-4-turbo-2024-04-09       | assistant     |  86.7  |  49.3  |  73.4  |   88.2    |  89.6  |  86.0                       | 24.2       |
| gpt-4-0125-preview           | assistant     |  85.4  |  41.4  |  64.5  |   86.6    |  85.1  |  81.5                       | n/a 
| gpt-4-1106-preview           | assistant     |  84.7  |  42.5  |  64.3  |   83.7    |  87.1  |  83.2                       | n/a 
| **Other Models (Reported)**   |               |        |        |        |           |        |                            |
| [Claude 3.5 Sonnet](https://www.anthropic.com/news/claude-3-5-sonnet) | unknown |  88.3  |  59.4  |  71.1  |   92.0    | **`91.6`** | **`87.1`** |  28.9 | 
| [Claude 3 Opus](https://www.anthropic.com/news/claude-3-family) | unknown |  86.8  |  50.4  |  60.1  |   84.9    |   90.7   |  83.1 |  23.5 |                   
| [Llama 3.1 405b](https://github.com/meta-llama/llama-models/blob/main/models/llama3_1/MODEL_CARD.md) | unknown |  88.6  |  50.7  |  73.8  |   89.0    | **`91.6`** |  84.8                   | n/a 
| [Llama 3.1 70b](https://github.com/meta-llama/llama-models/blob/main/models/llama3_1/MODEL_CARD.md) | unknown |  82.0  |  41.7  |  68.0  |   80.5    |  86.9  |  79.6                   | n/a 
| [Llama 3.1 8b](https://github.com/meta-llama/llama-models/blob/main/models/llama3_1/MODEL_CARD.md) | unknown |  68.4  |  30.4  |  51.9  |   72.6    |  68.9  |  59.5                   | n/a 
| [Grok 2](https://x.ai/blog/grok-2) | unknown | 87.5 | 56.0 | 76.1 | 88.4 | n/a | n/a | n/a 
| [Grok 2 mini](https://x.ai/blog/grok-2) | unknown | 86.2 | 51.0 | 73.0 | 85.7 | n/a | n/a | n/a 
| [Gemini 1.0 Ultra](https://goo.gle/GeminiV1-5) | unknown | 83.7 | n/a | 53.2 | 74.4 | 79.0 | 82.4 | n/a 
| [Gemini 1.5 Pro](https://goo.gle/GeminiV1-5) | unknown | 81.9 | n/a | 58.5 | 71.9 | 88.7 | 78.9 | n/a 
| [Gemini 1.5 Flash](https://goo.gle/GeminiV1-5) | unknown | 77.9 | 38.6 | 40.9 | 71.5 | 75.5 | 78.4 | n/a 

## Background

Evals are sensitive to prompting, and there's significant variation in the formulations used in recent publications and libraries.
Some use few-shot prompts or role playing prompts ("You are an expert software programmer...").
These approaches are carryovers from evaluating *base models* (rather than instruction/chat-tuned models) and from models that were worse at following instructions.

For this library, we are emphasizing the *zero-shot, chain-of-thought* setting, with simple instructions like "Solve the following multiple choice problem". We believe that this prompting technique is a better reflection of the models' performance in realistic usage.

**We will not be actively maintaining this repository and monitoring PRs and Issues.** In particular, we're not accepting new evals. Here are the changes we might accept.
- Bug fixes (hopefully not needed!)
- Adding adapters for new models
- Adding new rows to the table below with eval results, given new models and new system prompts.

This repository is NOT intended as a replacement for https://github.com/openai/evals, which is designed to be a comprehensive collection of a large number of evals.

## Evals

This repository currently contains the following evals:

- MMLU: Measuring Massive Multitask Language Understanding, reference: https://arxiv.org/abs/2009.03300, https://github.com/hendrycks/test, [MIT License](https://github.com/hendrycks/test/blob/master/LICENSE)
- MATH: Measuring Mathematical Problem Solving With the MATH Dataset, reference: https://arxiv.org/abs/2103.03874, https://github.com/hendrycks/math, [MIT License](https://github.com/idavidrein/gpqa/blob/main/LICENSE)
- GPQA: A Graduate-Level Google-Proof Q&A Benchmark, reference: https://arxiv.org/abs/2311.12022, https://github.com/idavidrein/gpqa/,  [MIT License](https://github.com/idavidrein/gpqa/blob/main/LICENSE)
- DROP: A Reading Comprehension Benchmark Requiring Discrete Reasoning Over Paragraphs, reference: https://arxiv.org/abs/1903.00161, https://allenai.org/data/drop, [Apache License 2.0](https://github.com/allenai/allennlp-models/blob/main/LICENSE)
- MGSM: Multilingual Grade School Math Benchmark (MGSM), Language Models are Multilingual Chain-of-Thought Reasoners, reference: https://arxiv.org/abs/2210.03057, https://github.com/google-research/url-nlp, [Creative Commons Attribution 4.0 International Public License (CC-BY)](https://github.com/google-research/url-nlp/blob/main/LICENSE)
- HumanEval: Evaluating Large Language Models Trained on Code, reference https://arxiv.org/abs/2107.03374, https://github.com/openai/human-eval, [MIT License](https://github.com/openai/human-eval/blob/master/LICENSE)

## Samplers

We have implemented sampling interfaces for the following language model APIs:

- OpenAI: https://platform.openai.com/docs/overview
- Claude: https://www.anthropic.com/api

Make sure to set the `*_API_KEY` environment variables before using these APIs.

## Setup

Due to the optional dependencies, we're not providing a unified setup mechanism. Instead, we're providing instructions for each eval and sampler.

For [HumanEval](https://github.com/openai/human-eval/) (python programming)
```bash
git clone https://github.com/openai/human-eval
pip install -e human-eval
```

For the [OpenAI API](https://pypi.org/project/openai/):
```bash
pip install openai
```

For the [Anthropic API](https://docs.anthropic.com/claude/docs/quickstart-guide):
```bash
pip install anthropic
```

## Demo
```bash
python -m simple-evals.demo
```
This will launch evaluations through the OpenAI API.

## Notes

[^1]:chatgpt system message: "You are ChatGPT, a large language model trained by OpenAI, based on the GPT-4 architecture.\nKnowledge cutoff: 2023-12\nCurrent date: 2024-04-01"
[^2]:assistant system message in [OpenAI API doc](https://platform.openai.com/docs/api-reference/introduction): "You are a helpful assistant." .
[^3]:claude-3 empty system message: suggested by Anthropic API doc, and we have done limited experiments due to [rate limit](https://docs.anthropic.com/claude/reference/rate-limits) issues, but we welcome PRs with alternative choices.
[^4]:claude-3 lmsys system message: system message in LMSYS [Fast-chat open source code](https://github.com/lm-sys/FastChat/blob/7899355ebe32117fdae83985cf8ee476d2f4243f/fastchat/conversation.py#L894): "The assistant is Claude, created by Anthropic. The current date is {{currentDateTime}}. Claude's knowledge base was last updated ... ". We have done limited experiments due to [rate limit](https://docs.anthropic.com/claude/reference/rate-limits) issues, but we welcome PRs with alternative choices.
[^5]:We believe these evals are saturated for our newer models, but are reporting them for completeness.
[^6]:For o1 models, we evaluate on [MATH-500](https://github.com/openai/prm800k/tree/main/prm800k/math_splits), which is a newer, IID version of MATH.
[^7]:o1 models do not support using a system prompt.

## Legal Stuff
By contributing to evals, you are agreeing to make your evaluation logic and data under the same MIT license as this repository. You must have adequate rights to upload any data used in an eval. OpenAI reserves the right to use this data in future service improvements to our product. Contributions to OpenAI evals will be subject to our usual Usage Policies: https://platform.openai.com/docs/usage-policies.
