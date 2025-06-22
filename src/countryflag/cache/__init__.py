"""
Caching functionality for the countryflag package.

This package contains the cache interface and implementations for different caching strategies.
"""

from countryflag.cache.base import Cache
from countryflag.cache.disk import DiskCache
from countryflag.cache.memory import MemoryCache

__all__ = [
    "Cache",
    "MemoryCache",
    "DiskCache",
]
