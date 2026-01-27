# 使用阿里云模型和自定义wandou模型运行HealthBench

## 设置环境变量

```bash
# 设置阿里云API信息
export PROXY_SERVER_URL="https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
export PROXY_API_KEY="sk-f1e6e0a228224a1792d71a83bbb9e4cf"

# 设置你的wandou模型API信息
export WANDOU_API_ENDPOINT="你的wandou模型API端点URL"
export WANDOU_API_KEY="你的wandou模型API密钥"
```

## 使用阿里云模型作为评分模型

如果你想使用阿里云的Qwen模型作为HealthBench的评分模型（替代默认的GPT-4.1）：

```bash
# 设置使用阿里云作为评分模型
export USE_ALIYUN_GRADER=true
export ALIYUN_GRADING_MODEL=qwen-plus  # 或 qwen-max

# 运行HealthBench评估，使用wandou模型作为被评估模型
python -m simple_evals.simple_evals --eval=healthbench --model=wandou
```

## 直接使用阿里云模型进行评估

如果你想直接评估阿里云的模型：

```bash
# 不设置USE_ALIYUN_GRADER，使用默认GPT-4.1作为评分模型
unset USE_ALIYUN_GRADER

# 评估阿里云的qwen-plus模型
python -m simple_evals.simple_evals --eval=healthbench --model=aliyun-qwen-plus
```

## 查看所有可用模型

```bash
python -m simple_evals.simple_evals --list-models
```

## 注意事项

1. 修改 `wandou_sampler.py` 中的API调用逻辑以匹配你的实际API格式
2. 根据你的wandou模型API响应格式调整内容提取逻辑
3. 确保API密钥安全，不要提交到版本控制系统