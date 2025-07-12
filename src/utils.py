"""
Utility functions for the application.
"""
import time
import random
import logging
from functools import wraps

from .config import AppConfig

logger = logging.getLogger(__name__)

def retry_with_exponential_backoff(
    retries=AppConfig.MAX_RETRIES, 
    initial_delay=AppConfig.RETRY_DELAY, 
    backoff_factor=AppConfig.RETRY_BACKOFF_FACTOR, 
    jitter=True, 
    allowed_exceptions=(Exception,)
):
    """
    A decorator for retrying a function with exponential backoff.

    :param retries: The maximum number of retries.
    :param initial_delay: The initial delay between retries in seconds.
    :param backoff_factor: The factor by which the delay is multiplied each time.
    :param jitter: Whether to add a random jitter to the delay.
    :param allowed_exceptions: A tuple of exception classes to catch and retry on.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
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