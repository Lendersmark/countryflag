"""
Disk-based cache implementation for the countryflag package.

This module contains the DiskCache class, which implements on-disk caching.
"""

import hashlib
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

from countryflag.cache.base import Cache
from countryflag.core.exceptions import CacheError

# Configure logging
logger = logging.getLogger("countryflag.cache.disk")


class DiskCache(Cache):
    """
    Disk-based cache implementation.

    This class implements an on-disk cache using JSON files.

    Attributes:
        _cache_dir: Path to the cache directory.
        _index: Dictionary that maps cache keys to filenames.
    """

    def __init__(self, cache_dir: str) -> None:
        """
        Initialize the disk cache.

        Args:
            cache_dir: Path to the cache directory.

        Raises:
            CacheError: If the cache directory cannot be created.
        """
        self._cache_dir = Path(cache_dir)
        self._index: Dict[str, str] = {}
        self._hits = 0  # Initialize hit counter

        # Create the cache directory if it doesn't exist
        try:
            os.makedirs(self._cache_dir, exist_ok=True)

            # Load the index file if it exists
            index_path = self._cache_dir / "index.json"
            if index_path.exists():
                with open(index_path, encoding="utf-8") as f:
                    self._index = json.load(f)
        except Exception as e:
            logger.error(f"Error initializing disk cache: {e}")
            raise CacheError(f"Error initializing disk cache: {e}")

    def _get_cache_path(self, key: str) -> Path:
        """
        Get the path to the cache file for a key.

        Args:
            key: The cache key.

        Returns:
            Path: The path to the cache file.
        """
        # Use a hash of the key as the filename to avoid invalid characters
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return self._cache_dir / f"{key_hash}.json"

    def _save_index(self) -> None:
        """
        Save the index to disk.

        Raises:
            CacheError: If the index file cannot be written.
        """
        try:
            index_path = self._cache_dir / "index.json"
            with open(index_path, "w", encoding="utf-8") as f:
                json.dump(self._index, f)
        except Exception as e:
            logger.error(f"Error saving cache index: {e}")
            raise CacheError(f"Error saving cache index: {e}")

    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from the cache.

        Args:
            key: The cache key.

        Returns:
            The cached value, or None if the key is not in the cache.

        Raises:
            CacheError: If the cache file cannot be read.

        Example:
            >>> cache = DiskCache("/tmp/countryflag_cache")
            >>> cache.set("key", "value")
            >>> cache.get("key")
            'value'
            >>> cache.get("nonexistent")
            None
        """
        if key not in self._index:
            return None

        cache_path = self._get_cache_path(key)
        if not cache_path.exists():
            # The file doesn't exist, so remove the key from the index
            del self._index[key]
            self._save_index()
            return None

        try:
            with open(cache_path, encoding="utf-8") as f:
                self._hits += 1  # Increment hit counter
                return json.load(f)
        except Exception as e:
            logger.error(f"Error reading cache file for key '{key}': {e}")
            raise CacheError(f"Error reading cache file for key '{key}': {e}", key)

    def set(self, key: str, value: Any) -> None:
        """
        Set a value in the cache.

        Args:
            key: The cache key.
            value: The value to cache.

        Raises:
            CacheError: If the cache file cannot be written.

        Example:
            >>> cache = DiskCache("/tmp/countryflag_cache")
            >>> cache.set("key", "value")
            >>> cache.get("key")
            'value'
        """
        cache_path = self._get_cache_path(key)

        try:
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(value, f)

            # Update the index
            self._index[key] = cache_path.name
            self._save_index()
        except Exception as e:
            logger.error(f"Error writing cache file for key '{key}': {e}")
            raise CacheError(f"Error writing cache file for key '{key}': {e}", key)

    def delete(self, key: str) -> None:
        """
        Delete a value from the cache.

        Args:
            key: The cache key to delete.

        Example:
            >>> cache = DiskCache("/tmp/countryflag_cache")
            >>> cache.set("key", "value")
            >>> cache.delete("key")
            >>> cache.get("key")
            None
        """
        if key not in self._index:
            return

        cache_path = self._get_cache_path(key)
        if cache_path.exists():
            try:
                os.remove(cache_path)
            except Exception as e:
                logger.error(f"Error deleting cache file for key '{key}': {e}")

        # Update the index
        del self._index[key]
        self._save_index()

    def clear(self) -> None:
        """
        Clear all values from the cache.

        Example:
            >>> cache = DiskCache("/tmp/countryflag_cache")
            >>> cache.set("key1", "value1")
            >>> cache.set("key2", "value2")
            >>> cache.clear()
            >>> cache.get("key1")
            None
            >>> cache.get("key2")
            None
        """
        for key in list(self._index.keys()):
            self.delete(key)
        self._hits = 0  # Reset hit counter

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

    def contains(self, key: str) -> bool:
        """
        Check if a key exists in the cache.

        Args:
            key: The cache key to check.

        Returns:
            bool: True if the key exists in the cache, False otherwise.

        Example:
            >>> cache = DiskCache("/tmp/countryflag_cache")
            >>> cache.set("key", "value")
            >>> cache.contains("key")
            True
            >>> cache.contains("nonexistent")
            False
        """
        if key not in self._index:
            return False

        cache_path = self._get_cache_path(key)
        return cache_path.exists()
