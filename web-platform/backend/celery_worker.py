#!/usr/bin/env python3
"""
Celery Worker 启动脚本

使用方法:
    python celery_worker.py

或者使用 celery 命令:
    celery -A app.core.celery_app worker --loglevel=info
"""

import sys
sys.path.insert(0, '/Users/davidliu/Git/wandou_benchmark/simple-evals/eval-web-platform/backend')

from app.core.celery_app import celery_app

if __name__ == "__main__":
    # 使用 celery 命令行启动
    import subprocess
    subprocess.run([
        "celery",
        "-A", "app.core.celery_app",
        "worker",
        "--loglevel=info",
        "-Q", "eval_queue",  # 指定队列
        "-n", "eval_worker@%h"  # worker 名称
    ])
