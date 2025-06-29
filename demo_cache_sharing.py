#!/usr/bin/env python3
"""
Demonstration of CountryFlag global cache sharing.

This script demonstrates how multiple CountryFlag instances share the same
global cache when no explicit cache is provided, while instances with
explicit cache parameters use their own cache.
"""

import sys
import os

# Add the src directory to Python path for local testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from countryflag.core.flag import CountryFlag
from countryflag.cache.memory import MemoryCache


def main():
    print("=== CountryFlag Global Cache Sharing Demo ===\n")

    # Clear any existing global cache state
    CountryFlag.clear_global_cache()

    print("1. Creating two CountryFlag instances without explicit cache:")
    cf1 = CountryFlag()
    cf2 = CountryFlag()

    print(f"   cf1._cache is cf2._cache: {cf1._cache is cf2._cache}")
    print(f"   Both use global cache: {cf1._cache is CountryFlag._global_cache}")
    print(f"   Initial global cache hits: {CountryFlag._global_cache.get_hits()}")
    print()

    print("2. Using cf1 to get flag for Germany:")
    flags1, pairs1 = cf1.get_flag(["Germany"])
    print(f"   Result: {flags1}")
    print(
        f"   Global cache hits after cf1 call: {CountryFlag._global_cache.get_hits()}"
    )
    print()

    print("3. Using cf2 to get flag for the same country (Germany):")
    flags2, pairs2 = cf2.get_flag(["Germany"])
    print(f"   Result: {flags2}")
    print(
        f"   Global cache hits after cf2 call: {CountryFlag._global_cache.get_hits()}"
    )
    print(f"   Results are identical: {flags1 == flags2}")
    print()

    print("4. Creating CountryFlag instance with custom cache:")
    custom_cache = MemoryCache()
    cf3 = CountryFlag(cache=custom_cache)

    print(f"   cf3 uses custom cache: {cf3._cache is custom_cache}")
    print(
        f"   cf3 cache is different from global: {cf3._cache is not CountryFlag._global_cache}"
    )
    print(f"   Custom cache hits: {custom_cache.get_hits()}")
    print()

    print("5. Using cf3 with custom cache to get flag for Germany:")
    flags3, pairs3 = cf3.get_flag(["Germany"])
    print(f"   Result: {flags3}")
    print(f"   Custom cache hits after cf3 call: {custom_cache.get_hits()}")
    print(f"   Global cache hits (unchanged): {CountryFlag._global_cache.get_hits()}")
    print()

    print("6. Testing cache persistence across instance creation:")
    print(
        f"   Global cache hits before deleting cf1, cf2: {CountryFlag._global_cache.get_hits()}"
    )

    # Delete instances
    del cf1, cf2

    # Create new instance
    cf4 = CountryFlag()
    print(f"   Created new instance cf4")
    print(
        f"   Global cache hits (should be same): {CountryFlag._global_cache.get_hits()}"
    )

    # Request same country again - should hit cache
    flags4, pairs4 = cf4.get_flag(["Germany"])
    print(f"   cf4 result for Germany: {flags4}")
    print(
        f"   Global cache hits after cf4 call: {CountryFlag._global_cache.get_hits()}"
    )
    print()

    print("7. Demonstrating clear_global_cache method:")
    print(f"   Global cache hits before clear: {CountryFlag._global_cache.get_hits()}")
    CountryFlag.clear_global_cache()
    print(f"   Global cache hits after clear: {CountryFlag._global_cache.get_hits()}")

    # Request again - should rebuild cache
    flags5, pairs5 = cf4.get_flag(["Germany"])
    print(f"   cf4 result after cache clear: {flags5}")
    print(f"   Global cache hits after rebuild: {CountryFlag._global_cache.get_hits()}")
    print()

    print("=== Demo Complete ===")
    print("\nKey Benefits:")
    print("✓ Automatic cache sharing between instances without explicit cache")
    print("✓ Independent caches when explicitly provided")
    print("✓ Thread-safe operations with proper locking")
    print("✓ Easy cache reset for testing via clear_global_cache()")
    print("✓ Backward compatibility - existing code works unchanged")


if __name__ == "__main__":
    main()
