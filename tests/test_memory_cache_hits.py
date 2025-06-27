"""
Unit tests for MemoryCache hit counter behavior.

This module contains tests specifically for verifying the hit counter
functionality of the MemoryCache implementation.
"""

import threading
import time
import unittest
from typing import List

from countryflag.cache.memory import MemoryCache


class TestMemoryCacheHits(unittest.TestCase):
    """Test cases for MemoryCache hit counter functionality."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.cache = MemoryCache()

    def test_initial_hits_is_zero(self):
        """Test that hit counter starts at zero."""
        self.assertEqual(self.cache.get_hits(), 0)

    def test_get_non_existent_key_does_not_increment_hits(self):
        """Test that getting a non-existent key does not increment hit counter."""
        # Initial state
        self.assertEqual(self.cache.get_hits(), 0)

        # Get non-existent key
        result = self.cache.get("non_existent_key")
        self.assertIsNone(result)

        # Hits should still be 0
        self.assertEqual(self.cache.get_hits(), 0)

    def test_set_does_not_change_hits(self):
        """Test that set operations do not change hit counter."""
        # Initial state
        self.assertEqual(self.cache.get_hits(), 0)

        # Set some values
        self.cache.set("key1", "value1")
        self.cache.set("key2", "value2")
        self.cache.set("key3", "value3")

        # Hits should still be 0
        self.assertEqual(self.cache.get_hits(), 0)

    def test_get_existing_key_increments_hits(self):
        """Test that getting an existing key increments hit counter."""
        # Set a value
        self.cache.set("test_key", "test_value")
        self.assertEqual(self.cache.get_hits(), 0)

        # Get the value
        result = self.cache.get("test_key")
        self.assertEqual(result, "test_value")
        self.assertEqual(self.cache.get_hits(), 1)

    def test_consecutive_gets_on_same_key_increment_hits(self):
        """Test that two consecutive get calls on the same key after a single set raise hits from 0 → 1 → 2."""
        # Set a value
        self.cache.set("test_key", "test_value")
        self.assertEqual(self.cache.get_hits(), 0)

        # First get - hits should go from 0 to 1
        result1 = self.cache.get("test_key")
        self.assertEqual(result1, "test_value")
        self.assertEqual(self.cache.get_hits(), 1)

        # Second get - hits should go from 1 to 2
        result2 = self.cache.get("test_key")
        self.assertEqual(result2, "test_value")
        self.assertEqual(self.cache.get_hits(), 2)

    def test_get_different_keys_increments_hits(self):
        """Test that getting different existing keys increments hit counter."""
        # Set multiple values
        self.cache.set("key1", "value1")
        self.cache.set("key2", "value2")
        self.cache.set("key3", "value3")
        self.assertEqual(self.cache.get_hits(), 0)

        # Get each value
        self.assertEqual(self.cache.get("key1"), "value1")
        self.assertEqual(self.cache.get_hits(), 1)

        self.assertEqual(self.cache.get("key2"), "value2")
        self.assertEqual(self.cache.get_hits(), 2)

        self.assertEqual(self.cache.get("key3"), "value3")
        self.assertEqual(self.cache.get_hits(), 3)

    def test_mixed_existing_and_non_existing_gets(self):
        """Test hit counter with mixed existing and non-existing key gets."""
        # Set one value
        self.cache.set("existing_key", "value")
        self.assertEqual(self.cache.get_hits(), 0)

        # Get non-existing key - should not increment
        self.assertIsNone(self.cache.get("non_existing"))
        self.assertEqual(self.cache.get_hits(), 0)

        # Get existing key - should increment
        self.assertEqual(self.cache.get("existing_key"), "value")
        self.assertEqual(self.cache.get_hits(), 1)

        # Get non-existing key again - should not increment
        self.assertIsNone(self.cache.get("another_non_existing"))
        self.assertEqual(self.cache.get_hits(), 1)

        # Get existing key again - should increment
        self.assertEqual(self.cache.get("existing_key"), "value")
        self.assertEqual(self.cache.get_hits(), 2)

    def test_get_with_none_value_increments_hits(self):
        """Test that getting a key with None value increments hit counter."""
        # Set None as a value
        self.cache.set("none_key", None)
        self.assertEqual(self.cache.get_hits(), 0)

        # Get the None value - this should NOT increment hits
        # because the get method checks for "value is not None"
        result = self.cache.get("none_key")
        self.assertIsNone(result)
        self.assertEqual(self.cache.get_hits(), 0)

    def test_reset_hits(self):
        """Test that reset_hits resets the counter to zero."""
        # Set and get some values to increment hits
        self.cache.set("key1", "value1")
        self.cache.set("key2", "value2")
        self.cache.get("key1")
        self.cache.get("key2")
        self.cache.get("key1")

        # Verify hits are greater than 0
        self.assertGreater(self.cache.get_hits(), 0)

        # Reset hits
        self.cache.reset_hits()
        self.assertEqual(self.cache.get_hits(), 0)

    def test_delete_does_not_affect_hits(self):
        """Test that delete operations do not affect hit counter."""
        # Set and get a value
        self.cache.set("test_key", "test_value")
        self.cache.get("test_key")
        self.assertEqual(self.cache.get_hits(), 1)

        # Delete the key
        self.cache.delete("test_key")

        # Hits should remain the same
        self.assertEqual(self.cache.get_hits(), 1)

    def test_clear_does_not_affect_hits(self):
        """Test that clear operation does not affect hit counter."""
        # Set and get some values
        self.cache.set("key1", "value1")
        self.cache.set("key2", "value2")
        self.cache.get("key1")
        self.cache.get("key2")
        self.assertEqual(self.cache.get_hits(), 2)

        # Clear the cache
        self.cache.clear()

        # Hits should remain the same
        self.assertEqual(self.cache.get_hits(), 2)

    def test_thread_safety_of_hit_counter(self):
        """Test that hit counter is thread-safe."""
        # Set a value
        self.cache.set("thread_test_key", "thread_test_value")

        # List to collect results from threads
        results: List[int] = []

        def get_and_record_hits():
            """Get a value and record the hit count."""
            self.cache.get("thread_test_key")
            results.append(self.cache.get_hits())

        # Create and start multiple threads
        threads = []
        num_threads = 10
        for _ in range(num_threads):
            thread = threading.Thread(target=get_and_record_hits)
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Verify final hit count
        final_hits = self.cache.get_hits()
        self.assertEqual(final_hits, num_threads)

        # Verify that all recorded hits are unique and sequential
        # (this tests that the locking works correctly)
        self.assertEqual(len(results), num_threads)
        self.assertEqual(len(set(results)), num_threads)  # All results should be unique
        self.assertEqual(sorted(results), list(range(1, num_threads + 1)))

    def test_concurrent_set_and_get_operations(self):
        """Test concurrent set and get operations with hit counter."""
        results: List[int] = []

        def set_and_get_operations(thread_id: int):
            """Perform set and get operations."""
            key = f"thread_{thread_id}_key"
            value = f"thread_{thread_id}_value"

            # Set a value (should not affect hits)
            self.cache.set(key, value)

            # Get the value (should increment hits)
            retrieved_value = self.cache.get(key)
            if retrieved_value == value:
                results.append(self.cache.get_hits())

        # Create and start multiple threads
        threads = []
        num_threads = 5
        for i in range(num_threads):
            thread = threading.Thread(target=set_and_get_operations, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Verify that we got the expected number of hits
        final_hits = self.cache.get_hits()
        self.assertEqual(final_hits, num_threads)
        self.assertEqual(len(results), num_threads)


if __name__ == "__main__":
    unittest.main()
