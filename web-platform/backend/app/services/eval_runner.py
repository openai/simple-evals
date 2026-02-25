import os
import sys
import json
import subprocess
from datetime import datetime
from typing import Optional
from celery import shared_task

# 添加 simple-evals 到路径
sys.path.insert(0, '/Users/davidliu/Git/wandou_benchmark/simple-evals')

from app.core.config import settings
from app.api.evaluations import update_evaluation_progress, complete_evaluation


@shared_task(bind=True, max_retries=3)
def run_evaluation_task(self, eval_id: str):
    """
    运行 Eval 任务的 Celery 任务
    
    这个任务会：
    1. 读取 Eval 配置
    2. 调用现有的 eval 脚本
    3. 实时更新进度到 progress.json
    4. 完成后更新数据库状态
    """
    try:
        run_dir = os.path.join(settings.EVAL_RUNS_DIR, eval_id)
        config_path = os.path.join(run_dir, "config.json")
        
        # 读取配置
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 初始化进度文件
        progress = {
            "total": config.get("num_examples", 100),
            "completed": 0,
            "current_score": None,
            "latest_samples": [],
            "metrics": {},
            "status": "running"
        }
        
        progress_path = os.path.join(run_dir, "progress.json")
        with open(progress_path, 'w', encoding='utf-8') as f:
            json.dump(progress, f, indent=2)
        
        # TODO: 这里集成实际的 eval 运行逻辑
        # 目前使用模拟数据演示
        
        # 模拟运行过程
        import time
        total = progress["total"]
        
        for i in range(total):
            # 模拟处理每个样本
            time.sleep(0.5)  # 实际运行时会替换为真实逻辑
            
            # 更新进度
            progress["completed"] = i + 1
            progress["current_score"] = 0.4 + (i / total) * 0.4  # 模拟分数增长
            
            # 添加最新样本（只保留最近5个）
            progress["latest_samples"].append({
                "index": i + 1,
                "question": f"问题 {i+1}: 患者症状描述...",
                "answer": f"回答 {i+1}: 建议进行...",
                "score": 0.7 + (i % 3) * 0.1,
                "timestamp": datetime.now().isoformat()
            })
            progress["latest_samples"] = progress["latest_samples"][-5:]
            
            # 写入进度文件
            with open(progress_path, 'w', encoding='utf-8') as f:
                json.dump(progress, f, indent=2)
            
            # 更新数据库（每10个样本更新一次，减少数据库压力）
            if (i + 1) % 10 == 0:
                update_evaluation_progress(eval_id, progress)
        
        # 运行完成
        progress["status"] = "success"
        with open(progress_path, 'w', encoding='utf-8') as f:
            json.dump(progress, f, indent=2)
        
        # 生成结果摘要
        result_summary = {
            "overall_score": progress["current_score"],
            "total_samples": total,
            "completed_samples": total,
            "metrics": {
                "accuracy": 0.75,
                "completeness": 0.82,
                "hedging": 0.68
            }
        }
        
        # 保存结果
        result_path = os.path.join(run_dir, "result.json")
        with open(result_path, 'w', encoding='utf-8') as f:
            json.dump(result_summary, f, indent=2, ensure_ascii=False)
        
        # 更新数据库
        complete_evaluation(eval_id, result_summary)
        
        return {"status": "success", "eval_id": eval_id}
        
    except Exception as exc:
        # 记录错误
        error_msg = str(exc)
        
        # 更新进度文件
        progress_path = os.path.join(settings.EVAL_RUNS_DIR, eval_id, "progress.json")
        if os.path.exists(progress_path):
            with open(progress_path, 'r', encoding='utf-8') as f:
                progress = json.load(f)
            progress["status"] = "failed"
            progress["error"] = error_msg
            with open(progress_path, 'w', encoding='utf-8') as f:
                json.dump(progress, f, indent=2)
        
        # 更新数据库
        from app.core.database import SessionLocal
        from app.models.database import Evaluation
        db = SessionLocal()
        try:
            evaluation = db.query(Evaluation).filter(Evaluation.id == eval_id).first()
            if evaluation:
                evaluation.status = "failed"
                evaluation.error_message = error_msg
                evaluation.completed_at = datetime.now()
                db.commit()
        finally:
            db.close()
        
        # 重试逻辑
        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc, countdown=60)
        
        return {"status": "failed", "error": error_msg, "eval_id": eval_id}


def start_evaluation_task(eval_id: str) -> str:
    """启动 Eval 任务的辅助函数"""
    task = run_evaluation_task.delay(eval_id)
    return task.id
