#!/usr/bin/env python3
"""
Simplified HealthBench evaluation script for wandou model with real-time output
"""
import argparse
import json
import os
from datetime import datetime
import pandas as pd
import time

from healthbench_eval import HealthBenchEval
from healthbench_meta_eval import HealthBenchMetaEval
from sampler.wandou_sampler import WandouSampler
from sampler.aliyun_sampler import AliyunSampler


def run_healthbench_for_wandou(
    model_name="wandou",
    eval_type="healthbench",  # healthbench, healthbench_hard, healthbench_consensus, healthbench_meta
    num_examples=None,
    output_dir="/tmp",
    custom_input_path=None,
    interactive=True  # 新增参数，用于控制是否显示实时输出
):
    """
    Run HealthBench evaluation for wandou model
    """
    print(f"Starting HealthBench evaluation for {model_name}")
    print(f"Evaluation type: {eval_type}")
    
    # Select the appropriate evaluator
    if eval_type == "healthbench_meta":
        evaluator = HealthBenchMetaEval(
            grader_model=WandouSampler(),  # or AliyunSampler() if using aliyun
            num_examples=num_examples
        )
    else:
        evaluator = HealthBenchEval(
            grader_model=WandouSampler(),  # or AliyunSampler() if using aliyun
            num_examples=num_examples,
            subset_name="hard" if eval_type == "healthbench_hard" 
                        else "consensus" if eval_type == "healthbench_consensus" 
                        else None,
            n_threads=1  # 使用单线程以获得更好的实时输出
        )
    
    # Run the evaluation with real-time output
    wandou_sampler = WandouSampler()
    
    # 如果是交互式模式，则手动实现带实时输出的评估
    if interactive and eval_type != "healthbench_meta":
        print("Running evaluation with real-time output...")
        
        # 获取示例数据
        examples = evaluator.examples
        if num_examples:
            examples = examples[:num_examples]
        
        results_list = []
        total_score = 0
        
        for idx, example in enumerate(examples):
            print(f"\n--- Test {idx + 1}/{len(examples)} ---")
            
            # 显示测试问题
            prompt_messages = example["prompt"]
            question_content = ""
            for msg in prompt_messages:
                if isinstance(msg["content"], str):
                    question_content = msg["content"]
                else:
                    # 如果内容是列表，提取文本部分
                    for item in msg["content"]:
                        if item.get("type") == "text":
                            question_content = item["text"]
                            break
            
            print(f"Question: {question_content[:200]}...")  # 只显示前200个字符
            
            # 显示评估标准（评分规则）
            rubrics = example["rubrics"]
            print(f"Evaluation criteria: {rubrics[0].criterion if rubrics else 'N/A'}")
            
            # 调用模型获取回答
            print("\nGetting model response...")
            start_time = time.time()
            sampler_response = wandou_sampler(prompt_messages)
            response_time = time.time() - start_time
            
            print(f"Model response (took {response_time:.2f}s):")
            print(f"Answer: {sampler_response.response_text[:300]}...")  # 只显示前300个字符
            
            # 使用评估器评估回答
            print("\nEvaluating response...")
            metrics, readable_explanation_str, rubric_items_with_grades = evaluator.grade_sample(
                prompt=prompt_messages,
                response_text=sampler_response.response_text,
                rubric_items=example["rubrics"],
                example_tags=example["example_tags"],
            )
            
            score = metrics["overall_score"]
            total_score += score
            print(f"Score: {score:.2f}")
            print(f"Evaluation details: {readable_explanation_str[:200]}...")
            
            # 保存结果
            results_list.append({
                "question": question_content,
                "answer": sampler_response.response_text,
                "score": score,
                "metrics": metrics,
                "evaluation_details": readable_explanation_str
            })
            
            print("-" * 50)
        
        # 计算总体结果
        avg_score = total_score / len(examples) if examples else 0
        results = {
            'score': avg_score,
            'metrics': {'average_score': avg_score, 'total_tests': len(examples)},
            'individual_results': results_list
        }
    else:
        # 原始批量处理方式
        results = evaluator(wandou_sampler)
    
    # Generate output filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_dir = os.path.join(output_dir, "evaluation_results")
    os.makedirs(results_dir, exist_ok=True)  # Ensure directory exists
    output_file = os.path.join(results_dir, f"healthbench_{model_name}_{eval_type}_{timestamp}.json")
    
    # Convert EvalResult to a JSON-serializable format if needed
    if hasattr(results, 'score'):
        results_dict = {
            'score': results.score,
            'metrics': results.metrics,
            'htmls': results.htmls,
            'convos': results.convos,
            'metadata': results.metadata
        }
    else:
        results_dict = results
    
    # Save results
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results_dict, f, indent=2, ensure_ascii=False)
    
    print(f"Evaluation completed. Results saved to: {output_file}")
    return results


def main():
    parser = argparse.ArgumentParser(description="Run HealthBench evaluation for wandou model")
    parser.add_argument("--model", type=str, default="wandou", help="Model name (default: wandou)")
    parser.add_argument("--eval-type", type=str, choices=["healthbench", "healthbench_hard", "healthbench_consensus", "healthbench_meta"], 
                       default="healthbench", help="Type of HealthBench evaluation")
    parser.add_argument("--examples", type=int, help="Number of examples to evaluate (default: all)")
    parser.add_argument("--output-dir", type=str, default="/tmp", help="Output directory for results")
    parser.add_argument("--api-key", type=str, help="API key for wandou model")
    parser.add_argument("--api-endpoint", type=str, help="API endpoint for wandou model")
    parser.add_argument("--interactive", action="store_true", help="Show real-time output during evaluation")
    
    args = parser.parse_args()
    
    # Set environment variables if provided
    if args.api_key:
        os.environ['PROXY_API_KEY'] = args.api_key
    if args.api_endpoint:
        os.environ['PROXY_SERVER_URL'] = args.api_endpoint
    
    # Run evaluation
    results = run_healthbench_for_wandou(
        model_name=args.model,
        eval_type=args.eval_type,
        num_examples=args.examples,
        output_dir=args.output_dir,
        interactive=args.interactive
    )
    
    print("Evaluation summary:")
    if isinstance(results, dict):
        print(json.dumps(results, indent=2))
    else:
        print(f"Average Score: {results.score}")
        print(f"Metrics: {results.metrics}")


if __name__ == "__main__":
    main()