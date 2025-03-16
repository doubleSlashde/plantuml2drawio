"""Logging configuration for the plantuml2drawio package."""

import logging
import logging.handlers
from pathlib import Path
from typing import List, Optional, Union


def setup_logging(
    log_level: Union[str, int] = logging.INFO,
    log_file: Optional[Union[str, Path]] = None,
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
) -> None:
    """Set up logging configuration for the application.

    Args:
        log_level: The logging level (default: INFO)
        log_file: Optional path to a log file. If None, logs only to console
        log_format: The format string for log messages
        max_bytes: Maximum size of each log file before rotation
        backup_count: Number of backup files to keep

    Example:
        >>> setup_logging(log_level="DEBUG", log_file="app.log")
    """
    # Convert string log level to numeric value if necessary
    if isinstance(log_level, str):
        log_level = getattr(logging, log_level.upper())

    # Create formatters and handlers
    formatter = logging.Formatter(log_format)
    handlers: List[logging.Handler] = []

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    handlers.append(console_handler)

    # File handler (if log_file is specified)
    if log_file:
        log_file = Path(log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
        )
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove existing handlers and add new ones
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    for handler in handlers:
        root_logger.addHandler(handler)

    # Create a logger for this package
    logger = logging.getLogger("plantuml2drawio")
    logger.setLevel(log_level)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for the given name.

    Args:
        name: The name of the logger, typically __name__

    Returns:
        A Logger instance

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("This is an info message")
    """
    return logging.getLogger(f"plantuml2drawio.{name}")
