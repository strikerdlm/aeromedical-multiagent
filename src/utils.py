"""
General-purpose utility functions for the application.

This module provides common helper functions, such as decorators for
retrying operations with exponential backoff, which are used across
various parts of the application to improve robustness and reliability.
"""
import time
import random
import logging
from functools import wraps
from typing import Callable, Any, Tuple, Type

from .config import AppConfig

logger = logging.getLogger(__name__)

def retry_with_exponential_backoff(
    retries: int = AppConfig.MAX_RETRIES,
    initial_delay: float = AppConfig.RETRY_DELAY,
    backoff_factor: float = AppConfig.RETRY_BACKOFF_FACTOR,
    jitter: bool = True,
    allowed_exceptions: Tuple[Type[Exception], ...] = (Exception,)
) -> Callable:
    """
    A decorator for retrying a function with exponential backoff.

    This decorator will retry a function if it raises one of the exceptions in
    `allowed_exceptions`. The delay between retries increases exponentially.

    Args:
        retries: The maximum number of times to retry the function.
        initial_delay: The initial delay in seconds before the first retry.
        backoff_factor: The multiplier for increasing the delay after each retry.
        jitter: If True, adds a random small amount of time to the delay
                to prevent a "thundering herd" problem.
        allowed_exceptions: A tuple of exception classes that should trigger a retry.

    Returns:
        A decorator that can be applied to a function.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            delay = initial_delay
            for i in range(retries):
                try:
                    return func(*args, **kwargs)
                except allowed_exceptions as e:
                    if i == retries - 1:
                        logger.error(f"Function {func.__name__} failed after {retries} retries. Error: {e}")
                        raise

                    backoff_delay = delay * (backoff_factor ** i)
                    if jitter:
                        backoff_delay += random.uniform(0, backoff_delay * 0.1)

                    logger.warning(f"Function {func.__name__} failed with {e}. Retrying in {backoff_delay:.2f} seconds...")
                    time.sleep(backoff_delay)
        return wrapper
    return decorator
