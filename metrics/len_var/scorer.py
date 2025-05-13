import statistics as st
from typing import List

def _window_lengths(tokens: List[str], window: int = 5) -> List[int]:
    return [len(" ".join(tokens[i:i+window]))
            for i in range(len(tokens) - window + 1)]

def score(prediction: str, reference: str = "", window: int = 5) -> float:
    """
    Length-variance score (0 = 安定, 1 ≒ 大揺れ)
    定義: sliding-window の文字長 標準偏差 ÷ 平均長
    """
    toks = prediction.split()
    if len(toks) < window:
        return 0.0
    lens = _window_lengths(toks, window)
    return st.pstdev(lens) / max(st.mean(lens), 1)
