from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import os
import json
import uuid

from app.core.database import get_db
from app.core.config import settings
from app.models.database import Evaluation, PromptVersion, PromptFile, PromptFileConfig
from app.models.schemas import (
    EvaluationCreate,
    EvaluationResponse,
    EvaluationListItem,
    EvaluationProgressResponse,
    MessageResponse
)

router = APIRouter()


def generate_eval_id() -> str:
    """生成 Eval ID: eval_20240224_171234_abc123"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    short_uuid = uuid.uuid4().hex[:8]
    return f"eval_{timestamp}_{short_uuid}"


@router.get("", response_model=List[EvaluationListItem])
def get_evaluations(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取 Eval 任务列表"""
    query = db.query(Evaluation)
    if status:
        query = query.filter(Evaluation.status == status)
    evaluations = query.order_by(Evaluation.created_at.desc()).offset(skip).limit(limit).all()
    return evaluations


@router.get("/{eval_id}", response_model=EvaluationResponse)
def get_evaluation(eval_id: str, db: Session = Depends(get_db)):
    """获取单个 Eval 任务详情"""
    evaluation = db.query(Evaluation).filter(Evaluation.id == eval_id).first()
    if not evaluation:
        raise HTTPException(status_code=404, detail="Eval 任务不存在")
    return evaluation


@router.post("", response_model=EvaluationResponse)
def create_evaluation(
    eval_data: EvaluationCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """创建新的 Eval 任务"""
    # 检查版本是否存在
    version = db.query(PromptVersion).filter(PromptVersion.id == eval_data.version_id).first()
    if not version:
        raise HTTPException(status_code=404, detail="Prompt 版本不存在")
    
    # 生成 Eval ID
    eval_id = generate_eval_id()
    
    # 创建运行目录
    run_dir = os.path.join(settings.EVAL_RUNS_DIR, eval_id)
    os.makedirs(run_dir, exist_ok=True)
    
    # 创建 prompts 子目录
    prompts_dir = os.path.join(run_dir, "prompts")
    os.makedirs(prompts_dir, exist_ok=True)
    
    # 从版本获取 prompt 内容并写入临时目录
    version_files = db.query(PromptFile).filter(PromptFile.version_id == eval_data.version_id).all()
    for vf in version_files:
        config = db.query(PromptFileConfig).filter(PromptFileConfig.key == vf.config_key).first()
        if config:
            # 使用配置的 key 作为文件名
            file_path = os.path.join(prompts_dir, f"{vf.config_key}.md")
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(vf.content)
    
    # 保存配置
    config_path = os.path.join(run_dir, "config.json")
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump({
            "eval_id": eval_id,
            "version_id": eval_data.version_id,
            "benchmark": eval_data.benchmark,
            "num_examples": eval_data.num_examples,
            "n_threads": eval_data.n_threads,
            "description": eval_data.description,
            "created_at": datetime.now().isoformat()
        }, f, indent=2, ensure_ascii=False)
    
    # 创建 Eval 记录
    db_eval = Evaluation(
        id=eval_id,
        version_id=eval_data.version_id,
        benchmark=eval_data.benchmark,
        num_examples=eval_data.num_examples,
        n_threads=eval_data.n_threads,
        description=eval_data.description,
        status="pending",
        run_dir=run_dir
    )
    db.add(db_eval)
    db.commit()
    db.refresh(db_eval)
    
    # TODO: 启动 Celery 任务
    # background_tasks.add_task(run_evaluation_task, eval_id)
    
    return db_eval


@router.post("/{eval_id}/start", response_model=MessageResponse)
def start_evaluation(eval_id: str, db: Session = Depends(get_db)):
    """启动 Eval 任务（从 pending 到 running）"""
    evaluation = db.query(Evaluation).filter(Evaluation.id == eval_id).first()
    if not evaluation:
        raise HTTPException(status_code=404, detail="Eval 任务不存在")
    
    if evaluation.status != "pending":
        raise HTTPException(status_code=400, detail=f"任务状态为 {evaluation.status}，无法启动")
    
    evaluation.status = "running"
    evaluation.started_at = datetime.now()
    db.commit()
    
    # TODO: 启动实际的 eval 运行逻辑
    
    return MessageResponse(message=f"Eval 任务 {eval_id} 已启动")


@router.get("/{eval_id}/progress", response_model=EvaluationProgressResponse)
def get_evaluation_progress(eval_id: str, db: Session = Depends(get_db)):
    """获取 Eval 任务实时进度"""
    evaluation = db.query(Evaluation).filter(Evaluation.id == eval_id).first()
    if not evaluation:
        raise HTTPException(status_code=404, detail="Eval 任务不存在")
    
    # 从 progress.json 读取实时数据
    progress_data = {
        "id": eval_id,
        "status": evaluation.status,
        "total": 0,
        "completed": 0,
        "current_score": None,
        "latest_samples": [],
        "metrics": None
    }
    
    if evaluation.run_dir:
        progress_path = os.path.join(evaluation.run_dir, "progress.json")
        if os.path.exists(progress_path):
            try:
                with open(progress_path, 'r', encoding='utf-8') as f:
                    file_data = json.load(f)
                    progress_data.update(file_data)
            except:
                pass
    
    # 合并数据库中的进度数据
    if evaluation.progress_data:
        progress_data.update(evaluation.progress_data)
    
    return EvaluationProgressResponse(**progress_data)


@router.post("/{eval_id}/cancel", response_model=MessageResponse)
def cancel_evaluation(eval_id: str, db: Session = Depends(get_db)):
    """取消 Eval 任务"""
    evaluation = db.query(Evaluation).filter(Evaluation.id == eval_id).first()
    if not evaluation:
        raise HTTPException(status_code=404, detail="Eval 任务不存在")
    
    if evaluation.status not in ["pending", "running"]:
        raise HTTPException(status_code=400, detail=f"任务状态为 {evaluation.status}，无法取消")
    
    evaluation.status = "failed"
    evaluation.error_message = "用户取消"
    evaluation.completed_at = datetime.now()
    db.commit()
    
    return MessageResponse(message=f"Eval 任务 {eval_id} 已取消")


@router.delete("/{eval_id}", response_model=MessageResponse)
def delete_evaluation(eval_id: str, db: Session = Depends(get_db)):
    """删除 Eval 任务"""
    evaluation = db.query(Evaluation).filter(Evaluation.id == eval_id).first()
    if not evaluation:
        raise HTTPException(status_code=404, detail="Eval 任务不存在")
    
    # 如果任务正在运行，先取消
    if evaluation.status == "running":
        raise HTTPException(status_code=400, detail="任务正在运行中，请先取消")
    
    # 删除运行目录
    if evaluation.run_dir and os.path.exists(evaluation.run_dir):
        import shutil
        shutil.rmtree(evaluation.run_dir)
    
    db.delete(evaluation)
    db.commit()
    
    return MessageResponse(message=f"Eval 任务 {eval_id} 已删除")


@router.get("/{eval_id}/result", response_model=dict)
def get_evaluation_result(eval_id: str, db: Session = Depends(get_db)):
    """获取 Eval 任务完整结果"""
    evaluation = db.query(Evaluation).filter(Evaluation.id == eval_id).first()
    if not evaluation:
        raise HTTPException(status_code=404, detail="Eval 任务不存在")
    
    if evaluation.status != "success":
        raise HTTPException(status_code=400, detail=f"任务状态为 {evaluation.status}，无结果")
    
    # 读取 result.json
    result_path = os.path.join(evaluation.run_dir, "result.json")
    if not os.path.exists(result_path):
        raise HTTPException(status_code=404, detail="结果文件不存在")
    
    with open(result_path, 'r', encoding='utf-8') as f:
        result = json.load(f)
    
    return result


# 内部函数：更新进度（供 Celery 任务调用）
def update_evaluation_progress(eval_id: str, progress_data: dict, db: Session = None):
    """更新 Eval 任务进度"""
    should_close = False
    if db is None:
        from app.core.database import SessionLocal
        db = SessionLocal()
        should_close = True
    
    try:
        evaluation = db.query(Evaluation).filter(Evaluation.id == eval_id).first()
        if evaluation:
            evaluation.progress_data = progress_data
            db.commit()
    finally:
        if should_close:
            db.close()


def complete_evaluation(eval_id: str, result_summary: dict, db: Session = None):
    """完成 Eval 任务"""
    should_close = False
    if db is None:
        from app.core.database import SessionLocal
        db = SessionLocal()
        should_close = True
    
    try:
        evaluation = db.query(Evaluation).filter(Evaluation.id == eval_id).first()
        if evaluation:
            evaluation.status = "success"
            evaluation.result_summary = result_summary
            evaluation.completed_at = datetime.now()
            db.commit()
    finally:
        if should_close:
            db.close()
