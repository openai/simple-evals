from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class PromptFileConfig(Base):
    """Prompt 文件配置表"""
    __tablename__ = "prompt_file_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, nullable=False, index=True)  # 唯一标识
    name = Column(String, nullable=False)  # 显示名称
    description = Column(Text, nullable=True)  # 描述
    external_path = Column(String, nullable=False)  # 外置文件路径
    sort_order = Column(Integer, default=0)  # 排序
    is_active = Column(Boolean, default=True)  # 是否启用
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    version_files = relationship("PromptFile", back_populates="config")


class PromptVersion(Base):
    """Prompt 版本主表"""
    __tablename__ = "prompt_versions"
    
    id = Column(String, primary_key=True, index=True)  # UUID
    created_at = Column(DateTime, default=datetime.utcnow)
    author = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=False)  # 是否当前生效
    parent_version_id = Column(String, ForeignKey("prompt_versions.id"), nullable=True)
    
    # 关系
    files = relationship("PromptFile", back_populates="version", cascade="all, delete-orphan")
    evaluations = relationship("Evaluation", back_populates="version")
    parent = relationship("PromptVersion", remote_side=[id], backref="children")


class PromptFile(Base):
    """版本文件内容表"""
    __tablename__ = "prompt_files"
    
    id = Column(Integer, primary_key=True, index=True)
    version_id = Column(String, ForeignKey("prompt_versions.id"), nullable=False)
    config_key = Column(String, ForeignKey("prompt_file_configs.key"), nullable=False)
    content = Column(Text, nullable=False)  # Markdown 内容
    
    # 关系
    version = relationship("PromptVersion", back_populates="files")
    config = relationship("PromptFileConfig", back_populates="version_files")


class Evaluation(Base):
    """Eval 任务表"""
    __tablename__ = "evaluations"
    
    id = Column(String, primary_key=True, index=True)  # eval_20240224_171234_abc123
    version_id = Column(String, ForeignKey("prompt_versions.id"), nullable=False)
    benchmark = Column(String, nullable=False)  # healthbench / csedb / usmle
    num_examples = Column(Integer, nullable=True)  # None 表示全部
    n_threads = Column(Integer, default=1)
    status = Column(String, default="pending")  # pending / running / success / failed
    description = Column(Text, nullable=True)  # 用户备注
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # 结果
    result_summary = Column(JSON, nullable=True)  # {"overall_score": 0.78, ...}
    progress_data = Column(JSON, nullable=True)  # 实时进度数据
    error_message = Column(Text, nullable=True)
    
    # 运行时路径
    run_dir = Column(String, nullable=True)  # /tmp/eval_platform/runs/eval_xxx
    
    # 关系
    version = relationship("PromptVersion", back_populates="evaluations")
