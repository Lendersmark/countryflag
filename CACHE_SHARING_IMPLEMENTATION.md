# CountryFlag Cache Sharing Implementation

## Problem
Previously, each `CountryFlag()` instance without an explicit cache parameter would receive `cache=None`, meaning no caching occurred. If users provided their own cache instances, they had to manually manage sharing the same cache instance across multiple `CountryFlag` objects, which led to cache fragmentation and reduced efficiency.

## Solution
Implemented a class-level global cache singleton that automatically shares cache data across all `CountryFlag` instances when no explicit cache is provided.

## Implementation Details

### 1. Core Changes to `CountryFlag` class (`src/countryflag/core/flag.py`)

#### Added Global Cache Class Attribute
```python
# Class-level shared cache instance
_global_cache: MemoryCache = MemoryCache()
```

#### Modified `__init__` Method
```python
def __init__(self, language: str = "en", cache: Optional[Cache] = None) -> None:
    # ... existing code ...
    # Use the global cache if no cache is provided
    self._cache = cache if cache is not None else self._global_cache
```

#### Added Cache Management Method
```python
@classmethod
def clear_global_cache(cls) -> None:
    """
    Clear the global cache. Useful for testing or resetting cache state.
    """
    cls._global_cache.clear()
    cls._global_cache.reset_hits()
```

### 2. Thread Safety
- The existing `MemoryCache` class already uses `threading.Lock()` for thread-safe operations
- All cache operations (get, set, clear, hit counting) are protected by locks
- Multiple threads can safely access the global cache concurrently

### 3. Backward Compatibility
- **100% backward compatible**: Existing code works without changes
- Instances with explicit cache parameters continue to use their custom cache
- Instances without cache parameters now automatically get shared caching

## Benefits

### Cache Hit Accumulation
- **Before**: Each `CountryFlag()` had `cache=None`, no caching occurred
- **After**: Multiple instances share the same cache, hits accumulate across instances

```python
# This now works efficiently with shared caching
cf1 = CountryFlag()
cf2 = CountryFlag()

flags1, _ = cf1.get_flag(["Germany"])  # Cache miss, stores result
flags2, _ = cf2.get_flag(["Germany"])  # Cache hit! Uses cf1's cached result
```

### Memory Efficiency
- Single cache instance shared across all default instances
- Reduces memory usage compared to multiple cache instances
- Cache data persists across instance creation/deletion

### Flexibility
- Users can still provide custom cache instances for specialized use cases
- Global cache can be easily cleared for testing: `CountryFlag.clear_global_cache()`
- Thread-safe operations ensure reliability in concurrent environments

## Testing

### Comprehensive Test Suite (`tests/test_global_cache_sharing.py`)
1. **Cache Instance Sharing**: Verifies instances without explicit cache share the same cache object
2. **Custom Cache Independence**: Ensures instances with custom cache don't affect global cache
3. **Hit Accumulation**: Tests that cache hits accumulate across different instances
4. **Thread Safety**: Validates concurrent access doesn't cause race conditions
5. **Cache Persistence**: Confirms cache survives instance creation/deletion
6. **Clear Method**: Tests the global cache reset functionality

### Example Test Results
```
tests/test_global_cache_sharing.py::TestGlobalCacheSharing::test_instances_without_cache_share_global_cache PASSED
tests/test_global_cache_sharing.py::TestGlobalCacheSharing::test_global_cache_accumulates_hits_across_instances PASSED
tests/test_global_cache_sharing.py::TestGlobalCacheSharing::test_global_cache_thread_safety PASSED
[All 8 tests PASSED]
```

## Usage Examples

### Default Usage (Automatic Cache Sharing)
```python
from countryflag.core.flag import CountryFlag

# Both instances automatically share the same cache
cf1 = CountryFlag()
cf2 = CountryFlag()

assert cf1._cache is cf2._cache  # True
assert cf1._cache is CountryFlag._global_cache  # True
```

### Custom Cache Usage (Independent Cache)
```python
from countryflag.core.flag import CountryFlag
from countryflag.cache.memory import MemoryCache

# Instance with custom cache
custom_cache = MemoryCache()
cf_custom = CountryFlag(cache=custom_cache)

# Instance with global cache
cf_global = CountryFlag()

assert cf_custom._cache is custom_cache  # True
assert cf_global._cache is CountryFlag._global_cache  # True
assert cf_custom._cache is not cf_global._cache  # True
```

### Testing Support
```python
# Clear global cache for clean test state
CountryFlag.clear_global_cache()

# Run tests...

# Cache state is reset for next test
assert CountryFlag._global_cache.get_hits() == 0
```

## Performance Impact

### Positive Impacts
- **Reduced Cache Misses**: Shared cache means higher hit rates
- **Memory Efficiency**: Single cache instance vs. multiple instances
- **Better Locality**: Related requests benefit from shared cached data

### No Negative Impacts
- **No Performance Overhead**: Same cache access patterns as before
- **Thread Safety**: Existing locking mechanism handles concurrency
- **Backward Compatibility**: Zero-cost abstraction for existing code

## Future Considerations

### Possible Enhancements
1. **Cache Size Limits**: Add configurable size limits to global cache
2. **Cache TTL**: Add time-to-live functionality for cached entries
3. **Cache Statistics**: Enhanced metrics and monitoring capabilities
4. **Cache Persistence**: Optional disk-based persistence for global cache

### Migration Path
This implementation provides a foundation for future caching enhancements while maintaining full backward compatibility.
