from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import os
import shutil
import uuid

from app.core.database import get_db
from app.core.config import settings
from app.models.database import PromptVersion, PromptFile, PromptFileConfig
from app.models.schemas import (
    PromptVersionCreate,
    PromptVersionResponse,
    PromptVersionListItem,
    PromptFileContent,
    MessageResponse,
    VersionDiffResponse
)

router = APIRouter()


def generate_version_id() -> str:
    """生成版本 ID: UUID"""
    return str(uuid.uuid4())


@router.get("", response_model=List[PromptVersionListItem])
def get_versions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取所有 Prompt 版本列表（按创建时间倒序）"""
    versions = db.query(PromptVersion).order_by(PromptVersion.created_at.desc()).offset(skip).limit(limit).all()
    return versions


@router.get("/active", response_model=Optional[PromptVersionResponse])
def get_active_version(db: Session = Depends(get_db)):
    """获取当前生效的版本"""
    version = db.query(PromptVersion).filter(PromptVersion.is_active == True).first()
    if not version:
        return None
    return version


@router.post("", response_model=PromptVersionResponse)
def create_version(version_data: PromptVersionCreate, db: Session = Depends(get_db)):
    """创建新的 Prompt 版本"""
    # 生成 UUID 作为版本 ID
    version_id = generate_version_id()
    
    # 创建版本记录
    db_version = PromptVersion(
        id=version_id,
        author=version_data.author,
        description=version_data.description,
        parent_version_id=version_data.parent_version_id,
        is_active=False
    )
    db.add(db_version)
    
    # 创建文件记录
    for file_data in version_data.files:
        db_file = PromptFile(
            version_id=version_id,
            config_key=file_data.config_key,
            content=file_data.content
        )
        db.add(db_file)
    
    db.commit()
    db.refresh(db_version)
    
    # 保存到文件系统（备份）
    version_dir = os.path.join(settings.PROMPT_VERSIONS_DIR, version_id)
    os.makedirs(version_dir, exist_ok=True)
    for file_data in version_data.files:
        config = db.query(PromptFileConfig).filter(PromptFileConfig.key == file_data.config_key).first()
        if config:
            file_path = os.path.join(version_dir, f"{file_data.config_key}.md")
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(file_data.content)
    
    return db_version


@router.get("/{version_id}", response_model=PromptVersionResponse)
def get_version(version_id: str, db: Session = Depends(get_db)):
    """获取单个版本详情"""
    version = db.query(PromptVersion).filter(PromptVersion.id == version_id).first()
    if not version:
        raise HTTPException(status_code=404, detail="版本不存在")
    return version


@router.post("/{version_id}/activate", response_model=MessageResponse)
def activate_version(version_id: str, db: Session = Depends(get_db)):
    """激活指定版本（写入外置文件系统）"""
    version = db.query(PromptVersion).filter(PromptVersion.id == version_id).first()
    if not version:
        raise HTTPException(status_code=404, detail="版本不存在")
    
    # 获取所有启用的配置
    configs = db.query(PromptFileConfig).filter(PromptFileConfig.is_active == True).all()
    config_map = {c.key: c for c in configs}
    
    # 获取版本的文件内容
    version_files = db.query(PromptFile).filter(PromptFile.version_id == version_id).all()
    
    # 写入外置文件系统
    errors = []
    for vf in version_files:
        config = config_map.get(vf.config_key)
        if config:
            try:
                # 确保目录存在
                os.makedirs(os.path.dirname(config.external_path), exist_ok=True)
                # 写入文件
                with open(config.external_path, 'w', encoding='utf-8') as f:
                    f.write(vf.content)
            except Exception as e:
                errors.append(f"{vf.config_key}: {str(e)}")
    
    if errors:
        raise HTTPException(status_code=500, detail=f"写入文件失败: {'; '.join(errors)}")
    
    # 更新激活状态
    db.query(PromptVersion).update({PromptVersion.is_active: False})
    version.is_active = True
    db.commit()
    
    return MessageResponse(
        message=f"版本 {version_id} 已激活并写入外置系统。注意：另一个项目需要重启才能使用新版本。"
    )


@router.get("/{version_id}/diff/{other_version_id}", response_model=VersionDiffResponse)
def compare_versions(version_id: str, other_version_id: str, db: Session = Depends(get_db)):
    """对比两个版本的差异"""
    v1 = db.query(PromptVersion).filter(PromptVersion.id == version_id).first()
    v2 = db.query(PromptVersion).filter(PromptVersion.id == other_version_id).first()
    
    if not v1 or not v2:
        raise HTTPException(status_code=404, detail="版本不存在")
    
    # 获取文件内容
    v1_files = {f.config_key: f.content for f in v1.files}
    v2_files = {f.config_key: f.content for f in v2.files}
    
    # 计算差异
    all_keys = set(v1_files.keys()) | set(v2_files.keys())
    diffs = {}
    for key in all_keys:
        old_content = v1_files.get(key, "")
        new_content = v2_files.get(key, "")
        if old_content != new_content:
            diffs[key] = {
                "old": old_content,
                "new": new_content
            }
    
    return VersionDiffResponse(
        version1_id=version_id,
        version2_id=other_version_id,
        diffs=diffs
    )


@router.delete("/{version_id}", response_model=MessageResponse)
def delete_version(version_id: str, db: Session = Depends(get_db)):
    """删除版本（不能删除当前激活版本）"""
    version = db.query(PromptVersion).filter(PromptVersion.id == version_id).first()
    if not version:
        raise HTTPException(status_code=404, detail="版本不存在")
    
    if version.is_active:
        raise HTTPException(status_code=400, detail="不能删除当前激活的版本")
    
    # 删除文件系统备份
    version_dir = os.path.join(settings.PROMPT_VERSIONS_DIR, version_id)
    if os.path.exists(version_dir):
        shutil.rmtree(version_dir)
    
    db.delete(version)
    db.commit()
    
    return MessageResponse(message=f"版本 {version_id} 已删除")


@router.post("/import-from-external", response_model=PromptVersionResponse)
def import_from_external(author: str, description: Optional[str] = None, db: Session = Depends(get_db)):
    """从外置文件系统导入当前内容作为新版本"""
    configs = db.query(PromptFileConfig).filter(PromptFileConfig.is_active == True).all()
    
    files = []
    for config in configs:
        try:
            if os.path.exists(config.external_path):
                with open(config.external_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            else:
                content = f"# {config.name}\n\n[文件不存在: {config.external_path}]"
        except Exception as e:
            content = f"# {config.name}\n\n[读取失败: {str(e)}]"
        
        files.append(PromptFileContent(config_key=config.key, content=content))
    
    version_data = PromptVersionCreate(
        author=author,
        description=description or "从外置系统导入",
        files=files
    )
    
    return create_version(version_data, db)


# ========== Prompt 专用接口（新设计）==========

from pydantic import BaseModel


class PromptVersionSimple(BaseModel):
    """简化版本信息（用于列表）"""
    id: str
    version_number: int = 0  # 前端动态计算
    is_active: bool
    created_at: datetime
    author: str
    description: Optional[str] = None


class PromptVersionsResponse(BaseModel):
    """Prompt 版本列表响应"""
    config_key: str
    config_name: str
    active_version_id: Optional[str]
    versions: List[PromptVersionSimple]


class CreatePromptVersionRequest(BaseModel):
    """创建 Prompt 版本请求"""
    author: str
    content: str
    description: Optional[str] = None


@router.get("/prompt/{config_key}", response_model=PromptVersionsResponse)
def get_prompt_versions(config_key: str, db: Session = Depends(get_db)):
    """获取指定 Prompt 的所有版本（简化版）"""
    # 检查配置是否存在
    config = db.query(PromptFileConfig).filter(PromptFileConfig.key == config_key).first()
    if not config:
        raise HTTPException(status_code=404, detail="Prompt 配置不存在")
    
    # 查询该 Prompt 的所有版本
    # 通过 PromptFile 关联查询
    version_files = db.query(PromptFile).filter(
        PromptFile.config_key == config_key
    ).all()
    
    version_ids = [vf.version_id for vf in version_files]
    
    if not version_ids:
        return PromptVersionsResponse(
            config_key=config_key,
            config_name=config.name,
            active_version_id=None,
            versions=[]
        )
    
    # 获取版本详情（按创建时间倒序）
    versions = db.query(PromptVersion).filter(
        PromptVersion.id.in_(version_ids)
    ).order_by(PromptVersion.created_at.desc()).all()
    
    # 找到当前生效的版本
    active_version = db.query(PromptVersion).filter(
        PromptVersion.id.in_(version_ids),
        PromptVersion.is_active == True
    ).first()
    
    return PromptVersionsResponse(
        config_key=config_key,
        config_name=config.name,
        active_version_id=active_version.id if active_version else None,
        versions=[
            PromptVersionSimple(
                id=v.id,
                version_number=0,  # 前端动态计算
                is_active=v.is_active,
                created_at=v.created_at,
                author=v.author,
                description=v.description
            )
            for v in versions
        ]
    )


@router.get("/prompt/{config_key}/content/{version_id}")
def get_prompt_version_content(config_key: str, version_id: str, db: Session = Depends(get_db)):
    """获取指定 Prompt 版本的完整内容"""
    # 验证配置存在
    config = db.query(PromptFileConfig).filter(PromptFileConfig.key == config_key).first()
    if not config:
        raise HTTPException(status_code=404, detail="Prompt 配置不存在")
    
    # 获取版本文件内容
    version_file = db.query(PromptFile).filter(
        PromptFile.version_id == version_id,
        PromptFile.config_key == config_key
    ).first()
    
    if not version_file:
        raise HTTPException(status_code=404, detail="版本不存在")
    
    return {
        "id": version_id,
        "config_key": config_key,
        "content": version_file.content
    }


@router.post("/prompt/{config_key}", response_model=PromptVersionResponse)
def create_prompt_version(
    config_key: str,
    request: CreatePromptVersionRequest,
    db: Session = Depends(get_db)
):
    """为指定 Prompt 创建新版本"""
    from sqlalchemy.orm import joinedload
    
    # 验证配置存在
    config = db.query(PromptFileConfig).filter(PromptFileConfig.key == config_key).first()
    if not config:
        raise HTTPException(status_code=404, detail="Prompt 配置不存在")
    
    # 生成 UUID 作为版本 ID
    version_id = generate_version_id()
    
    # 创建版本记录
    db_version = PromptVersion(
        id=version_id,
        author=request.author,
        description=request.description,
        is_active=False
    )
    db.add(db_version)
    
    # 创建文件记录
    db_file = PromptFile(
        version_id=version_id,
        config_key=config_key,
        content=request.content
    )
    db.add(db_file)
    
    db.commit()
    
    # 重新查询以加载 files 关系
    db_version = db.query(PromptVersion).options(joinedload(PromptVersion.files)).filter(PromptVersion.id == version_id).first()
    
    # 保存到文件系统（备份）
    version_dir = os.path.join(settings.PROMPT_VERSIONS_DIR, version_id)
    os.makedirs(version_dir, exist_ok=True)
    file_path = os.path.join(version_dir, f"{config_key}.md")
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(request.content)
    
    return db_version


@router.post("/prompt/{config_key}/activate/{version_id}", response_model=MessageResponse)
def activate_prompt_version(config_key: str, version_id: str, db: Session = Depends(get_db)):
    """激活指定 Prompt 的指定版本"""
    # 验证配置存在
    config = db.query(PromptFileConfig).filter(PromptFileConfig.key == config_key).first()
    if not config:
        raise HTTPException(status_code=404, detail="Prompt 配置不存在")
    
    # 获取版本
    version = db.query(PromptVersion).filter(PromptVersion.id == version_id).first()
    if not version:
        raise HTTPException(status_code=404, detail="版本不存在")
    
    # 获取该版本的文件内容
    version_file = db.query(PromptFile).filter(
        PromptFile.version_id == version_id,
        PromptFile.config_key == config_key
    ).first()
    
    if not version_file:
        raise HTTPException(status_code=404, detail="版本内容不存在")
    
    # 写入外置文件系统
    try:
        os.makedirs(os.path.dirname(config.external_path), exist_ok=True)
        with open(config.external_path, 'w', encoding='utf-8') as f:
            f.write(version_file.content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"写入文件失败: {str(e)}")
    
    # 更新激活状态（只更新该 Prompt 相关的版本）
    # 先取消该 Prompt 其他版本的激活状态
    db.query(PromptVersion).filter(
        PromptVersion.id.in_(
            db.query(PromptFile.version_id).filter(PromptFile.config_key == config_key)
        )
    ).update({PromptVersion.is_active: False}, synchronize_session=False)
    
    # 激活当前版本
    version.is_active = True
    db.commit()
    
    return MessageResponse(
        message=f"Prompt '{config.name}' 的版本已生效。"
    )


class UpdateContentRequest(BaseModel):
    """更新版本内容请求"""
    content: str


@router.put("/prompt/{config_key}/content/{version_id}", response_model=MessageResponse)
def update_prompt_version_content(
    config_key: str,
    version_id: str,
    request: UpdateContentRequest,
    db: Session = Depends(get_db)
):
    """更新指定 Prompt 版本的内容（用于同步外部文件）"""
    # 验证配置存在
    config = db.query(PromptFileConfig).filter(PromptFileConfig.key == config_key).first()
    if not config:
        raise HTTPException(status_code=404, detail="Prompt 配置不存在")
    
    # 获取版本文件
    version_file = db.query(PromptFile).filter(
        PromptFile.version_id == version_id,
        PromptFile.config_key == config_key
    ).first()
    
    if not version_file:
        raise HTTPException(status_code=404, detail="版本不存在")
    
    # 更新内容
    version_file.content = request.content
    db.commit()
    
    # 同时更新文件系统备份
    try:
        version_dir = os.path.join(settings.PROMPT_VERSIONS_DIR, version_id)
        if os.path.exists(version_dir):
            file_path = os.path.join(version_dir, f"{config_key}.md")
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(request.content)
    except Exception as e:
        print(f"更新文件系统备份失败: {str(e)}")
    
    return MessageResponse(message="版本内容已更新")
