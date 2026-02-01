# Wandou HealthBench Evaluation

这是一个精简版的HealthBench评估工具，专门用于测试wandou模型。

## 安装依赖

```bash
pip install -r requirements.txt
```

## 运行评估

```bash
# 基本运行
python run_wandou_healthbench.py --model wandou

# 指定评估类型
python run_wandou_healthbench.py --model wandou --eval-type healthbench_hard

# 限制示例数量进行快速测试
python run_wandou_healthbench.py --model wandou --examples 5

# 指定API密钥和端点
python run_wandou_healthbench.py --model wandou --api-key YOUR_API_KEY --api-endpoint YOUR_API_ENDPOINT
```

## 配置环境变量

您也可以通过环境变量配置API信息：

```bash
export WANDOU_API_KEY="your_api_key"
export WANDOU_API_ENDPOINT="your_api_endpoint"
```

## 支持的评估类型

- `healthbench`: 标准HealthBench评估
- `healthbench_hard`: 更具挑战性的HealthBench评估
- `healthbench_consensus`: 基于共识的HealthBench评估
- `healthbench_meta`: 元评估（评估评估器本身）

## 输出

评估结果将保存为JSON文件，默认位置在 `/tmp` 目录下。