import time

from utils.logger import get_logger

logger = get_logger(__name__)


def load_timer():
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            elapsed_time = end_time - start_time
            logger.info(f"{elapsed_time:.2f}s --> {func.__name__}: {args[1][0:-5]}")
            return result
        return wrapper
    return decorator


