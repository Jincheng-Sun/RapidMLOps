import sys
import logging
import subprocess


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """Get a logger with the specified name and level. The logger will log to stdout.

    Args:
        name: str, The name of the logger.
        level: int, The logging level.

    Returns:
        logging.Logger: The logger.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(level)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
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
