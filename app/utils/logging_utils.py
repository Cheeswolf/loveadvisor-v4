"""
LoveAdvisor V3 - Logging Utilities
Phase 1: Engineering Skeleton Initialization

This module provides logging configuration and utilities for the application.
It supports structured logging, log rotation, and different log levels.
"""

import logging
import logging.handlers
import sys
import os
import json
from datetime import datetime
from typing import Optional, Dict, Any, Callable
from pathlib import Path

# Default log format
DEFAULT_LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
DEFAULT_JSON_LOG_FORMAT = {
    'timestamp': '%(asctime)s',
    'logger': '%(name)s',
    'level': '%(levelname)s',
    'message': '%(message)s',
    'module': '%(module)s',
    'function': '%(funcName)s',
    'line': '%(lineno)d'
}


class StructuredFormatter(logging.Formatter):
    """
    Formatter for structured JSON logging.

    This formatter outputs logs as JSON objects for easier parsing
    by log aggregation systems.
    """

    def __init__(self, fmt_dict: Optional[Dict[str, str]] = None):
        """
        Initialize structured formatter.

        Args:
            fmt_dict: Dictionary mapping field names to format strings.
        """
        super().__init__()
        self.fmt_dict = fmt_dict or DEFAULT_JSON_LOG_FORMAT

    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON.

        Args:
            record: Log record to format.

        Returns:
            JSON string.
        """
        log_dict = {}
        for key, fmt in self.fmt_dict.items():
            log_dict[key] = fmt % record.__dict__

        # Add extra attributes
        if hasattr(record, 'extra') and record.extra:
            log_dict.update(record.extra)

        # Add exception info if present
        if record.exc_info:
            log_dict['exception'] = self.formatException(record.exc_info)

        return json.dumps(log_dict, ensure_ascii=False)


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    log_format: str = "text",
    max_bytes: int = 10 * 1024 * 1024,  # 10 MB
    backup_count: int = 5,
    enable_console: bool = True
) -> None:
    """
    Set up logging configuration for the application.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        log_file: Path to log file (optional).
        log_format: Log format ("text" or "json").
        max_bytes: Maximum log file size before rotation.
        backup_count: Number of backup log files to keep.
        enable_console: Whether to enable console logging.
    """
    # Convert log level string to logging constant
    level = getattr(logging, log_level.upper(), logging.INFO)

    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create formatter
    if log_format.lower() == "json":
        formatter = StructuredFormatter()
    else:
        formatter = logging.Formatter(DEFAULT_LOG_FORMAT)

    # Console handler
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    # File handler (if log file specified)
    if log_file:
        # Create log directory if it doesn't exist
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.handlers.RotatingFileHandler(
            filename=log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    # Log startup message
    root_logger.info(f"Logging initialized. Level: {log_level}, Format: {log_format}")


def get_logger(
    name: str,
    extra_fields: Optional[Dict[str, Any]] = None
) -> logging.Logger:
    """
    Get a logger with optional extra fields for structured logging.

    Args:
        name: Logger name (usually __name__).
        extra_fields: Extra fields to include in all log messages.

    Returns:
        Configured logger instance.
    """
    logger = logging.getLogger(name)

    # Add extra fields to log records
    if extra_fields:
        old_factory = logging.getLogRecordFactory()

        def record_factory(*args, **kwargs):
            record = old_factory(*args, **kwargs)
            record.extra = extra_fields.copy()
            return record

        logging.setLogRecordFactory(record_factory)

    return logger


def log_execution_time(logger: Optional[logging.Logger] = None):
    """
    Decorator to log function execution time.

    Args:
        logger: Logger to use (defaults to function module logger).

    Returns:
        Decorator function.
    """
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            # Get logger
            nonlocal logger
            if logger is None:
                logger = logging.getLogger(func.__module__)

            # Log start
            start_time = datetime.now()
            logger.debug(f"Starting {func.__name__}")

            try:
                # Execute function
                result = func(*args, **kwargs)

                # Log completion
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                logger.debug(f"Completed {func.__name__} in {duration:.3f}s")

                return result

            except Exception as e:
                # Log error
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                logger.error(f"Failed {func.__name__} in {duration:.3f}s: {e}")
                raise

        return wrapper

    return decorator


class RequestLogger:
    """
    Logger for tracking individual request lifecycle.

    This logger attaches to a specific request ID and logs all
    events related to that request.
    """

    def __init__(self, request_id: str, logger: Optional[logging.Logger] = None):
        """
        Initialize request logger.

        Args:
            request_id: Unique request identifier.
            logger: Base logger to use.
        """
        self.request_id = request_id
        self.logger = logger or logging.getLogger(__name__)

    def log(self, level: str, message: str, **kwargs):
        """
        Log message with request context.

        Args:
            level: Log level (debug, info, warning, error, critical).
            message: Log message.
            **kwargs: Additional fields for structured logging.
        """
        log_method = getattr(self.logger, level.lower())

        # Add request context
        extra = kwargs.copy()
        extra['request_id'] = self.request_id

        log_method(message, extra=extra)

    def debug(self, message: str, **kwargs):
        """Log debug message."""
        self.log('debug', message, **kwargs)

    def info(self, message: str, **kwargs):
        """Log info message."""
        self.log('info', message, **kwargs)

    def warning(self, message: str, **kwargs):
        """Log warning message."""
        self.log('warning', message, **kwargs)

    def error(self, message: str, **kwargs):
        """Log error message."""
        self.log('error', message, **kwargs)

    def critical(self, message: str, **kwargs):
        """Log critical message."""
        self.log('critical', message, **kwargs)

    def log_pipeline_stage(self, stage: str, status: str, details: str = ""):
        """
        Log pipeline stage execution.

        Args:
            stage: Pipeline stage name.
            status: Stage status (started, completed, failed).
            details: Additional details.
        """
        self.info(
            f"Pipeline stage {stage} {status}",
            pipeline_stage=stage,
            stage_status=status,
            stage_details=details
        )

    def log_llm_call(self, provider: str, model: str, duration: float, success: bool):
        """
        Log LLM API call.

        Args:
            provider: LLM provider name.
            model: Model name.
            duration: Call duration in seconds.
            success: Whether call succeeded.
        """
        self.info(
            f"LLM call: {provider}/{model}",
            llm_provider=provider,
            llm_model=model,
            llm_duration=duration,
            llm_success=success
        )


def setup_request_logging(request_id: str) -> RequestLogger:
    """
    Convenience function to create a RequestLogger.

    Args:
        request_id: Request identifier.

    Returns:
        RequestLogger instance.
    """
    return RequestLogger(request_id)