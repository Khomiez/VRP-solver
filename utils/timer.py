"""
Timer module for the VRP solver.
Provides a context manager for timing code blocks.
"""

import time
from contextlib import contextmanager

@contextmanager
def timer(description):
    """
    Context manager for timing code blocks.
    
    Args:
        description (str): Description of the timed operation
    
    Yields:
        None
    
    Example:
        with timer("Operation time"):
            # Code to time
            pass
    """
    start = time.time()
    yield
    elapsed = time.time() - start
    print(f"{description}: {elapsed:.3f} seconds")