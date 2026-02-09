"""
Base Logger Configuration
Simple per-thread logging without clutter
"""

import logging
import os
from typing import Optional
from pathlib import Path

# Project root (2 levels up from this file)
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
LOG_BASE_DIR = PROJECT_ROOT / "logs"
APP_LOG_DIR = LOG_BASE_DIR / "app"
MEMORY_LOG_DIR = LOG_BASE_DIR / "memory"
WORKFLOW_LOG_DIR = LOG_BASE_DIR / "workflow"

for directory in [APP_LOG_DIR, MEMORY_LOG_DIR, WORKFLOW_LOG_DIR]:
    os.makedirs(directory, exist_ok=True)

# Log format
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def get_logger(logger_type: str, thread_id: Optional[str] = None) -> logging.Logger:
    """
    Get a logger for specific type and thread
    
    Args:
        logger_type: 'app', 'memory', or 'workflow'
        thread_id: Optional thread ID for per-thread logging
    """
    if thread_id:
        log_dir = {
            'app': APP_LOG_DIR,
            'memory': MEMORY_LOG_DIR,
            'workflow': WORKFLOW_LOG_DIR
        }[logger_type]
        
        log_file = os.path.join(log_dir, f"{logger_type}_{thread_id}.log")
        logger_name = f"{logger_type}_{thread_id}"
    else:
        log_file = os.path.join(LOG_BASE_DIR, f"{logger_type}.log")
        logger_name = f"{logger_type}_main"
    
    # Get or create logger
    logger = logging.getLogger(logger_name)
    
    # Only configure if not already configured
    if not logger.handlers:
        handler = logging.FileHandler(log_file, encoding='utf-8')
        handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
        
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)
        logger.propagate = False
    
    return logger
