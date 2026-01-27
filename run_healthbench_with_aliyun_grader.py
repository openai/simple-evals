#!/usr/bin/env python3
"""
Custom script to run HealthBench evaluation with custom grader model (Aliyun model)
"""

import os
from simple_evals.healthbench_eval import HealthBenchEval
from simple_evals.sampler.aliyun_sampler import AliyunSampler
from simple_evals import common


def run_healthbench_with_aliyun_grader():
    # Initialize the Aliyun grader model
    aliyun_grader = AliyunSampler(
        model="qwen-plus",  # You can change this to any model you want to use
        api_key=os.environ.get("PROXY_API_KEY"),
        temperature=0.0,  # Lower temperature for more consistent grading
        max_tokens=2048,
    )
    
    # Initialize the HealthBench evaluator with your custom grader
    evaluator = HealthBenchEval(
        grader_model=aliyun_grader,
        num_examples=5,  # Set to small number for testing, remove for full eval
        n_repeats=1,
        n_threads=1,  # Reduce threads for testing
    )
    
    # Create a dummy sampler or use your own model sampler
    # For this example, I'll use a dummy sampler to test the grading functionality
    from simple_evals.types import SamplerBase, SamplerResponse
    
    class DummySampler(SamplerBase):
        def __call__(self, message_list):
            # Return a dummy response for testing purposes
            # In practice, you'd replace this with your wandou model sampler
            return SamplerResponse(
                response_text="This is a dummy response for testing grading.",
                actual_queried_message_list=message_list,
                response_metadata={}
            )
    
    dummy_sampler = DummySampler()
    
    # Run the evaluation
    result = evaluator(dummy_sampler)
    
    # Print the results
    print("Evaluation completed!")
    print(f"Overall Score: {result.score}")
    print(f"Metrics: {result.metrics}")
    
    # Save the report
    import datetime
    now = datetime.datetime.now()
    date_str = now.strftime("%Y%m%d_%H%M%S")
    
    report_filename = f"/tmp/healthbench_aliyun_grader_{date_str}.html"
    with open(report_filename, "w") as fh:
        fh.write(common.make_report(result))
    
    print(f"Report saved to {report_filename}")
    
    return result


if __name__ == "__main__":
    # Set your environment variables
    os.environ["PROXY_SERVER_URL"] = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
    os.environ["PROXY_API_KEY"] = "sk-f1e6e0a228224a1792d71a83bbb9e4cf"
    
    result = run_healthbench_with_aliyun_grader()