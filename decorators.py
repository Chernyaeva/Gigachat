from functools import wraps
import logging
import traceback
import inspect

def log(logger):
    def decorator(func):
        @wraps(func)
        def decorated(*args, **kwargs):
            res = func(*args, **kwargs)
            logger.debug(f'Function {func.__name__} called with parameters {args}, {kwargs}. '
                     f'from function {traceback.format_stack()[0].strip().split()[-1]} of module {func.__module__}.'
                     f'Call from function {inspect.stack()[1][3]}')
            return res
        return decorated
    return decorator
