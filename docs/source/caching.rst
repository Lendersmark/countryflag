Caching System
============

CountryFlag includes a robust caching system to improve performance when working with repeated country name lookups.

Built-in Cache Types
------------------

Memory Cache
~~~~~~~~~~

The simplest and fastest caching option, storing data in memory:

.. code-block:: python

   from countryflag.core import CountryFlag
   from countryflag.cache import MemoryCache

   # Create a memory cache
   cache = MemoryCache()
   
   # Create a CountryFlag instance with caching
   cf = CountryFlag(cache=cache)
   
   # First call (cache miss)
   flags1 = cf.get_flag(["United States", "Canada"])
   
   # Second call (cache hit - much faster)
   flags2 = cf.get_flag(["United States", "Canada"])

Disk Cache
~~~~~~~~

Persistent caching that survives program restarts:

.. code-block:: python

   from countryflag.cache import DiskCache

   # Create a disk cache
   cache = DiskCache("/path/to/cache/dir")
   
   # Use it with CountryFlag
   cf = CountryFlag(cache=cache)

Redis Cache
~~~~~~~~~

For distributed systems, use the Redis cache plugin:

.. code-block:: python

   from countryflag.plugins.redis_cache import RedisCache

   # Create a Redis cache
   cache = RedisCache(host="localhost", port=6379)
   
   # Use it with CountryFlag
   cf = CountryFlag(cache=cache)

Cache Configuration
----------------

Common configuration options:

.. code-block:: python

   # Memory cache with size limit
   cache = MemoryCache(max_size=1000)

   # Disk cache with TTL
   cache = DiskCache(
       cache_dir="/path/to/cache",
       ttl=3600  # 1 hour
   )

   # Redis cache with custom configuration
   cache = RedisCache(
       host="localhost",
       port=6379,
       db=0,
       password="optional_password",
       ttl=3600
   )

Creating Custom Caches
-------------------

You can create custom cache implementations by extending the base Cache class:

.. code-block:: python

   from countryflag.cache.base import Cache
   from typing import Optional, Any

   class CustomCache(Cache):
       def get(self, key: str) -> Optional[Any]:
           # Implementation
           pass

       def set(self, key: str, value: Any) -> None:
           # Implementation
           pass

       def delete(self, key: str) -> None:
           # Implementation
           pass

       def clear(self) -> None:
           # Implementation
           pass

       def contains(self, key: str) -> bool:
           # Implementation
           pass

Cache Performance
--------------

Benchmarking results for different cache types:

+-------------+------------+-------------+--------------+
| Operation   | No Cache   | Memory Cache| Disk Cache   |
+=============+============+=============+==============+
| First Call  | 100ms      | 100ms       | 100ms        |
+-------------+------------+-------------+--------------+
| Second Call | 100ms      | 1ms         | 10ms         |
+-------------+------------+-------------+--------------+

Best Practices
------------

1. **Choose the Right Cache**:
   - Use MemoryCache for single-process applications
   - Use DiskCache for persistence between runs
   - Use RedisCache for distributed systems

2. **Configure Cache Size**:
   - Set appropriate size limits
   - Monitor cache usage
   - Implement cache eviction policies

3. **Handle Cache Failures**:
   - Implement fallback mechanisms
   - Log cache errors
   - Monitor cache performance

4. **Cache Invalidation**:
   - Implement clear cache policies
   - Use TTL for time-sensitive data
   - Provide cache clearing mechanisms

API Reference
-----------

.. automodule:: countryflag.cache.base
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: countryflag.cache.memory
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: countryflag.cache.disk
   :members:
   :undoc-members:
   :show-inheritance:

