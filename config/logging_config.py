'''
Logging configuration module for setting up logging in Python applications.
This module provides a function to set up logging with both file and console handlers, ensuring that logs are written in UTF-8 encoding.
It creates a directory for logs if it does not exist and configures the logger with a specified name.'''
import os
import logging
from typing import List

def setup_logging(name: str, log_dir: str = 'logs') -> logging.Logger: 
    '''Set up logging configuration for the application.
    Args:
        name (str): The name of the logger.
        log_dir (str): The directory where log files will be stored. Defaults to 'logs'.
    Returns:
        logging.Logger: Configured logger instance.
    '''
    
    # Ensure logs directory exists
    os.makedirs(log_dir, exist_ok=True)

    # Create a logger with the specified name
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Create a file handler and set its level to INFO
    log_file = os.path.join(log_dir, f"{name}.log")

    # Avoid duplicate handlers
    if not logger.handlers:
        # Create a file handler for logging to a file
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] - %(message)s")
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)
        logger.addHandler(file_handler)

        # Create a stream handler for console output
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        stream_handler.setLevel(logging.INFO)
        logger.addHandler(stream_handler)
    
    return logger