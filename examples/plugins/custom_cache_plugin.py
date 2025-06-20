#!/usr/bin/env python3
"""
Example of a custom cache plugin for countryflag.

This plugin implements a Redis-based cache for countryflag.
"""

import json
import pickle
from typing import Any, Optional

try:
    import redis
except ImportError:
    redis = None

from countryflag.cache.base import Cache


class RedisCache(Cache):
    """
    Redis-based cache implementation.
    
    This class implements a cache that stores data in Redis.
    
    Attributes:
        _redis: Redis client.
        _prefix: Prefix for Redis keys.
        _ttl: Time-to-live for cache entries (in seconds).
    """
    
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0, 
                 prefix: str = "countryflag:", ttl: int = 3600):
        """
        Initialize the Redis cache.
        
        Args:
            host: Redis host.
            port: Redis port.
            db: Redis database number.
            prefix: Prefix for Redis keys.
            ttl: Time-to-live for cache entries (in seconds).
            
        Raises:
            ImportError: If Redis is not installed.
        """
        if redis is None:
            raise ImportError("Redis is not installed. Install it with 'pip install redis'.")
        
        self._redis = redis.Redis(host=host, port=port, db=db)
        self._prefix = prefix
        self._ttl = ttl
    
    def _get_key(self, key: str) -> str:
        """
        Get the full Redis key with prefix.
        
        Args:
            key: The cache key.
            
        Returns:
            str: The full Redis key.
        """
        return f"{self._prefix}{key}"
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from the cache.
        
        Args:
            key: The cache key.
            
        Returns:
            The cached value, or None if the key is not in the cache.
        """
        redis_key = self._get_key(key)
        value = self._redis.get(redis_key)
        
        if value is None:
            return None
        
        try:
            # Try to deserialize with pickle
            return pickle.loads(value)
        except (pickle.PickleError, TypeError, ValueError):
            # Fall back to JSON
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                # Return as string
                return value.decode('utf-8')
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a value in the cache.
        
        Args:
            key: The cache key.
            value: The value to cache.
        """
        redis_key = self._get_key(key)
        
        try:
            # Try to serialize with pickle
            serialized = pickle.dumps(value)
        except (pickle.PickleError, TypeError):
            # Fall back to JSON
            try:
                serialized = json.dumps(value).encode('utf-8')
            except (TypeError, ValueError):
                # Fall back to string
                serialized = str(value).encode('utf-8')
        
        self._redis.set(redis_key, serialized, ex=self._ttl)
    
    def delete(self, key: str) -> None:
        """
        Delete a value from the cache.
        
        Args:
            key: The cache key to delete.
        """
        redis_key = self._get_key(key)
        self._redis.delete(redis_key)
    
    def clear(self) -> None:
        """
        Clear all values from the cache.
        """
        # Get all keys with the prefix
        pattern = f"{self._prefix}*"
        keys = self._redis.keys(pattern)
        
        # Delete all keys
        if keys:
            self._redis.delete(*keys)
    
    def contains(self, key: str) -> bool:
        """
        Check if a key exists in the cache.
        
        Args:
            key: The cache key to check.
            
        Returns:
            bool: True if the key exists in the cache, False otherwise.
        """
        redis_key = self._get_key(key)
        return self._redis.exists(redis_key) > 0


def example_usage():
    """Example usage of the Redis cache plugin."""
    if redis is None:
        print("Redis is not installed. Install it with 'pip install redis'.")
        return
    
    try:
        # Create the Redis cache
        redis_cache = RedisCache()
        
        # Use the cache with CountryFlag
        from countryflag.core import CountryFlag
        cf = CountryFlag(cache=redis_cache)
        
        # First request (cache miss)
        import time
        start_time = time.time()
        flags1, _ = cf.get_flag(["United States", "Canada", "Germany"])
        miss_time = time.time() - start_time
        
        # Second request (cache hit)
        start_time = time.time()
        flags2, _ = cf.get_flag(["United States", "Canada", "Germany"])
        hit_time = time.time() - start_time
        
        # Print results
        print("Flags:", flags1)
        print(f"Cache miss time: {miss_time:.6f} seconds")
        print(f"Cache hit time: {hit_time:.6f} seconds")
        print(f"Speed improvement: {miss_time / hit_time:.2f}x")
        
        # Clean up
        redis_cache.clear()
        
    except redis.ConnectionError:
        print("Could not connect to Redis. Make sure Redis is running.")


if __name__ == "__main__":
    example_usage()
