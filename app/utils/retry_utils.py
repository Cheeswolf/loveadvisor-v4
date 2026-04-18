"""
LoveAdvisor V3 - Retry Utilities
Phase 1: Engineering Skeleton Initialization

This module provides utilities for retrying failed operations with
exponential backoff, jitter, and configurable exception handling.
"""

import asyncio
import random
import time
from typing import Callable, Type, Tuple, List, Optional, Any, Union
from functools import wraps
import logging

logger = logging.getLogger(__name__)


class RetryConfig:
    """
    Configuration for retry behavior.

    Attributes:
        max_attempts: Maximum number of retry attempts (including initial).
        base_delay: Base delay in seconds for exponential backoff.
        max_delay: Maximum delay in seconds.
        jitter: Whether to add random jitter to delays.
        retry_exceptions: Tuple of exception types to retry on.
        backoff_factor: Multiplier for exponential backoff.
        timeout: Overall timeout in seconds (None for no timeout).
    """

    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 30.0,
        jitter: bool = True,
        retry_exceptions: Tuple[Type[Exception], ...] = (Exception,),
        backoff_factor: float = 2.0,
        timeout: Optional[float] = None
    ):
        self.max_attempts = max(max_attempts, 1)
        self.base_delay = max(base_delay, 0.0)
        self.max_delay = max(max_delay, self.base_delay)
        self.jitter = jitter
        self.retry_exceptions = retry_exceptions
        self.backoff_factor = max(backoff_factor, 1.0)
        self.timeout = timeout

    def calculate_delay(self, attempt: int) -> float:
        """
        Calculate delay for a specific attempt.

        Args:
            attempt: Current attempt number (0-indexed).

        Returns:
            Delay in seconds.
        """
        if attempt == 0:
            return 0.0

        # Exponential backoff
        delay = self.base_delay * (self.backoff_factor ** (attempt - 1))

        # Cap at max delay
        delay = min(delay, self.max_delay)

        # Add jitter if enabled
        if self.jitter:
            # Random jitter between 0.5 and 1.5 of the delay
            jitter_factor = 0.5 + random.random()  # 0.5 to 1.5
            delay *= jitter_factor

        return delay


class RetryError(Exception):
    """
    Exception raised when all retry attempts fail.

    Attributes:
        last_exception: The exception from the final attempt.
        attempts: Number of attempts made.
        total_delay: Total time spent waiting between attempts.
    """

    def __init__(
        self,
        last_exception: Exception,
        attempts: int,
        total_delay: float
    ):
        self.last_exception = last_exception
        self.attempts = attempts
        self.total_delay = total_delay
        super().__init__(
            f"Failed after {attempts} attempts "
            f"(total delay: {total_delay:.2f}s): {last_exception}"
        )


def retry_with_backoff(
    config: Optional[RetryConfig] = None,
    **kwargs
) -> Callable:
    """
    Decorator for retrying functions with exponential backoff.

    Args:
        config: RetryConfig instance or None to use defaults.
        **kwargs: Configuration parameters for RetryConfig.

    Returns:
        Decorator function.
    """
    if config is None:
        config = RetryConfig(**kwargs)

    def decorator(func: Callable) -> Callable:
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                return await _retry_async(func, config, *args, **kwargs)
            return async_wrapper
        else:
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                return _retry_sync(func, config, *args, **kwargs)
            return sync_wrapper

    return decorator


async def _retry_async(
    func: Callable,
    config: RetryConfig,
    *args,
    **kwargs
) -> Any:
    """
    Retry async function with exponential backoff.

    Args:
        func: Async function to retry.
        config: Retry configuration.
        *args: Function arguments.
        **kwargs: Function keyword arguments.

    Returns:
        Function result.

    Raises:
        RetryError: If all attempts fail.
    """
    last_exception = None
    total_delay = 0.0
    start_time = time.time()

    for attempt in range(config.max_attempts):
        # Check timeout
        if config.timeout is not None:
            elapsed = time.time() - start_time
            if elapsed > config.timeout:
                raise TimeoutError(f"Operation timed out after {elapsed:.2f}s")

        # Calculate delay (0 for first attempt)
        delay = config.calculate_delay(attempt)
        if delay > 0:
            total_delay += delay
            await asyncio.sleep(delay)

        try:
            return await func(*args, **kwargs)

        except config.retry_exceptions as e:
            last_exception = e

            # Log retry attempt
            logger.warning(
                f"Attempt {attempt + 1}/{config.max_attempts} failed: {e}. "
                f"Next retry in {config.calculate_delay(attempt + 1):.2f}s"
            )

            # Check if we should retry
            if attempt == config.max_attempts - 1:
                logger.error(f"All {config.max_attempts} attempts failed")
                raise RetryError(
                    last_exception=last_exception,
                    attempts=config.max_attempts,
                    total_delay=total_delay
                )

    # This should never be reached
    raise RetryError(
        last_exception=last_exception or Exception("Unknown error"),
        attempts=config.max_attempts,
        total_delay=total_delay
    )


def _retry_sync(
    func: Callable,
    config: RetryConfig,
    *args,
    **kwargs
) -> Any:
    """
    Retry sync function with exponential backoff.

    Args:
        func: Sync function to retry.
        config: Retry configuration.
        *args: Function arguments.
        **kwargs: Function keyword arguments.

    Returns:
        Function result.

    Raises:
        RetryError: If all attempts fail.
    """
    last_exception = None
    total_delay = 0.0
    start_time = time.time()

    for attempt in range(config.max_attempts):
        # Check timeout
        if config.timeout is not None:
            elapsed = time.time() - start_time
            if elapsed > config.timeout:
                raise TimeoutError(f"Operation timed out after {elapsed:.2f}s")

        # Calculate delay (0 for first attempt)
        delay = config.calculate_delay(attempt)
        if delay > 0:
            total_delay += delay
            time.sleep(delay)

        try:
            return func(*args, **kwargs)

        except config.retry_exceptions as e:
            last_exception = e

            # Log retry attempt
            logger.warning(
                f"Attempt {attempt + 1}/{config.max_attempts} failed: {e}. "
                f"Next retry in {config.calculate_delay(attempt + 1):.2f}s"
            )

            # Check if we should retry
            if attempt == config.max_attempts - 1:
                logger.error(f"All {config.max_attempts} attempts failed")
                raise RetryError(
                    last_exception=last_exception,
                    attempts=config.max_attempts,
                    total_delay=total_delay
                )

    # This should never be reached
    raise RetryError(
        last_exception=last_exception or Exception("Unknown error"),
        attempts=config.max_attempts,
        total_delay=total_delay
    )


def retry_on_exception(
    exceptions: Union[Type[Exception], Tuple[Type[Exception], ...]],
    max_attempts: int = 3,
    **kwargs
) -> Callable:
    """
    Convenience decorator for retrying on specific exceptions.

    Args:
        exceptions: Exception type(s) to retry on.
        max_attempts: Maximum retry attempts.
        **kwargs: Additional RetryConfig parameters.

    Returns:
        Decorator function.
    """
    if not isinstance(exceptions, tuple):
        exceptions = (exceptions,)

    config = RetryConfig(
        max_attempts=max_attempts,
        retry_exceptions=exceptions,
        **kwargs
    )

    return retry_with_backoff(config)


class CircuitBreaker:
    """
    Circuit breaker pattern implementation.

    Prevents repeated calls to failing services by opening the circuit
    after a threshold of failures.
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 30.0,
        half_open_max_attempts: int = 3
    ):
        """
        Initialize circuit breaker.

        Args:
            failure_threshold: Number of failures before opening circuit.
            recovery_timeout: Time in seconds before attempting recovery.
            half_open_max_attempts: Maximum attempts in half-open state.
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_attempts = half_open_max_attempts

        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self.failure_count = 0
        self.last_failure_time = None
        self.half_open_attempts = 0

    def record_success(self):
        """Record a successful operation."""
        if self.state == "HALF_OPEN":
            # Successful call in half-open state, close the circuit
            self.state = "CLOSED"
            self.failure_count = 0
            self.half_open_attempts = 0
            logger.info("Circuit breaker closed after successful recovery")
        elif self.state == "CLOSED":
            # Reset failure count on success
            self.failure_count = max(0, self.failure_count - 1)

    def record_failure(self):
        """Record a failed operation."""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.state == "CLOSED" and self.failure_count >= self.failure_threshold:
            # Too many failures, open the circuit
            self.state = "OPEN"
            logger.warning(f"Circuit breaker opened after {self.failure_count} failures")
        elif self.state == "HALF_OPEN":
            # Failed in half-open state, reopen the circuit
            self.half_open_attempts += 1
            if self.half_open_attempts >= self.half_open_max_attempts:
                self.state = "OPEN"
                logger.warning("Circuit breaker reopened after failed recovery attempts")

    def allow_request(self) -> bool:
        """
        Check if a request should be allowed.

        Returns:
            True if request should be allowed, False otherwise.
        """
        if self.state == "CLOSED":
            return True
        elif self.state == "OPEN":
            # Check if recovery timeout has passed
            if self.last_failure_time is None:
                return False

            elapsed = time.time() - self.last_failure_time
            if elapsed >= self.recovery_timeout:
                # Move to half-open state
                self.state = "HALF_OPEN"
                self.half_open_attempts = 0
                logger.info("Circuit breaker moved to half-open state")
                return True
            return False
        elif self.state == "HALF_OPEN":
            return self.half_open_attempts < self.half_open_max_attempts
        else:
            return False

    def __call__(self, func: Callable) -> Callable:
        """Decorator to apply circuit breaker to a function."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not self.allow_request():
                raise CircuitBreakerOpenError("Circuit breaker is open")

            try:
                result = func(*args, **kwargs)
                self.record_success()
                return result
            except Exception as e:
                self.record_failure()
                raise

        return wrapper


class CircuitBreakerOpenError(Exception):
    """Exception raised when circuit breaker is open."""
    pass