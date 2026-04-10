import sys
import logging
import subprocess


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """Get a logger with the specified name and level. The logger will log to stdout.

    Args:
        name (str): The name of the logger.
        level (int): The logging level.

    Returns:
        logging.Logger: The logger.
    """
    # Check if the logger already has handlers
    if logging.getLogger(name).hasHandlers():
        return logging.getLogger(name)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(level)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger


def get_git_changes():
    """Executes git diff to find added, modified, and deleted files.

    Returns:
        dict: A dictionary of file paths and their git change status {file_path: 'A'/'M'/'D'}
    """
    logger = get_logger(__name__)
    try:
        # We use HEAD~1 to check against the previous commit.
        # In a squashed PR merge, this gets the difference since the last merge baseline.
        # --no-renames ensures renamed files are treated explicitly as a Delete and an Add.
        result = subprocess.run(
            ["git", "diff", "--name-status", "--no-renames", "HEAD~1", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError as e:
        logger.error(f"Git diff failed. Ensure fetchDepth: 0 is set. Error: {e.stderr}")
        return {}

    changes = {}
    for line in result.stdout.strip().split("\n"):
        if not line:
            continue
        parts = line.split("\t")
        if len(parts) >= 2:
            status = parts[0][0]  # Get A, M and D
            file_path = parts[-1]
            changes[file_path] = status

    return changes
