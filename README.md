# 🏥 Wandou Benchmark

一个综合性的医疗 AI 模型评估平台，支持多种医疗基准测试（HealthBench、CSEDB、USMLE），并提供 Prompt 版本管理与 Web 可视化界面。

## 📁 项目结构

```
wandou-benchmark/
├── benchmarks/                    # 基准测试核心代码
│   ├── core/                      # 核心模块
│   │   ├── types.py               # 数据类型定义
│   │   └── common.py              # 通用工具函数
│   ├── samplers/                  # 模型采样器
│   │   ├── wandou_sampler.py      # Wandou 模型
│   │   ├── aliyun_sampler.py      # 阿里云 DashScope
│   │   ├── chat_completion_sampler.py  # OpenAI GPT
│   │   ├── claude_sampler.py      # Anthropic Claude
│   │   └── ...
│   ├── healthbench/               # HealthBench 医疗评估
│   │   ├── README.md              # HealthBench 使用手册
│   │   ├── evaluator.py           # 评估器
│   │   ├── meta_evaluator.py      # 元评估器
│   │   ├── runner.py              # 运行脚本
│   │   ├── data/                  # 数据集
│   │   └── results/               # 评估结果
│   ├── csedb/                     # CSEDB 评估（预留）
│   └── usmle/                     # USMLE 评估（预留）
├── web-platform/                  # Web 管理平台
│   ├── backend/                   # FastAPI 后端
│   │   ├── app/
│   │   │   ├── api/               # REST API
│   │   │   ├── models/            # 数据库模型
│   │   │   ├── services/          # 业务逻辑
│   │   │   └── main.py            # 应用入口
│   │   └── requirements.txt
│   └── frontend/                  # React + TypeScript 前端
│       ├── src/
│       └── package.json
├── data/                          # 数据目录
├── results/                       # 结果目录
├── prompts/                       # Prompt 模板
└── requirements.txt               # Python 依赖
```

## 🚀 快速开始

### 1. 环境准备

**Python 版本**: 3.12+

```bash
# 克隆项目
cd /Users/davidliu/Git/wandou_benchmark/simple-evals

# 创建虚拟环境
python3.12 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 运行 HealthBench 评估

```bash
# 运行完整评估
./venv/bin/python -m benchmarks.healthbench.runner

# 运行指定数量样本
./venv/bin/python -m benchmarks.healthbench.runner --examples 10

# 并行运行（多线程）
./venv/bin/python -m benchmarks.healthbench.runner --examples 10 --n-threads 4

# 高难度测试
./venv/bin/python -m benchmarks.healthbench.runner --eval-type healthbench_hard --examples 20

# 实时输出模式
./venv/bin/python -m benchmarks.healthbench.runner --interactive --examples 5
```

更多 HealthBench 用法请参考 [benchmarks/healthbench/README.md](benchmarks/healthbench/README.md)

### 3. 启动 Web 平台

#### 后端 (FastAPI)

```bash
cd web-platform/backend
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 启动服务
./venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

后端 API 文档: http://localhost:8000/docs

#### 前端 (React)

```bash
cd web-platform/frontend
npm install --legacy-peer-deps
npm run dev
```

前端页面: http://localhost:5173

#### 使用 Docker Compose（推荐）

```bash
cd web-platform
docker-compose up -d
```

## 🎯 功能特性

### 基准测试
- ✅ **HealthBench**: 医疗问答评估基准
  - 标准医疗评估
  - 高难度医疗问题
  - 专家共识评估
  - 元评估模式
- 🚧 **CSEDB**: 中文医疗对话评估（开发中）
- 🚧 **USMLE**: 美国医师执照考试评估（开发中）

### Web 平台
- 📋 **Prompt 版本管理**: 创建、查看、对比、激活 Prompt 版本
- 🔄 **版本对比**: 可视化 Diff 查看版本差异
- 📊 **Eval 任务**: 创建评估任务，支持多种 Benchmark
- 📈 **实时监控**: 查看运行进度、实时分数、问答流
- 🎨 **现代 UI**: React + Ant Design，支持深色模式

## 🛠️ 支持的模型

| 模型 | Sampler | 说明 |
|------|---------|------|
| Wandou | `wandou_sampler.py` | 豌豆医疗模型 |
| 阿里云 DashScope | `aliyun_sampler.py` | Qwen 系列模型 |
| OpenAI GPT | `chat_completion_sampler.py` | GPT-4/GPT-3.5 |
| Anthropic Claude | `claude_sampler.py` | Claude 系列 |
| OpenAI o1 | `o_chat_completion_sampler.py` | o1/o3 推理模型 |

## 📊 评估结果

评估结果保存在 `/tmp/evaluation_results/` 目录，格式：

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

## 🔧 开发指南

### 添加新的 Sampler

1. 在 `benchmarks/samplers/` 创建新的 sampler 文件
2. 继承 `SamplerBase` 类
3. 实现 `__call__` 方法

```python
from benchmarks.core.types import SamplerBase, SamplerResponse, MessageList

class MySampler(SamplerBase):
    def __call__(self, message_list: MessageList) -> SamplerResponse:
        # 实现模型调用逻辑
        return SamplerResponse(...)
```

### 添加新的 Benchmark

1. 在 `benchmarks/` 下创建新的目录（如 `mymbench/`）
2. 创建 `evaluator.py` 实现评估逻辑
3. 继承 `Eval` 类并实现 `__call__` 方法

```python
from benchmarks.core.types import Eval, EvalResult, SamplerBase

class MyBenchmark(Eval):
    def __call__(self, sampler: SamplerBase) -> EvalResult:
        # 实现评估逻辑
        return EvalResult(...)
```

## 📝 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `PROXY_SERVER_URL` | Wandou API 端点 | - |
| `PROXY_API_KEY` | Wandou API 密钥 | - |
| `DASHSCOPE_API_KEY` | 阿里云 DashScope API 密钥 | - |
| `OPENAI_API_KEY` | OpenAI API 密钥 | - |
| `ANTHROPIC_API_KEY` | Anthropic API 密钥 | - |

## 🤝 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📄 许可证

[MIT](LICENSE)

## 🙏 致谢

- [HealthBench](https://github.com/openai/simple-evals) - OpenAI 医疗评估基准
- [Simple-Evals](https://github.com/openai/simple-evals) - OpenAI 评估框架

---

<p align="center">Made with ❤️ by Wandou Team</p>
