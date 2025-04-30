"""
Logger module for the VRP solver.
Provides utility functions for logging messages with different indentation levels.
"""

# Configure logging
VERBOSE = True  # Set to False to reduce output

def log(message, level=1):
    """
    Simple logging function with indentation based on level.
    
    Args:
        message (str): The message to log
        level (int): The indentation level (default: 1)
    """
    if VERBOSE:
        indent = "  " * (level - 1)
        print(f"{indent}{message}")

def set_verbose(verbose):
    """
    Set the verbosity level for logging.
    
    Args:
        verbose (bool): Whether to enable verbose logging
    """
    global VERBOSE
    VERBOSE = verbose