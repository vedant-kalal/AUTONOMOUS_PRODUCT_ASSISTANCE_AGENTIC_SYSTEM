"""
Base Logger Configuration
Logs to both a per-thread file AND the terminal (with color).
"""

import logging
import os
from typing import Optional
from pathlib import Path

# ── Project paths ──────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
LOG_BASE_DIR = PROJECT_ROOT / "logs"
APP_LOG_DIR      = LOG_BASE_DIR / "app"
MEMORY_LOG_DIR   = LOG_BASE_DIR / "memory"
WORKFLOW_LOG_DIR = LOG_BASE_DIR / "workflow"

for directory in [APP_LOG_DIR, MEMORY_LOG_DIR, WORKFLOW_LOG_DIR]:
    os.makedirs(directory, exist_ok=True)

# ── Formats ────────────────────────────────────────────────────────────────────
FILE_FORMAT    = "%(asctime)s | %(levelname)-8s | %(message)s"
TERMINAL_FORMAT = "%(asctime)s | %(levelname)-8s | %(message)s"
DATE_FORMAT    = "%H:%M:%S"   # shorter for terminal readability

# ── ANSI color codes ───────────────────────────────────────────────────────────
RESET   = "\033[0m"
BOLD    = "\033[1m"
GREY    = "\033[90m"
CYAN    = "\033[96m"
GREEN   = "\033[92m"
YELLOW  = "\033[93m"
RED     = "\033[91m"
MAGENTA = "\033[95m"

LEVEL_COLORS = {
    logging.DEBUG:    GREY,
    logging.INFO:     CYAN,
    logging.WARNING:  YELLOW,
    logging.ERROR:    RED,
    logging.CRITICAL: MAGENTA,
}

# ── Colored terminal formatter ─────────────────────────────────────────────────
class ColoredFormatter(logging.Formatter):
    """Applies ANSI colors to log level and message for terminal output."""

    def format(self, record: logging.LogRecord) -> str:
        color = LEVEL_COLORS.get(record.levelno, RESET)
        record.levelname = f"{color}{record.levelname:<8}{RESET}"
        # Dim the timestamp
        formatted = super().format(record)
        ts_end = formatted.index("|")
        return GREY + formatted[:ts_end] + RESET + formatted[ts_end:]


# ── Shared terminal handler (one for the whole process) ───────────────────────
_terminal_handler: Optional[logging.StreamHandler] = None

def _get_terminal_handler() -> logging.StreamHandler:
    global _terminal_handler
    if _terminal_handler is None:
        _terminal_handler = logging.StreamHandler()
        _terminal_handler.setLevel(logging.INFO)
        _terminal_handler.setFormatter(
            ColoredFormatter(TERMINAL_FORMAT, DATE_FORMAT)
        )
    return _terminal_handler


# ── Public API ─────────────────────────────────────────────────────────────────
def get_logger(logger_type: str, thread_id: Optional[str] = None) -> logging.Logger:
    """
    Get a logger that writes to both a per-thread file AND the terminal.

    Args:
        logger_type: 'app', 'memory', or 'workflow'
        thread_id:   Optional thread ID for per-thread log files
    """
    if thread_id:
        log_dir = {
            'app':      APP_LOG_DIR,
            'memory':   MEMORY_LOG_DIR,
            'workflow': WORKFLOW_LOG_DIR,
        }[logger_type]
        log_file    = os.path.join(log_dir, f"{logger_type}_{thread_id}.log")
        logger_name = f"{logger_type}_{thread_id}"
    else:
        log_file    = os.path.join(LOG_BASE_DIR, f"{logger_type}.log")
        logger_name = f"{logger_type}_main"

    logger = logging.getLogger(logger_name)

    if not logger.handlers:
        # ── File handler ──────────────────────────────────────────────────────
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(
            logging.Formatter(FILE_FORMAT, "%Y-%m-%d %H:%M:%S")
        )
        file_handler.setLevel(logging.DEBUG)

        logger.setLevel(logging.INFO)
        logger.addHandler(file_handler)
        logger.addHandler(_get_terminal_handler())  # ← prints to terminal
        logger.propagate = False

    return logger
