from functools import wraps
from typing import Callable

IGNORED_EXCEPTIONS = (
    AttributeError,
    TypeError,
    ValueError,
    )


def safe_return(func: Callable = None, *, exception=IGNORED_EXCEPTIONS, default_return=None):
    def func_wrapper(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except exception as e:
                return default_return
        return wrapper
    if func:
        return func_wrapper(func)

    return func_wrapper
