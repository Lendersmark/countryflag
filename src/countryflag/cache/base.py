"""
Base cache interface for the countryflag package.

This module contains the base Cache interface that all cache implementations must implement.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional


class Cache(ABC):
    """
    Abstract base class for caching implementations.

    This class defines the interface that all cache implementations must adhere to.
    """

    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from the cache.

        Args:
            key: The cache key.

        Returns:
            The cached value, or None if the key is not in the cache.
        """
        pass

    @abstractmethod
    def set(self, key: str, value: Any) -> None:
        """
        Set a value in the cache.

        Args:
            key: The cache key.
            value: The value to cache.
        """
        pass

    @abstractmethod
    def delete(self, key: str) -> None:
        """
        Delete a value from the cache.

        Args:
            key: The cache key to delete.
        """
        pass

    @abstractmethod
    def clear(self) -> None:
        """
        Clear all values from the cache.
        """
        pass

    @abstractmethod
    def contains(self, key: str) -> bool:
        """
        Check if a key exists in the cache.

        Args:
            key: The cache key to check.

        Returns:
            bool: True if the key exists in the cache, False otherwise.
        """
        pass
