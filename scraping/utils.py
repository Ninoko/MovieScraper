import locale
from typing import Callable


def safe_return(exception=Exception, default_return: object = None):
    def wrapper(func: Callable):
        def func_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except exception:
                return default_return
        return func_wrapper
    return wrapper


def set_locale():
    locale.setlocale(locale.LC_TIME, 'pl_PL.UTF-8')
