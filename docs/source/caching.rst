Caching System
==============
CountryFlag includes a robust caching system to improve performance when working with repeated country name lookups.

The caching system features automatic cache sharing, thread-safe operations, and intelligent key normalization for optimal performance.

Automatic Cache Sharing
-----------------------
Starting from version 1.0.1, CountryFlag automatically provides shared caching across instances when no explicit cache is provided.

.. code-block:: python

   from countryflag.core import CountryFlag

   # These instances automatically share the same cache
   cf1 = CountryFlag()
   cf2 = CountryFlag()
   
   # First call (cache miss)
   flags1, _ = cf1.get_flag(["Germany"])
   
   # Second call from different instance (cache hit!)
   flags2, _ = cf2.get_flag(["Germany"])  # Much faster
   
   # Verify cache sharing
   assert cf1._cache is cf2._cache  # True

This behavior provides significant performance improvements as cache data accumulates across the application lifecycle, while maintaining full backward compatibility.

Global Cache Management
~~~~~~~~~~~~~~~~~~~~~~~
The shared cache can be easily managed for testing or reset scenarios:

.. code-block:: python

   # Clear the global cache
   CountryFlag.clear_global_cache()
   
   # Check cache statistics
   hits = CountryFlag._global_cache.get_hits()
   print(f"Cache hits: {hits}")

Thread Safety
-------------
All cache operations in CountryFlag are thread-safe, using ``threading.Lock`` to ensure data integrity in concurrent environments.

.. code-block:: python

   import threading
   from countryflag.core import CountryFlag

   def worker():
       """Worker function for concurrent access."""
       cf = CountryFlag()
       flags, _ = cf.get_flag(["Germany", "France"])
       return flags

   # Create multiple threads
   threads = []
   for i in range(10):
       thread = threading.Thread(target=worker)
       threads.append(thread)
       thread.start()

   # Wait for completion
   for thread in threads:
       thread.join()

   print("All threads completed safely")

**Thread Safety Features:**

- All cache operations (get, set, delete, clear) are protected by locks
- Concurrent access to global cache is safe across multiple instances
- No data corruption or race conditions
- Performance optimized with fine-grained locking

Key Normalization
-----------------
CountryFlag uses intelligent key normalization to improve cache hit rates by creating deterministic cache keys regardless of input order.

.. code-block:: python

   cf = CountryFlag()

   # These two calls will use the same cache entry
   flags1, _ = cf.get_flag(["Germany", "France", "Italy"])
   flags2, _ = cf.get_flag(["Italy", "Germany", "France"])  # Cache hit!

   # The results are reordered to match input order
   # but the underlying cache key is normalized

**Key Normalization Benefits:**

- **Order Independence**: Same countries in different orders share cache entries
- **Higher Hit Rates**: Reduces cache misses due to input variations
- **Memory Efficiency**: Eliminates duplicate cache entries for equivalent requests
- **Intelligent Filtering**: Only valid string entries are used for key generation

**How It Works:**

1. Filter out invalid/empty entries from country list
2. Sort valid country names alphabetically
3. Create deterministic cache key with separator
4. Store result with normalized key
5. Reorder cached results to match current input order

Backward Compatibility and Migration
-------------------------------------

.. important::
   **Breaking Change in v1.0.1**: The caching behavior has changed for CountryFlag instances created without an explicit cache parameter.

**Before v1.0.1:**

.. code-block:: python

   # These instances had NO caching
   cf1 = CountryFlag()  # cache = None
   cf2 = CountryFlag()  # cache = None
   
   # Each call was computed from scratch
   flags1, _ = cf1.get_flag(["Germany"])  # No caching
   flags2, _ = cf2.get_flag(["Germany"])  # No caching

**From v1.0.1 onwards:**

.. code-block:: python

   # These instances automatically share a global cache
   cf1 = CountryFlag()  # cache = CountryFlag._global_cache
   cf2 = CountryFlag()  # cache = CountryFlag._global_cache
   
   # Cache data is shared between instances
   flags1, _ = cf1.get_flag(["Germany"])  # Cache miss, stores result
   flags2, _ = cf2.get_flag(["Germany"])  # Cache hit!

**Migration Guide:**

1. **No Code Changes Required**: Existing code will continue to work
2. **Performance Improvement**: Applications will automatically benefit from shared caching
3. **Custom Cache Users**: No changes needed - explicit cache parameters work as before
4. **Testing Code**: Use ``CountryFlag.clear_global_cache()`` to reset cache state between tests

**Disabling Global Cache** (if needed):

.. code-block:: python

   from countryflag.cache.base import NoOpCache
   
   # Create instance with no caching (similar to old behavior)
   cf = CountryFlag(cache=NoOpCache())

**Impact on Performance:**

- **Positive**: Significantly faster repeated operations
- **Memory**: Minimal increase due to singleton pattern
- **Thread Safety**: Enhanced with proper locking mechanisms

Built-in Cache Types
--------------------
Memory Cache
~~~~~~~~~~~~
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
~~~~~~~~~~
Persistent caching that survives program restarts:

.. code-block:: python

   from countryflag.cache import DiskCache

   # Create a disk cache
   cache = DiskCache("/path/to/cache/dir")

   # Use it with CountryFlag
   cf = CountryFlag(cache=cache)

Redis Cache
~~~~~~~~~~~
For distributed systems, use the Redis cache plugin:

.. code-block:: python

   from countryflag.plugins.redis_cache import RedisCache

   # Create a Redis cache
   cache = RedisCache(host="localhost", port=6379)

   # Use it with CountryFlag
   cf = CountryFlag(cache=cache)

Cache Configuration
-------------------
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
----------------------
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
-----------------
Benchmarking results for different cache types:

+-------------+------------+-------------+--------------+
| Operation   | No Cache   | Memory Cache| Disk Cache   |
+=============+============+=============+==============+
| First Call  | 100ms      | 100ms       | 100ms        |
+-------------+------------+-------------+--------------+
| Second Call | 100ms      | 1ms         | 10ms         |
+-------------+------------+-------------+--------------+

Best Practices
--------------
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
-------------
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
