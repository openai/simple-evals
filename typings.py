from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

Message = Dict[str, Any]  # keys role, content
MessageList = List[Message]

@dataclass
class EvalResult:
    """
    Result of running an evaluation (usually consisting of many samples)
    """
    score: Optional[float]  # top-line metric
    metrics: Optional[Dict[str, float]]  # other metrics
    convos: List[MessageList]  # sampled conversations

@dataclass
class SingleEvalResult:
    """
    Result of evaluating a single sample
    """
    score: Optional[float]
    metrics: Dict[str, float] = field(default_factory=dict)
    convo: Optional[MessageList] = None  # sampled conversation