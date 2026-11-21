"""Load this checkout as the simple-evals package when running pytest."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent
_PARENT = _REPO.parent

# types.py would otherwise shadow the standard library module named types.
sys.path[:] = [p for p in sys.path if Path(p).resolve() != _REPO]
if str(_PARENT) not in sys.path:
    sys.path.insert(0, str(_PARENT))
