from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = "Eval Platform"
    DEBUG: bool = True
    
    # 数据库配置
    DATABASE_URL: str = "sqlite:///./eval_platform.db"
    
    # Redis 配置（Celery 使用）
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # 文件存储路径
    DATA_DIR: str = "./data"
    PROMPT_VERSIONS_DIR: str = "./data/prompt_versions"
    EVAL_RUNS_DIR: str = "./data/eval_runs"
    
    # CORS 配置
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    class Config:
        env_file = ".env"


settings = Settings()

# 确保目录存在
os.makedirs(settings.PROMPT_VERSIONS_DIR, exist_ok=True)
os.makedirs(settings.EVAL_RUNS_DIR, exist_ok=True)
