# Eval Platform - Prompt 版本管理与评估系统

一个用于管理 Prompt 版本、运行 Eval 任务并实时监控的 Web 平台。

## 功能特性

- **Prompt 文件配置**: 动态配置多个 Prompt 文件路径
- **版本管理**: 创建、查看、对比、激活 Prompt 版本
- **Eval 任务**: 创建评估任务，支持多种 Benchmark
- **实时监控**: 查看运行进度、实时分数、问答流

## 快速开始

### 使用 Docker Compose（推荐）

```bash
# 克隆项目后进入目录
cd eval-web-platform

# 启动所有服务
docker-compose up -d

# 访问前端
open http://localhost:3000

# 后端 API 文档
open http://localhost:8000/docs
```

### 手动启动

#### 1. 启动 Redis
```bash
docker run -d -p 6379:6379 redis:7-alpine
```

#### 2. 启动后端
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python run.py
```

#### 3. 启动 Celery Worker
```bash
cd backend
source venv/bin/activate
celery -A app.core.celery_app worker --loglevel=info
```

#### 4. 启动前端
```bash
cd frontend
npm install
npm run dev
```

## 项目结构

```
eval-web-platform/
├── backend/                 # FastAPI 后端
│   ├── app/
│   │   ├── api/            # API 路由
│   │   ├── core/           # 核心配置
│   │   ├── models/         # 数据库模型
│   │   └── services/       # 业务逻辑
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/               # React 前端
│   ├── src/
│   │   ├── api/           # API 客户端
│   │   ├── pages/         # 页面组件
│   │   └── types/         # TypeScript 类型
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## 使用流程

1. **配置 Prompt 文件**: 在"Prompt 配置"页面添加需要管理的 Prompt 文件
2. **创建版本**: 在"版本管理"页面创建新的 Prompt 版本
3. **生效版本**: 点击"生效"将版本写入外置系统（另一个项目）
4. **创建 Eval**: 在"新建 Eval"页面选择版本和 Benchmark 创建任务
5. **运行任务**: 在"Eval 任务"页面启动任务并查看实时进度

## API 文档

启动后端后访问: http://localhost:8000/docs

## 开发说明

### 添加新的 Benchmark

在 `frontend/src/pages/NewEvalPage.tsx` 中的 `BENCHMARK_OPTIONS` 数组添加新选项。

### 修改数据库模型

修改 `backend/app/models/database.py` 后，重启服务会自动创建表。

## License

MIT
