from functools import wraps
from typing import Callable


def safe_return(func: Callable = None, *, exception=Exception, default_return=None):
    def func_wrapper(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except exception:
                return default_return
        return wrapper
    if func:
        return func_wrapper(func)

    return func_wrapper
