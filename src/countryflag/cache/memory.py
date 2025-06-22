"""
Memory-based cache implementation for the countryflag package.

This module contains the MemoryCache class, which implements in-memory caching.
"""

from typing import Any, Dict, Optional

from countryflag.cache.base import Cache


class MemoryCache(Cache):
    """
    In-memory cache implementation.

    This class implements a simple in-memory cache using a dictionary.

    Attributes:
        _cache: Dictionary that stores the cached values.
    """

    def __init__(self) -> None:
        """
        Initialize the memory cache.
        """
        self._cache: Dict[str, Any] = {}
        self._hits = 0  # Initialize hit counter

    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from the cache.

        Args:
            key: The cache key.

        Returns:
            The cached value, or None if the key is not in the cache.

        Example:
            >>> cache = MemoryCache()
            >>> cache.set("key", "value")
            >>> cache.get("key")
            'value'
            >>> cache.get("nonexistent")
            None
        """
        value = self._cache.get(key)
        if value is not None:
            self._hits += 1  # Increment hit counter
        return value

    def set(self, key: str, value: Any) -> None:
        """
        Set a value in the cache.

        Args:
            key: The cache key.
            value: The value to cache.

        Example:
            >>> cache = MemoryCache()
            >>> cache.set("key", "value")
            >>> cache.get("key")
            'value'
        """
        self._cache[key] = value

    def delete(self, key: str) -> None:
        """
        Delete a value from the cache.

        Args:
            key: The cache key to delete.

        Example:
            >>> cache = MemoryCache()
            >>> cache.set("key", "value")
            >>> cache.delete("key")
            >>> cache.get("key")
            None
        """
        if key in self._cache:
            del self._cache[key]

    def clear(self) -> None:
        """
        Clear all values from the cache.

        Example:
            >>> cache = MemoryCache()
            >>> cache.set("key1", "value1")
            >>> cache.set("key2", "value2")
            >>> cache.clear()
            >>> cache.get("key1")
            None
            >>> cache.get("key2")
            None
        """
        self._cache.clear()

    def contains(self, key: str) -> bool:
        """
        Check if a key exists in the cache.

        Args:
            key: The cache key to check.

        Returns:
            bool: True if the key exists in the cache, False otherwise.

        Example:
            >>> cache = MemoryCache()
            >>> cache.set("key", "value")
            >>> cache.contains("key")
            True
            >>> cache.contains("nonexistent")
            False
        """
        return key in self._cache

    def get_hits(self) -> int:
        """
        Get the number of cache hits.

        Returns:
            int: The number of cache hits.
        """
        return self._hits

    def reset_hits(self) -> None:
        """
        Reset the cache hit counter.
        """
        self._hits = 0
