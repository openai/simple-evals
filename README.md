# Overview
This repository contains a lightweight library for evaluating language models.
We are open sourcing it so we can be transparent about the accuracy numbers we're publishing alongside our latest models (starting with `gpt-4-turbo-2024-04-09`).

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


## Benchmark Results
| Model                         | Prompt        |DROP(f1)| GPQA%   |   MATH% |   MGSM% |   MMLU% |HumanEval% | 
|:-----------------------------:|:-------------:|:------:|:-------:|:-------:|:-------:|:-------:|:---------:| 
|     GPT4s                     |               |        |         |         |         |         |           |
| gpt-4-turbo-2024-04-09        | chatgpt[^1]   |   85.4 |  49.1   |   72.2  |   88.6  |   86.5  |      87.6 |
| gpt-4-turbo-2024-04-09        | assistant[^2] |   86.0 |  49.3   |   73.4  |   89.6  |   86.7  |      88.2 |
| gpt-4-1106(-vision)-preview   | chatgpt       |   81.3 |  42.1   |   64.1  |   86.5  |   84.6  |      82.2 |
| gpt-4-1106(-vision)-preview   | assistant     |   83.2 |  42.5   |   64.3  |   87.1  |   84.7  |      83.7 |
| gpt-4-0125-preview            | chatgpt       |   83.4 |  39.7   |   64.2  |   83.7  |   84.8  |      88.2 |
| gpt-4-0125-preview            | assistant     |   81.5 |  41.4   |   64.5  |   85.1  |   85.4  |      86.6 |
| REFERENCE                     |               |                  |         |         |         |           |
| Claude-3-Opus (rerun w/ api)  | empty[^3]     |   79.0 |  49.7   |   63.2  |   89.7  |   84.1  |      84.8 |
| Claude-3-Opus (rerun w/ api)  | lmsys[^4]     |   77.1 |  50.7   |   63.8  |   89.2  |   84.2  |      82.9 |
| Claude-3-Opus (report[^5])    | unknown       |   83.1 |  50.4   |   60.1  |   90.7  |   86.8  |      84.9 |
| Gemini-Ultra-1.0 (report[^6]) | unknown       |   82.4 | n/a     |   53.2  |  79.0   |   83.7  |      74.4 |
| Gemini-Pro-1.5 (report[^6])   | unknown       |   78.9 | n/a     |   58.5  |   88.7  |   81.9  |      71.9 |

[^1]:chatgpt system message: "You are ChatGPT, a large language model trained by OpenAI, based on the GPT-4 architecture.\nKnowledge cutoff: 2023-12\nCurrent date: 2024-04-01"
[^2]:assistant system message in [OpenAI API doc](https://platform.openai.com/docs/api-reference/introduction): "You are a helpful assistant." .
[^3]:claude-3 empty system message: suggested by Anthropic API doc, and we have done limited experiments due to [rate limit](https://docs.anthropic.com/claude/reference/rate-limits) issues, but we welcome PRs with alternative choices. 
[^4]:claude-3 lmsys system message: system message in LMSYS [Fast-chat open source code](https://github.com/lm-sys/FastChat/blob/7899355ebe32117fdae83985cf8ee476d2f4243f/fastchat/conversation.py#L894): "The assistant is Claude, created by Anthropic. The current date is {{currentDateTime}}. Claude's knowledge base was last updated ... ". We have done limited experiments due to [rate limit](https://docs.anthropic.com/claude/reference/rate-limits) issues, but we welcome PRs with alternative choices. 
[^5]:claude-3 reports: [https://www.anthropic.com/news/claude-3-family](https://www.anthropic.com/news/claude-3-family).
[^6]:gemini-1.5 reports: [https://blog.google/technology/ai/google-gemini-next-generation-model-february-2024/](https://blog.google/technology/ai/google-gemini-next-generation-model-february-2024/), we dont have rerun results due to [rate_limit](https://ai.google.dev/pricing) issues and paid-as-you-go version are still "coming soon" by the time of this study on 04/02. 

## Legal Stuff
By contributing to evals, you are agreeing to make your evaluation logic and data under the same MIT license as this repository. You must have adequate rights to upload any data used in an eval. OpenAI reserves the right to use this data in future service improvements to our product. Contributions to OpenAI evals will be subject to our usual Usage Policies: https://platform.openai.com/docs/usage-policies.
