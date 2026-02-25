from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime


# ==================== PromptFileConfig Schemas ====================

class PromptFileConfigBase(BaseModel):
    key: str
    name: str
    description: Optional[str] = None
    external_path: str
    sort_order: int = 0
    is_active: bool = True


class PromptFileConfigCreate(PromptFileConfigBase):
    pass


class PromptFileConfigUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    external_path: Optional[str] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


class PromptFileConfigResponse(PromptFileConfigBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== PromptVersion Schemas ====================

class PromptFileContent(BaseModel):
    config_key: str
    content: str


class PromptVersionCreate(BaseModel):
    author: str
    description: Optional[str] = None
    parent_version_id: Optional[str] = None
    files: List[PromptFileContent]


class PromptFileResponse(BaseModel):
    config_key: str
    content: str
    
    class Config:
        from_attributes = True


class PromptVersionResponse(BaseModel):
    id: str
    version_number: int = 0  # 前端动态计算
    created_at: datetime
    author: str
    description: Optional[str] = None
    is_active: bool
    parent_version_id: Optional[str] = None
    files: List[PromptFileResponse] = []
    
    class Config:
        from_attributes = True


class PromptVersionListItem(BaseModel):
    id: str
    version_number: int = 0  # 前端动态计算
    created_at: datetime
    author: str
    description: Optional[str] = None
    is_active: bool
    
    class Config:
        from_attributes = True


class VersionDiffResponse(BaseModel):
    version1_id: str
    version2_id: str
    diffs: Dict[str, Any]  # {config_key: {old: "...", new: "..."}}


# ==================== Evaluation Schemas ====================

class EvaluationCreate(BaseModel):
    version_id: str
    benchmark: str  # healthbench / csedb / usmle
    num_examples: Optional[int] = None
    n_threads: int = 1
    description: Optional[str] = None


class EvaluationResponse(BaseModel):
    id: str
    version_id: str
    benchmark: str
    num_examples: Optional[int]
    n_threads: int
    status: str
    description: Optional[str]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    result_summary: Optional[Dict[str, Any]]
    error_message: Optional[str]
    
    class Config:
        from_attributes = True


class EvaluationProgressResponse(BaseModel):
    id: str
    status: str
    total: int
    completed: int
    current_score: Optional[float]
    latest_samples: List[Dict[str, Any]]
    metrics: Optional[Dict[str, Any]]


class EvaluationListItem(BaseModel):
    id: str
    version_id: str
    benchmark: str
    status: str
    description: Optional[str]
    created_at: datetime
    result_summary: Optional[Dict[str, Any]]
    
    class Config:
        from_attributes = True


# ==================== Common Schemas ====================

class MessageResponse(BaseModel):
    message: str


class ErrorResponse(BaseModel):
    detail: str
