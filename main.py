import argparse
from dataclasses import dataclass, asdict
from pathlib import Path
import pandas as pd

from models.mapping import MODEL_LOADING_MAP, get_model_server
from evals.mapping import EVAL_TASK_MAPPING, run_eval_from_name
from typings import EvalResult

@dataclass(frozen=True)
class EvalConfig:
    model_loader: str
    model: str
    eval_name: str
    num_examples: int
    k_shots: int
    output_dir: str

    def __post_init__(self) -> None:
        assert self.model_loader in MODEL_LOADING_MAP, f"Unknown {self.model_loader=} | Accepted values: {MODEL_LOADING_MAP.keys()}"
        assert self.eval_name in EVAL_TASK_MAPPING, f"Unknown {self.eval_name=} | Accepted values: {EVAL_TASK_MAPPING.keys()}"

        model_loader_models = MODEL_LOADING_MAP[self.model_loader]
        assert self.model in model_loader_models, f"Unknown {self.model=} | Accepted values: {model_loader_models.keys()}"

        if not Path(self.output_dir).exists():
            logger.warn(f"Output directory {self.output_dir} does not exist. Creating it...")
            Path(self.output_dir).mkdir(parents=True)

def run_eval(eval_config: EvalConfig) -> None:
    server = get_model_server(eval_config.model_loader, eval_config.model)
    print(f"Using server: {server}")
    eval_result: EvalResult = run_eval_from_name(
        eval_name=eval_config.eval_name,
        server=server,
        num_examples=eval_config.num_examples,
        k_shots=eval_config.k_shots
    )

    file_slug = f"{eval_config.eval_name}_{eval_config.model}_fs{eval_config.k_shots}_{eval_config.num_examples}"
    # First, save out a summary of the score and metrics
    summary_out_path = Path(eval_config.output_dir) / f"{file_slug}_summary.txt"
    print(f"Saving evaluation summary to {summary_out_path}")
    with open(summary_out_path, "w") as f:
        f.write(f"Score: {eval_result.score}\n")
        for metric, value in eval_result.metrics.items():
            f.write(f"{metric}: {value}\n")

    # Next, save out the conversations
    csv_out_path = Path(eval_config.output_dir) / f"{file_slug}_conversations.csv"
    print(f"Saving evaluation results to {csv_out_path}")
    eval_result_conversations: List[List[str]] = eval_result.convos
    eval_df = pd.DataFrame(eval_result_conversations)
    eval_df.to_csv(csv_out_path, index=False)

def main() -> None:
    parser = argparse.ArgumentParser(description="Run evaluation")
    
    parser.add_argument("--model_loader", type=str, choices=["openai", "anthropic"], required=True)
    parser.add_argument("--model", type=str, required=True)

    parser.add_argument("--eval_name", type=str, choices=["mmlu"])
    parser.add_argument("--num_examples", type=int, default=1000)
    parser.add_argument("--k_shots", type=int, default=5)

    parser.add_argument("--output_dir", type=str, default="output")

    args = parser.parse_args()
    eval_config = EvalConfig(
        model_loader=args.model_loader,
        model=args.model,
        eval_name=args.eval_name,
        num_examples=args.num_examples,
        k_shots=args.k_shots,
        output_dir=args.output_dir
    )
    print(f"Running evaluation with {eval_config=}")
    run_eval(eval_config)

if __name__ == "__main__":
    main()