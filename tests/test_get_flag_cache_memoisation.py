"""
Test to verify caching/memoisation behavior for repeated get_flag calls.

This module tests Step 8 of the plan: ensuring that repeated `get_flag("FR")` calls
are served from an internal cache (memoisation) and the second call doesn't
re-invoke the underlying loader.
"""

import unittest
from unittest.mock import MagicMock, patch

from countryflag import getflag
from countryflag.cache.memory import MemoryCache
from countryflag.core.flag import CountryFlag


class TestGetFlagCacheMemoisation(unittest.TestCase):
    """Test cases for get_flag caching and memoisation behavior."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Clear any existing global cache to ensure clean state
        CountryFlag.clear_global_cache()

    def test_getflag_uses_cache_for_repeated_calls(self):
        """Test that repeated getflag("FR") calls use internal caching."""
        # Test with the convenience function getflag()
        # Call 1: Should populate cache
        result1 = getflag("FR")

        # Call 2: Should be served from cache
        result2 = getflag("FR")

        # Both calls should return the same result
        self.assertEqual(result1, result2)
        self.assertEqual(result1, "🇫🇷")  # Verify it's the French flag

        # Verify results are strings (not None or other types)
        self.assertIsInstance(result1, str)
        self.assertIsInstance(result2, str)

    def test_countryFlag_get_flag_uses_cache_with_hit_counter(self):
        """Test that CountryFlag.get_flag uses cache and increments hit counter."""
        # Create a CountryFlag instance (will use the global cache)
        cf = CountryFlag()

        # Verify initial cache state
        initial_hits = cf._cache.get_hits()
        self.assertEqual(initial_hits, 0)

        # Call 1: Should populate cache
        flags1, pairs1 = cf.get_flag(["FR"])

        # Verify first call results
        self.assertEqual(flags1, "🇫🇷")
        self.assertEqual(len(pairs1), 1)
        self.assertEqual(pairs1[0], ("FR", "🇫🇷"))

        # Hit counter should still be 0 (cache miss, then cache set)
        hits_after_first_call = cf._cache.get_hits()
        self.assertEqual(hits_after_first_call, 0)

        # Call 2: Should be served from cache
        flags2, pairs2 = cf.get_flag(["FR"])

        # Verify second call results match first call
        self.assertEqual(flags2, flags1)
        self.assertEqual(pairs2, pairs1)

        # Hit counter should now be 1 (cache hit)
        hits_after_second_call = cf._cache.get_hits()
        self.assertEqual(hits_after_second_call, 1)

    def test_same_object_returned_from_cache(self):
        """Test that the exact same object is returned from cache."""
        cf = CountryFlag()

        # Call 1: Populate cache
        flags1, pairs1 = cf.get_flag(["FR"])

        # Call 2: Should return cached result
        flags2, pairs2 = cf.get_flag(["FR"])

        # The string content should be identical
        self.assertEqual(flags1, flags2)
        self.assertEqual(pairs1, pairs2)

        # For the pairs list, the tuples should be equal
        self.assertEqual(pairs1[0], pairs2[0])

        # Verify cache hit occurred
        self.assertEqual(cf._cache.get_hits(), 1)

    def test_underlying_converter_not_reinvoked_on_cache_hit(self):
        """Test that the underlying converter is not re-invoked when cache hits."""
        cf = CountryFlag()

        # Patch the converter's convert method to track calls
        with patch.object(
            cf._converter, "convert", wraps=cf._converter.convert
        ) as mock_convert:
            # Call 1: Should invoke converter
            flags1, pairs1 = cf.get_flag(["FR"])

            # Verify converter was called
            self.assertEqual(mock_convert.call_count, 1)
            mock_convert.assert_called_with("FR")

            # Call 2: Should be served from cache, not invoke converter again
            flags2, pairs2 = cf.get_flag(["FR"])

            # Verify converter was NOT called again (still 1 call total)
            self.assertEqual(mock_convert.call_count, 1)

            # Verify results are identical
            self.assertEqual(flags1, flags2)
            self.assertEqual(pairs1, pairs2)

            # Verify cache hit occurred
            self.assertEqual(cf._cache.get_hits(), 1)

    def test_cache_sharing_across_instances(self):
        """Test that cache is shared across CountryFlag instances by default."""
        # Create first instance
        cf1 = CountryFlag()

        # Call get_flag on first instance to populate cache
        flags1, pairs1 = cf1.get_flag(["FR"])
        self.assertEqual(cf1._cache.get_hits(), 0)  # Cache miss, then set

        # Create second instance (should share the same global cache)
        cf2 = CountryFlag()

        # Both instances should share the same cache object
        self.assertIs(cf1._cache, cf2._cache)

        # Call get_flag on second instance - should hit cache
        flags2, pairs2 = cf2.get_flag(["FR"])

        # Results should be identical
        self.assertEqual(flags1, flags2)
        self.assertEqual(pairs1, pairs2)

        # Cache hit should be recorded in shared cache
        self.assertEqual(cf1._cache.get_hits(), 1)
        self.assertEqual(cf2._cache.get_hits(), 1)  # Same cache object

    def test_cache_with_custom_cache_instance(self):
        """Test caching behavior with a custom cache instance."""
        # Create a custom cache instance
        custom_cache = MemoryCache()
        cf = CountryFlag(cache=custom_cache)

        # Verify custom cache is being used
        self.assertIs(cf._cache, custom_cache)
        self.assertIsNot(cf._cache, CountryFlag._global_cache)

        # Test caching behavior with custom cache
        initial_hits = custom_cache.get_hits()
        self.assertEqual(initial_hits, 0)

        # First call
        flags1, pairs1 = cf.get_flag(["FR"])
        self.assertEqual(custom_cache.get_hits(), 0)  # Cache miss

        # Second call - should hit custom cache
        flags2, pairs2 = cf.get_flag(["FR"])
        self.assertEqual(custom_cache.get_hits(), 1)  # Cache hit

        # Results should be identical
        self.assertEqual(flags1, flags2)
        self.assertEqual(pairs1, pairs2)

    def test_multiple_calls_increment_hit_counter(self):
        """Test that multiple cache hits increment the hit counter correctly."""
        cf = CountryFlag()

        # First call: populate cache
        cf.get_flag(["FR"])
        self.assertEqual(cf._cache.get_hits(), 0)

        # Multiple subsequent calls: should all hit cache
        for i in range(1, 6):  # Calls 2-6
            cf.get_flag(["FR"])
            self.assertEqual(cf._cache.get_hits(), i)

    def test_cache_key_deterministic_for_same_input(self):
        """Test that cache keys are deterministic for the same input."""
        cf = CountryFlag()

        # Make cache key method accessible for testing
        key1 = cf._make_key(["FR"], " ")
        key2 = cf._make_key(["FR"], " ")

        # Keys should be identical for same input
        self.assertEqual(key1, key2)

        # Call get_flag twice with same input
        cf.get_flag(["FR"])  # Populate cache
        cf.get_flag(["FR"])  # Should hit cache

        # Verify cache hit occurred
        self.assertEqual(cf._cache.get_hits(), 1)


if __name__ == "__main__":
    unittest.main()
