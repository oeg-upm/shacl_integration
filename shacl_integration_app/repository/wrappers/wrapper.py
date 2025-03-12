from functools import wraps
from typing import Callable, Any
import time

def get_time(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start: float = time.perf_counter()
        result: Any = func(*args, **kwargs)
        end: float = time.perf_counter()
        print(f"Execution time of '{func.__name__}' function: ({end - start:.2f} seconds || {(end - start)*1000:.2f} milliseconds)")
        return result
    return wrapper
