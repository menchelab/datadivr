import logging
import sys
from collections.abc import Mapping, MutableMapping
from typing import Any, Callable, Optional, Union

import structlog


def setup_logging(
    level: str = "INFO",
    pretty: bool = True,
    log_file: Optional[str] = None,
) -> None:
    """Configure logging for the entire application.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        pretty: If True, use pretty console output, else JSON
        log_file: Optional file path to write logs to
    """
    # Set log level
    log_level = getattr(logging, level.upper())

    # Configure processors with type annotation
    processors: list[
        Callable[[Any, str, MutableMapping[str, Any]], Union[Mapping[str, Any], str, bytes, bytearray, tuple[Any, ...]]]
    ] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.filter_by_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.StackInfoRenderer(),
        #       structlog.processors.format_exc_info,
    ]

    if pretty:
        processors.append(structlog.dev.ConsoleRenderer(colors=True))
    else:
        processors.append(structlog.processors.JSONRenderer())

    # Basic logging configuration
    config = {
        "format": "%(message)s",
        "level": log_level,
    }

    if log_file:
        config["filename"] = log_file
    else:
        config["stream"] = sys.stdout

    logging.basicConfig(**config)

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> Any:
    """Get a structured logger instance."""
    return structlog.get_logger(name)
