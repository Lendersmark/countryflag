"""
Validation utility functions for the countryflag package.

This module contains utility functions for validating inputs and outputs.
"""

import functools
import logging
from typing import Any, Callable, TypeVar

import typeguard

# Configure logging
logger = logging.getLogger("countryflag.utils.validation")

# Type variable for generic functions
T = TypeVar("T")


def require(predicate: Callable[..., bool], message: str = "Precondition failed"):
    """
    Decorator to enforce preconditions using design by contract.

    Args:
        predicate: A function that takes the same arguments as the decorated function
                  and returns True if the precondition is satisfied.
        message: The error message to raise if the precondition fails.

    Returns:
        The decorated function.

    Raises:
        ValueError: If the precondition is not satisfied.

    Example:
        >>> @require(lambda x: x > 0, "x must be positive")
        ... def sqrt(x):
        ...     return x ** 0.5
        >>> sqrt(4)
        2.0
        >>> sqrt(-1)  # doctest: +ELLIPSIS
        Traceback (most recent call last):
        ...
        ValueError: x must be positive in sqrt
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            if not predicate(*args, **kwargs):
                raise ValueError(f"{message} in {func.__name__}")
            return func(*args, **kwargs)

        return wrapper

    return decorator


def ensure(predicate: Callable[[T], bool], message: str = "Postcondition failed"):
    """
    Decorator to enforce postconditions using design by contract.

    Args:
        predicate: A function that takes the return value of the decorated function
                  and returns True if the postcondition is satisfied.
        message: The error message to raise if the postcondition fails.

    Returns:
        The decorated function with postcondition checking.

    Raises:
        ValueError: If the postcondition is not satisfied.

    Example:
        >>> @ensure(lambda result: result >= 0, "result must be non-negative")
        ... def abs(x):
        ...     return -x  # Bug: should be abs(x)
        >>> abs(1)  # doctest: +ELLIPSIS
        Traceback (most recent call last):
        ...
        ValueError: result must be non-negative in abs
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            result = func(*args, **kwargs)
            if not predicate(result):
                raise ValueError(f"{message} in {func.__name__}")
            return result

        return wrapper

    return decorator


def runtime_typechecked(func: Callable[..., T]) -> Callable[..., T]:
    """
    Decorator to add runtime type checking to a function.

    Args:
        func: The function to decorate.

    Returns:
        The decorated function with runtime type checking.

    Raises:
        TypeError: If the arguments or return value do not match the type annotations.

    Example:
        >>> @runtime_typechecked
        ... def add(x: int, y: int) -> int:
        ...     return x + y
        >>> add(1, 2)
        3
        >>> add("1", 2)  # doctest: +ELLIPSIS
        Traceback (most recent call last):
        ...
        TypeError: ...
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        return typeguard.typechecked(func)(*args, **kwargs)

    return wrapper
