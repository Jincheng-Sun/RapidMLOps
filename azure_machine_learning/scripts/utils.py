import os
import sys
import logging
import subprocess


def get_logger(name: str, level: int = logging.INFO, log_dir="lazy_mlops_logs") -> logging.Logger:
    """Get a logger with the specified name and level. The logger will log to stdout.

    Args:
        name: str, The name of the logger.
        level: int, default to logging.INFO level, The logging level.
        log_dir: str, default to 'lazy_mlops_logs', logging file saving directory

    Returns:
        logging.Logger: The logger.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # Stream handler
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    # File handler
    os.makedirs(log_dir, exist_ok=True)
    sanitized_name = name.replace(".", "_")
    log_path = os.path.join(log_dir, f"{sanitized_name}.log")
    file_handler = logging.FileHandler(log_path)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger


def get_git_changes():
    """Returns a dictionary of changed files categorized by status (A, M, D)."""
    changes = {"A": [], "M": [], "D": []}
    result = subprocess.run(["git", "diff", "--name-status", "HEAD^", "HEAD"],
                            capture_output=True,
                            text=True
                            )
    for line in result.stdout.strip().split("\n"):
        if line:
            status, file_path = line.split("\t", 1)
            if status in changes:
                changes[status].append(file_path)
    return changes
