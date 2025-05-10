# semantic_match.py  ―  drift-aware scorer (≈10行)

import numpy as np
from sentence_transformers import SentenceTransformer

_model = SentenceTransformer("all-MiniLM-L6-v2")   # 軽量埋め込みモデル

def score(ref: str, pred: str) -> float:
    """ref が pred に含まれ、
       かつ埋め込み距離 drift ≤0.2 なら満点。
       drift が大きいほど減点。"""
    if ref.strip() not in pred.strip():          # 完全一致しなければ即 0
        return 0.0
    r, p = _model.encode([ref, pred])
    drift = 1 - np.dot(r, p) / (np.linalg.norm(r) * np.linalg.norm(p))
    return max(0.0, 1 - drift * 5)               # drift>0.2 → 減点
