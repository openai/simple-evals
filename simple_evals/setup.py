from setuptools import setup, find_packages

setup(
    name="simple-evals",
    version="0.1.0",
    description="A lightweight library for evaluating language models",
    author="OpenAI",
    packages=find_packages(),
    install_requires=[
        "openai",  # For OpenAI API
        "anthropic",  # For Claude API
    ],
    extras_require={
        "humaneval": ["human-eval"],  # Optional dependency for HumanEval
    },
    python_requires=">=3.8",
) 