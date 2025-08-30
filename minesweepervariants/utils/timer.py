import time
from typing import Callable


HISTORY = []

MAP = ["UNKNOWN", "MODEL_INVALID", "FEASIBLE", "INFEASIBLE", "OPTIMAL"]

def timer[T](func: Callable[..., T]) -> Callable[..., T]:
    def wrapper(*args, **kwargs):
        ts = time.time()
        result = func(*args, **kwargs)
        te = time.time()
        HISTORY.append({
            "result": MAP[result], # type: ignore
            "time": te - ts
        })
        return result
    return wrapper