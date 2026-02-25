from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
import os
from pydantic import BaseModel
from app.core.database import get_db
from app.models.database import PromptFileConfig
from app.models.schemas import (
    PromptFileConfigCreate,
    PromptFileConfigUpdate,
    PromptFileConfigResponse,
    MessageResponse
)
import uuid


class TestPathRequest(BaseModel):
    path: str


class TestPathResponse(BaseModel):
    readable: bool
    content: Optional[str] = None
    error: Optional[str] = None

router = APIRouter()


@router.get("", response_model=List[PromptFileConfigResponse])
def get_configs(db: Session = Depends(get_db)):
    """获取所有 Prompt 文件配置"""
    configs = db.query(PromptFileConfig).order_by(PromptFileConfig.sort_order).all()
    return configs


@router.post("", response_model=PromptFileConfigResponse)
def create_config(config: PromptFileConfigCreate, db: Session = Depends(get_db)):
    """创建新的 Prompt 文件配置"""
    # 检查 key 是否已存在
    existing = db.query(PromptFileConfig).filter(PromptFileConfig.key == config.key).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Key '{config.key}' 已存在")
    
    # 自动设置排序
    if config.sort_order == 0:
        max_order = db.query(PromptFileConfig).count()
        config.sort_order = max_order + 1
    
    db_config = PromptFileConfig(**config.model_dump())
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    
    # 自动创建版本1，读取外置文件内容
    try:
        from app.models.database import PromptVersion, PromptFile
        from datetime import datetime
        import os
        
        # 读取外置文件内容
        file_content = ""
        if os.path.exists(config.external_path):
            try:
                with open(config.external_path, 'r', encoding='utf-8') as f:
                    file_content = f.read()
            except Exception as e:
                file_content = f"# {config.name}\n\n[读取文件失败: {str(e)}]"
        else:
            file_content = f"# {config.name}\n\n[文件不存在: {config.external_path}]"
        
        # 创建初始版本
        version_id = str(uuid.uuid4())
        version = PromptVersion(
            id=version_id,
            author="system",
            description="初始版本（创建配置时自动生成）",
            is_active=True
        )
        db.add(version)
        
        # 创建版本文件
        version_file = PromptFile(
            version_id=version_id,
            config_key=config.key,
            content=file_content
        )
        db.add(version_file)
        db.commit()
    except Exception as e:
        # 版本创建失败不影响配置创建
        print(f"自动创建版本1失败: {str(e)}")
    
    return db_config


@router.get("/{config_key}", response_model=PromptFileConfigResponse)
def get_config(config_key: str, db: Session = Depends(get_db)):
    """获取单个 Prompt 文件配置"""
    config = db.query(PromptFileConfig).filter(PromptFileConfig.key == config_key).first()
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    return config


@router.put("/{config_key}", response_model=PromptFileConfigResponse)
def update_config(config_key: str, config_update: PromptFileConfigUpdate, db: Session = Depends(get_db)):
    """更新 Prompt 文件配置"""
    config = db.query(PromptFileConfig).filter(PromptFileConfig.key == config_key).first()
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    
    # 更新字段
    update_data = config_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(config, field, value)
    
    db.commit()
    db.refresh(config)
    return config


@router.delete("/{config_key}", response_model=MessageResponse)
def delete_config(config_key: str, force: bool = False, db: Session = Depends(get_db)):
    """删除 Prompt 文件配置
    
    Args:
        config_key: 配置标识
        force: 是否强制删除，如果为 true 则连带删除所有关联版本
    """
    config = db.query(PromptFileConfig).filter(PromptFileConfig.key == config_key).first()
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    
    # 检查是否有版本引用此配置
    from app.models.database import PromptFile, PromptVersion
    referencing_files = db.query(PromptFile).filter(PromptFile.config_key == config_key).all()
    
    if referencing_files and not force:
        # 返回引用数量，让前端提示用户
        raise HTTPException(
            status_code=409,  # Conflict
            detail=f"该 Prompt 已被 {len(referencing_files)} 个版本引用，删除后将同时删除这些版本。如需继续，请确认强制删除。"
        )
    
    if referencing_files and force:
        # 强制删除：先删除关联的版本文件和版本
        version_ids = set(f.version_id for f in referencing_files)
        
        # 删除版本文件记录
        for file in referencing_files:
            db.delete(file)
        
        # 删除版本（级联删除其他关联文件）
        for version_id in version_ids:
            version = db.query(PromptVersion).filter(PromptVersion.id == version_id).first()
            if version:
                db.delete(version)
    
    db.delete(config)
    db.commit()
    
    if referencing_files and force:
        return MessageResponse(message=f"配置 '{config_key}' 及其 {len(referencing_files)} 个关联版本已删除")
    return MessageResponse(message=f"配置 '{config_key}' 已删除")


@router.post("/reorder", response_model=MessageResponse)
def reorder_configs(config_keys: List[str], db: Session = Depends(get_db)):
    """调整配置排序"""
    for index, key in enumerate(config_keys):
        config = db.query(PromptFileConfig).filter(PromptFileConfig.key == key).first()
        if config:
            config.sort_order = index + 1
    
    db.commit()
    return MessageResponse(message="排序已更新")


@router.post("/test-path", response_model=TestPathResponse)
def test_path(request: TestPathRequest):
    """测试文件路径是否可读"""
    try:
        if not os.path.exists(request.path):
            return TestPathResponse(readable=False, error="文件不存在")
        
        if not os.path.isfile(request.path):
            return TestPathResponse(readable=False, error="路径不是文件")
        
        with open(request.path, 'r', encoding='utf-8') as f:
            content = f.read()
            return TestPathResponse(readable=True, content=content)
    
    except PermissionError:
        return TestPathResponse(readable=False, error="没有权限读取文件")
    except Exception as e:
        return TestPathResponse(readable=False, error=f"读取失败: {str(e)}")
