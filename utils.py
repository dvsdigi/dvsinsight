import numpy as np
from numpy.linalg import norm

def cosine_similarity(a, b):
    a = np.array(a, dtype=float)
    b = np.array(b, dtype=float)
    if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
        return 0.0
    return float(np.dot(a, b) / (norm(a) * norm(b)))

def ensure_dirs(path):
    from pathlib import Path
    Path(path).mkdir(parents=True, exist_ok=True)
