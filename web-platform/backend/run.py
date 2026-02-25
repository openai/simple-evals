#!/usr/bin/env python3
"""
FastAPI 应用启动脚本

使用方法:
    python run.py
    
或者使用 uvicorn 命令:
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
