"""
Step 8 Test: Call get_flag("FR") twice; assert that the second call is served from an internal cache.

This test ensures memoisation path is covered by verifying:
1. Two calls to get_flag("FR") return the same result
2. The second call is served from cache (cache hit counter increments)
3. The underlying loader is not re-invoked via mock verification
"""

import unittest
from unittest.mock import patch

from countryflag import getflag
from countryflag.core.flag import CountryFlag


class TestStep8GetFlagFRTwice(unittest.TestCase):
    """Step 8: Test that repeated get_flag("FR") calls use caching/memoisation."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Clear any existing global cache to ensure clean state
        CountryFlag.clear_global_cache()

    def test_get_flag_fr_twice_uses_cache(self):
        """
        Step 8: Call get_flag("FR") twice; assert that the second call is served from an internal cache.
        Ensures memoisation path is covered.
        """
        cf = CountryFlag()

        # Verify initial cache state - no hits
        initial_hits = cf._cache.get_hits()
        self.assertEqual(initial_hits, 0, "Cache should start with 0 hits")

        # FIRST CALL: get_flag("FR") - should populate cache
        flags1, pairs1 = cf.get_flag(["FR"])

        # Verify first call results
        self.assertEqual(flags1, "🇫🇷", "First call should return French flag")
        self.assertEqual(
            len(pairs1), 1, "First call should return one country-flag pair"
        )
        self.assertEqual(
            pairs1[0],
            ("FR", "🇫🇷"),
            "First call should return correct country-flag pair",
        )

        # After first call: cache miss (then cache set), so hits should still be 0
        hits_after_first_call = cf._cache.get_hits()
        self.assertEqual(
            hits_after_first_call, 0, "First call should be cache miss (0 hits)"
        )

        # SECOND CALL: get_flag("FR") - should be served from internal cache
        flags2, pairs2 = cf.get_flag(["FR"])

        # Verify second call results are identical to first call
        self.assertEqual(
            flags2, flags1, "Second call should return same flags as first call"
        )
        self.assertEqual(
            pairs2, pairs1, "Second call should return same pairs as first call"
        )
        self.assertEqual(flags2, "🇫🇷", "Second call should return French flag")
        self.assertEqual(
            pairs2[0],
            ("FR", "🇫🇷"),
            "Second call should return correct country-flag pair",
        )

        # After second call: cache hit, so hits should increment to 1
        hits_after_second_call = cf._cache.get_hits()
        self.assertEqual(
            hits_after_second_call, 1, "Second call should be cache hit (1 hit)"
        )

        # Verify that the second call was indeed served from cache
        self.assertGreater(
            hits_after_second_call,
            hits_after_first_call,
            "Second call should increment cache hit counter",
        )

    def test_underlying_loader_not_reinvoked_via_mock(self):
        """
        Verify that underlying loader (converter) is not re-invoked on second call using mock.
        Ensures memoisation path is covered by checking mock call count.
        """
        cf = CountryFlag()

        # Mock the converter's convert method to track invocations
        with patch.object(
            cf._converter, "convert", wraps=cf._converter.convert
        ) as mock_convert:

            # FIRST CALL: should invoke underlying converter
            flags1, pairs1 = cf.get_flag(["FR"])

            # Verify that converter was called exactly once
            self.assertEqual(
                mock_convert.call_count,
                1,
                "First call should invoke underlying converter once",
            )
            mock_convert.assert_called_with("FR")

            # Verify first call results
            self.assertEqual(flags1, "🇫🇷")
            self.assertEqual(pairs1[0], ("FR", "🇫🇷"))

            # SECOND CALL: should NOT invoke underlying converter (served from cache)
            flags2, pairs2 = cf.get_flag(["FR"])

            # Verify that converter was NOT called again (still only 1 total call)
            self.assertEqual(
                mock_convert.call_count,
                1,
                "Second call should NOT invoke underlying converter again",
            )

            # Verify second call results are identical
            self.assertEqual(flags2, flags1, "Second call should return same result")
            self.assertEqual(pairs2, pairs1, "Second call should return same pairs")

            # Verify cache hit occurred
            cache_hits = cf._cache.get_hits()
            self.assertEqual(
                cache_hits, 1, "Second call should be served from cache (1 hit)"
            )

    def test_getflag_convenience_function_also_uses_cache(self):
        """
        Test that the convenience getflag() function also benefits from caching.
        """
        # Clear global cache
        CountryFlag.clear_global_cache()

        # FIRST CALL using convenience function
        result1 = getflag("FR")
        initial_hits = CountryFlag._global_cache.get_hits()

        # SECOND CALL using convenience function
        result2 = getflag("FR")
        final_hits = CountryFlag._global_cache.get_hits()

        # Verify results are identical
        self.assertEqual(result1, result2, "Both calls should return same result")
        self.assertEqual(result1, "🇫🇷", "Both calls should return French flag")

        # Verify that second call hit the cache
        self.assertEqual(initial_hits, 0, "After first call, cache hits should be 0")
        self.assertEqual(final_hits, 1, "After second call, cache hits should be 1")
        self.assertGreater(
            final_hits, initial_hits, "Second call should increment cache hits"
        )


if __name__ == "__main__":
    unittest.main()
