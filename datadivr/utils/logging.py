import logging
import os
import sys
from collections.abc import Mapping, MutableMapping
from typing import Any, Callable, Optional, Union

import structlog


def setup_logging(
    level: Optional[str] = None,
    pretty: Optional[bool] = None,
    log_file: Optional[str] = None,
) -> None:
    """Configure logging for the entire application."""
    # Get settings from environment with fallbacks
    level = os.getenv("DATADIVR_LOG_LEVEL", level) or "INFO"
    pretty = os.getenv("DATADIVR_LOG_PRETTY", str(pretty)).lower() != "false" if pretty is not None else True
    log_file = os.getenv("DATADIVR_LOG_FILE", log_file)

    # Set log level
    log_level = getattr(logging, level.upper())

    # Configure processors
    processors: list[
        Callable[[Any, str, MutableMapping[str, Any]], Union[Mapping[str, Any], str, bytes, bytearray, tuple[Any, ...]]]
    ] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.filter_by_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    if log_file:
        processors.append(structlog.dev.ConsoleRenderer(colors=False))
    else:
        if pretty:
            processors.append(structlog.dev.ConsoleRenderer(colors=True))
        else:
            processors.append(structlog.processors.JSONRenderer())

    # Configure standard logging
    logging_config = {
        "format": "%(message)s",
        "level": log_level,
        "force": True,  # Override any existing configuration
    }

    # Add either stream or filename, but not both
    if log_file:
        logging_config["filename"] = log_file
    else:
        logging_config["stream"] = sys.stdout

    logging.basicConfig(**logging_config)

    # Configure structlog
    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Ensure all loggers respect our level setting
    logging.getLogger().setLevel(log_level)


def get_logger(name: str) -> Any:
    """Get a structured logger instance."""
    return structlog.get_logger(name)
