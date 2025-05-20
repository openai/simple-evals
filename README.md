# Welcome to Language Model Evaluations!

Hello there! 👋 If you're curious about how different AI language models perform on various tasks, you've come to the right place! This repository contains a collection of tools designed to help you evaluate and understand the capabilities of these fascinating models.

We know that diving into new tools can sometimes feel a bit daunting, so we've put together this guide especially for beginners. Our aim is to walk you through everything, step by step, so you can get started on your language model evaluation journey with confidence.

Let's explore together!

## Prerequisites: Getting Your System Ready

Before you can start evaluating models, there are a few things you'll need to set up on your computer. Don't worry, we'll guide you through each one!

### 1. Python Installation

This toolkit is written in Python, so you'll need Python installed on your system.

*   **Requirement:** We recommend using **Python 3.8 or newer**.
*   **How to get it:** If you don't have Python installed, you can download the latest version from the official Python website: [python.org](https://www.python.org/downloads/)
*   **Check if installed:** You can check if you already have Python by opening your terminal (or Command Prompt on Windows) and typing `python --version` or `python3 --version`.

### 2. Installing Necessary Python Libraries

Once Python is set up, you'll need to install a few key libraries that our evaluation scripts depend on. These libraries help with tasks like interacting with model APIs and handling data.

*   **Command:** Open your terminal and run the following command:
    ```bash
    pip install openai anthropic pandas
    ```
    *   `pip` is Python's package installer, and it comes with Python.
    *   `openai` and `anthropic` are libraries that allow our scripts to talk to the APIs of OpenAI (for models like GPT-4) and Anthropic (for models like Claude).
    *   `pandas` is a library used for data handling, which is helpful for managing the datasets used in evaluations.

### 3. API Keys: Your Access Pass to Language Models

To evaluate most of the powerful language models available today (like those from OpenAI or Anthropic), you need to use their Application Programming Interfaces (APIs). Think of an API as a way for computer programs to talk to each other. To use these APIs, you'll need API keys.

*   **What are API Keys?** An API key is a unique secret code that identifies you to the API provider (e.g., OpenAI). It's like a password that grants the scripts access to use the models. You'll need to sign up for an account with the respective providers (e.g., [OpenAI Platform](https://platform.openai.com/), [Anthropic Console](https://console.anthropic.com/)) to get your own API keys.

*   **Why Environment Variables? (Security First!)**
    It's very important **not to write your API keys directly into the code**. If you did, and you shared your code or uploaded it to a public place like GitHub, your secret keys would be exposed!
    Instead, we use **environment variables**. These are variables stored outside of your code but accessible by it. This way, your keys stay safe and private on your computer.

*   **Setting API Keys as Environment Variables:**
    You'll need to set environment variables for each model provider you plan to use. The common ones for this repository are:
    *   `OPENAI_API_KEY` for OpenAI models.
    *   `ANTHROPIC_API_KEY` for Anthropic models.

    Here's how to set them:

    *   **On Linux or macOS:**
        Open your terminal and type the following, replacing `"your_key_here"` with your actual API key:
        ```bash
        export OPENAI_API_KEY="your_openai_api_key_here"
        export ANTHROPIC_API_KEY="your_anthropic_api_key_here"
        ```
        *Note: This sets the variable for your current terminal session. To make it permanent, you'd add these lines to your shell's startup file (e.g., `~/.bashrc`, `~/.zshrc`, or `~/.profile`) and then either restart your terminal or "source" the file (e.g., `source ~/.bashrc`).*

    *   **On Windows:**
        Open Command Prompt (not PowerShell for the `set` command in this exact syntax) and type:
        ```cmd
        set OPENAI_API_KEY=your_openai_api_key_here
        set ANTHROPIC_API_KEY=your_anthropic_api_key_here
        ```
        To set it in PowerShell, the syntax is:
        ```powershell
        $Env:OPENAI_API_KEY="your_openai_api_key_here"
        $Env:ANTHROPIC_API_KEY="your_anthropic_api_key_here"
        ```
        *Note: The `set` command in Command Prompt sets the variable for the current session. For a more permanent setting on Windows, search for "environment variables" in the Start menu to open the System Properties dialog where you can add them.*

Once these prerequisites are sorted, you'll be ready to start running evaluations!

## Getting Started: Your First Steps

With the prerequisites out of the way, let's get the code and take our first steps into the world of language model evaluation.

### 1. Get the Code (Cloning the Repository)

The first thing you need is a copy of this repository's code on your computer. We use a tool called `git` for this. If you don't have `git` installed, you can download it from [git-scm.com](https://git-scm.com/downloads).

*   **Command:**
    Open your terminal and run the following command. This will download a copy of the repository into a new folder on your computer.
    ```bash
    git clone https://github.com/openai/simple-evals.git
    ```
    *(Note: If you're working with a personal fork or a different version of this repository, replace the URL above with the correct one for your specific case.)*

*   **What this does:**
    The `git clone` command "clones" (makes a copy of) the remote repository from GitHub onto your local machine. You'll see it create a new directory, likely named `simple-evals` (or matching the repository's name).

### 2. Navigate into the Repository Directory

Once the download is complete, you need to "enter" the newly created directory in your terminal so you can run the evaluation scripts.

*   **Command:**
    Assuming the repository was cloned into a folder named `simple-evals`, type:
    ```bash
    cd simple-evals
    ```
    If the folder was named something else, use that name instead (e.g., `cd your-repository-name`).

*   **What this does:**
    The `cd` (change directory) command changes your terminal's current working location to the specified directory. Now, any commands you type will be relative to this folder, which is where all the code and scripts reside.

You're now in the right place and ready to start using the evaluation tools!

## Running Your First Evaluation: A Step-by-Step Guide

Now that you have the code and are in the correct directory, let's run your first evaluation!

### Step 1: See What Models You Can Evaluate

Before you can tell the scripts to evaluate a model, you need to know which models this toolkit is set up to work with. Each model has a short name or "identifier" that you'll use.

*   **Why this is important:** You'll need one of these model identifiers for the next step when we run an actual evaluation.

*   **The Command:**
    In your terminal (make sure you're still inside the `simple-evals` directory!), type the following command and press Enter:
    ```bash
    python -m simple_evals.simple_evals --list-models
    ```

*   **Expected Output:**
    The script will print a list of available model identifiers. It will look something like this (the exact list might vary):
    ```
    Available models:
     - o3
     - o3_high
     - o3_low
     - o4-mini
     - gpt-4.1
     - gpt-4o
     - claude-3-opus-20240229_empty
     - ... (and so on)
    ```

*   **What to do with this list:**
    Take note of these model identifiers. You'll pick one of them to use in the very next step when you run your first test evaluation.

### Step 2: Run Your First (Simple) Evaluation

Now that you have a list of model identifiers, you're ready to run an actual evaluation! We'll start with a very small test to make sure everything is working and to give you a feel for the process.

*   **The Command:**
    Let's say you want to test the model `gpt-4o` (remember to pick a model from **your** list from Step 1!) on the `mmlu` benchmark, using only 5 questions. In your terminal (still in the `simple-evals` directory), you would type:
    ```bash
    python -m simple_evals.simple_evals --model gpt-4o --eval mmlu --examples 5
    ```

*   **Breaking Down the Command:**

    *   `python -m simple_evals.simple_evals`:
        *   This is the base part of the command that tells Python to run the main script from our evaluation toolkit.

    *   `--model gpt-4o`:
        *   `--model`: This flag tells the script that you're about to specify which language model to use.
        *   `gpt-4o`: This is where you put the identifier of the model you chose from Step 1. **If `gpt-4o` wasn't in your list, replace it with one that was!**

    *   `--eval mmlu`:
        *   `--eval`: This flag indicates that you're specifying which evaluation benchmark to run.
        *   `mmlu`: This is the identifier for the "Massive Multitask Language Understanding" benchmark, a popular and comprehensive test. It's a good one to start with. (Later, you can explore other benchmarks listed in the repository, like `math`, `humaneval`, etc.)

    *   `--examples 5`:
        *   `--examples`: This is a very important flag for your first few runs! It tells the script to only use a certain number of questions (examples) from the benchmark.
        *   `5`: In this case, we're only running 5 questions.
        *   **Why is this important?**
            *   **Speed:** Full benchmarks can have thousands of questions and take a long time. Using `--examples 5` makes the test run very quickly.
            *   **Cost-Saving:** Many models are accessed via APIs that charge based on usage. A small number of examples keeps your first test very low-cost (or even free, depending on the provider's trial terms).
            *   **Quick Check:** It allows you to verify that your setup, API keys, and the script itself are working correctly without waiting for a long time or spending much on API fees.

*   **Run it!**
    Once you've typed the command (customizing the model name if needed), press Enter. The script will begin its work. You should see some output in the terminal as it processes the questions.

### Step 3: Understand the Results

Great! You've run your first evaluation. Now, let's look at what the script produced. You'll find results both in your terminal and in more detailed report files.

*   **1. Console Output (What You See in the Terminal):**
    Once the script finishes (which should be quick for just 5 examples), you'll see some final messages in your terminal. This might include:
    *   A brief summary of the score (e.g., how many of the 5 questions the model got right).
    *   **Most importantly:** Paths to where the detailed report files have been saved. Look for lines like:
        ```
        Writing report to /tmp/mmlu_gpt-4o_YYYYMMDD_HHMMSS.html
        Writing results to /tmp/mmlu_gpt-4o_YYYYMMDD_HHMMSS.json
        Writing all results to /tmp/mmlu_gpt-4o_YYYYMMDD_HHMMSS_allresults.json
        ```
        *(The `YYYYMMDD_HHMMSS` part will be a timestamp of when you ran the evaluation.)*

*   **2. Report Files (The Detailed Breakdown):**
    The most useful information is saved in files. As the console output indicates, these are usually placed in a temporary directory (like `/tmp/` on Linux or macOS).

    *   **The HTML Report (`.html` file) - Your Best Friend!**
        *   **What it is:** This is a webpage file that you can open in any web browser (like Chrome, Firefox, Safari, etc.). This is the most user-friendly way to see your results.
        *   **How to open it:**
            1.  Look at your console output to find the exact filename ending in `.html`.
            2.  You can then open this file directly. For example, on most systems, you can navigate to the `/tmp/` directory in your file explorer and double-click the HTML file. Alternatively, you can often type `open /tmp/your_report_filename.html` (on macOS) or `start /tmp/your_report_filename.html` (on Windows) in your terminal.
        *   **What's inside:** This report will show you:
            *   Each **question** that was asked.
            *   The **model's full answer** to each question.
            *   The **correct answer** (for benchmarks where this applies).
            *   The **score** for each individual question (e.g., was it right or wrong?).
            *   An **overall score** for the (small) set of examples you ran.
        *   *This detailed view is fantastic for seeing exactly how the model responded!*

    *   **The JSON Files (`.json` files):**
        *   **What they are:** You'll also see files ending in `.json`. These contain all the same information as the HTML report, but in a structured data format called JSON.
        *   **Their purpose:** JSON files are mainly for computers or other scripts to read. For example, if you were doing advanced analysis or collecting many results, these files would be very useful.
        *   **For beginners:** You can largely ignore the `.json` files for now. If you do open one in a text editor, you'll see a lot of text with curly braces `{}` and quotes `""` – it's less visual than the HTML report.

*   **Finding Your Files:**
    Remember to check the console output from when you ran the script. It will tell you the exact names and locations of your HTML and JSON report files.

By opening and reviewing the HTML report, you'll get a clear understanding of how the model performed on the few questions you tested. This is the first step in learning how to interpret evaluation results!

## Exploring Further: What's Next?

Congratulations on running your first evaluation and looking at the results! Now that you've got the basics down, here are a few ways you can explore further:

### 1. Try a Different Language Model

*   **How:** Go back to the list of model identifiers you got from `python -m simple_evals.simple_evals --list-models` (Step 1). Pick a *different* model name from that list. Then, re-run the evaluation command from Step 2, but replace the previous model name with your new choice.
*   **Example:** If you first used `gpt-4o` and `claude-3-opus-20240229_empty` was also in your list, you could try:
    ```bash
    python -m simple_evals.simple_evals --model claude-3-opus-20240229_empty --eval mmlu --examples 5
    ```
*   **Why:** This lets you compare how different models perform on the same set of questions. (Remember to ensure you have the correct API key environment variable set for the new model's provider!)

### 2. Experiment with Different Benchmarks

*   **How:** Keep the model the same (or pick one you're interested in) and change the benchmark using the `--eval` parameter. You can find names of other available benchmarks by looking at the `*_eval.py` files in the repository (e.g., `math_eval.py` means you can try `--eval math`).
*   **Example:** If you used `mmlu` before, you could try the `math` benchmark:
    ```bash
    python -m simple_evals.simple_evals --model gpt-4o --eval math --examples 5
    ```
    Or, if you've done the specific setup for HumanEval (mentioned in Prerequisites of the original README), you could try:
    ```bash
    python -m simple_evals.simple_evals --model gpt-4o --eval humaneval --examples 5
    ```
*   **Why:** Different benchmarks test different skills (e.g., general knowledge, math, coding). This helps you see a model's strengths and weaknesses across various domains.

### 3. Gradually Increase the Number of Examples

*   **How:** Change the number after the `--examples` flag to something larger, like `--examples 20` or `--examples 100`. If you want to run the entire benchmark, you can remove the `--examples` flag altogether.
*   **Example (more examples):**
    ```bash
    python -m simple_evals.simple_evals --model gpt-4o --eval mmlu --examples 50
    ```
*   **Example (full benchmark run):**
    ```bash
    python -m simple_evals.simple_evals --model gpt-4o --eval mmlu
    ```
*   **⚠️ Important Warning:**
    *   **Time:** Running more examples, especially a full benchmark, will take **significantly longer** (from many minutes to potentially hours).
    *   **API Costs:** Using more examples means more API calls, which can lead to **higher costs** from the model providers (OpenAI, Anthropic, etc.). Be very mindful of this!
    *   It's a good idea to increase the number of examples gradually to get a sense of the time and cost involved before running a full benchmark.

### 4. Dive Deeper into the HTML Reports

*   **How:** For every evaluation you run, open the HTML report (as described in Step 3). Don't just look at the overall score!
*   **What to look for:**
    *   Read the actual questions and the model's full answers.
    *   Where did the model make mistakes? Were they understandable errors, or completely off?
    *   Does the model provide reasoning? Is it sound? (This is especially relevant for "chain-of-thought" prompting, which this repository often uses).
    *   Compare the responses from different models to the same questions.
*   **Why:** This is where you'll gain the most insight. Scores are numbers, but the actual responses show you *how* the model behaves, which is much more informative.

By trying these suggestions, you'll start to build a much richer understanding of how these AI models work and how they are evaluated. Happy exploring!

## Important Notes & Tips

As you continue your journey with language model evaluations, here are a few important points and helpful tips to keep in mind:

### 1. Be Mindful of API Costs

*   Many of the language models you'll evaluate are accessed via APIs from providers like OpenAI, Anthropic, etc. These providers often charge based on the amount of data you send and receive (i.e., the number of questions you ask and the length of the answers).
*   While running a few examples with the `--examples` flag is usually very cheap or covered by free tiers, running **full benchmarks** (without `--examples` or with a very high number) can lead to **significant API usage and potentially incur costs.**
*   Always be aware of the pricing models for the APIs you are using and monitor your usage on the provider's dashboard.

### 2. Specific Setup for the `humaneval` Benchmark

*   If you plan to run the `humaneval` benchmark (which tests Python code generation), it requires a one-time setup step because it uses code and data from a separate repository.
*   If you haven't done this already during the initial prerequisites, you'll need to:
    1.  Clone the `human-eval` repository from GitHub:
        ```bash
        git clone https://github.com/openai/human-eval
        ```
    2.  Navigate into the cloned directory and install it in "editable" mode:
        ```bash
        cd human-eval
        pip install -e .
        cd .. 
        ```
        (The `cd ..` command takes you back to your main `simple-evals` directory).
*   Without this setup, trying to run `--eval humaneval` will result in an error.

### 3. Saving Your Important Results

*   As you've seen, the detailed HTML and JSON reports are typically saved in a temporary directory (like `/tmp/`).
*   Files in temporary directories can sometimes be automatically deleted by your operating system (e.g., when you restart your computer).
*   If you run an evaluation that produces particularly interesting results or an HTML report you want to keep for longer, it's a good idea to **copy it from the `/tmp/` directory to a more permanent folder** on your computer (e.g., a "My Evaluations" folder in your Documents).
*   You can do this by using your computer's file explorer to drag and drop the files, or by using terminal commands like `cp` (on Linux/macOS) or `copy` (on Windows). For example, on Linux or macOS:
    ```bash
    # Example: cp /tmp/mmlu_gpt-4o_your_timestamp.html /path/to/your/permanent/folder/
    ```

We hope these tips help you have a smooth and insightful experience evaluating language models!
