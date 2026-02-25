
# 🎯 Wandou Benchmark 脚本使用手册

## 📋 脚本概述
`run_wandou_healthbench.py` 是一个用于运行 HealthBench 医疗评估基准测试的脚本，支持 Wandou 模型进行医疗问答评估。

## 🚀 基本用法

### 1. 激活虚拟环境
```bash
cd /Users/davidliu/Git/wandou_benchmark/simple-evals
source venv/bin/activate
```

### 2. 运行基本测试
```bash
# 运行所有测试
./venv/bin/python3 -m benchmarks.healthbench.runner

# 运行指定数量的测试
./venv/bin/python3 -m benchmarks.healthbench.runner --examples 10

# 并行运行测试
./venv/bin/python3 -m benchmarks.healthbench.runner --examples 10 --n-threads 4
```

## ⚙️ 命令行参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--model` | string | `wandou` | 模型名称 |
| `--eval-type` | string | `healthbench` | 评估类型：`healthbench`, `healthbench_hard`, `healthbench_consensus`, `healthbench_meta` |
| `--examples` | int | `None` | 测试数量（默认运行全部） |
| `--output-dir` | string | `/tmp` | 结果输出目录 |
| `--api-key` | string | `None` | Wandou API 密钥 |
| `--api-endpoint` | string | `None` | Wandou API 端点 |
| `--interactive` | flag | `False` | 显示实时输出 |
| `--n-threads` | int | `1` | 并行线程数 |

## 📊 评估类型说明

- **`healthbench`**: 标准医疗评估
- **`healthbench_hard`**: 高难度医疗问题
- **`healthbench_consensus`**: 专家共识医疗问题
- **`healthbench_meta`**: 元评估模式

## 💾 输出结果

测试结果保存在：`/tmp/evaluation_results/` 目录下，文件名格式：
```
healthbench_{model_name}_{eval_type}_{timestamp}.json
```

## 📈 输出示例

```json
{
  "overall_score": 0.459,
  "metrics": {
    "overall_score": 0.459,
    "theme:hedging": 0.573,
    "axis:accuracy": 0.359,
    "axis:completeness": 0.551
  }
}
```

## 🔧 高级用法

### 自定义 API 配置
```bash
./venv/bin/python3 -m benchmarks.healthbench.runner \
  --api-key "your-api-key" \
  --api-endpoint "https://your-api-endpoint.com"
```

### 实时输出模式
```bash
./venv/bin/python3 -m benchmarks.healthbench.runner --interactive --examples 5
```

### 高难度测试
```bash
./venv/bin/python3 -m benchmarks.healthbench.runner --eval-type healthbench_hard --examples 20
```

## ⚠️ 注意事项

1. **Python 版本**: 确保使用 Python 3.12.12
2. **虚拟环境**: 必须在激活的虚拟环境中运行
3. **依赖包**: 确保已安装所有依赖：`pip install -r requirements.txt`
4. **并行设置**: 根据系统性能调整 `--n-threads` 参数

## 🐛 常见问题

### Q: 出现 `ModuleNotFoundError: No module named 'jinja2'`
**A**: 使用完整路径运行：
```bash
./venv/bin/python3 -m benchmarks.healthbench.runner --examples 10
```

### Q: 如何查看测试结果？
**A**: 结果保存在 `/tmp/evaluation_results/` 目录，查看最新的 JSON 文件。

### Q: 如何调整并行度？
**A**: 使用 `--n-threads` 参数，例如：`--n-threads 8`

现在你可以开始使用 Wandou Benchmark 进行医疗评估测试了！🚀

## 语言

- 默认使用简体中文

