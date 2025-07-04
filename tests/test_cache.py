"""
Comprehensive tests for cache implementations.

This module contains tests for both DiskCache and MemoryCache implementations,
including basic operations, TTL expiry, error handling, and concurrency scenarios.

Force CI refresh - no RuleBasedStateMachine import needed.
"""

import json
import os
import stat
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, List
from unittest.mock import Mock, patch

import pytest
from freezegun import freeze_time

from countryflag.cache.base import Cache
from countryflag.cache.disk import DiskCache
from countryflag.cache.memory import MemoryCache
from countryflag.core.exceptions import CacheError


class TTLCache:
    """
    TTL (Time To Live) wrapper for cache implementations.

    This wrapper adds TTL functionality to any cache implementation.
    """

    def __init__(self, cache: Cache, default_ttl: float = 300, time_func=None):
        """
        Initialize TTL cache wrapper.

        Args:
            cache: The underlying cache implementation
            default_ttl: Default TTL in seconds (300 = 5 minutes)
            time_func: Function to get current time (defaults to time.time)
        """
        self._cache = cache
        self._default_ttl = default_ttl
        self._expiry_times = {}
        self._lock = threading.RLock()
        self._time_func = time_func or time.time

    def _is_expired(self, key: str) -> bool:
        """Check if a key has expired."""
        if key not in self._expiry_times:
            return False
        return self._time_func() > self._expiry_times[key]

    def _cleanup_expired(self, key: str) -> None:
        """Remove expired key from cache and expiry times."""
        if self._is_expired(key):
            with self._lock:
                if key in self._expiry_times:
                    del self._expiry_times[key]
                self._cache.delete(key)

    def get(self, key: str) -> Any:
        """Get value from cache, checking TTL."""
        with self._lock:
            if self._is_expired(key):
                self._cleanup_expired(key)
                return None
            return self._cache.get(key)

    def set(self, key: str, value: Any, ttl: float = None) -> None:
        """Set value in cache with TTL."""
        ttl = ttl or self._default_ttl
        with self._lock:
            self._cache.set(key, value)
            self._expiry_times[key] = self._time_func() + ttl

    def delete(self, key: str) -> None:
        """Delete value from cache."""
        with self._lock:
            self._cache.delete(key)
            if key in self._expiry_times:
                del self._expiry_times[key]

    def clear(self) -> None:
        """Clear all values from cache."""
        with self._lock:
            self._cache.clear()
            self._expiry_times.clear()

    def contains(self, key: str) -> bool:
        """Check if key exists and is not expired."""
        with self._lock:
            if self._is_expired(key):
                self._cleanup_expired(key)
                return False
            return self._cache.contains(key)


class TestCacheBasicOperations:
    """Test basic cache operations for both DiskCache and MemoryCache."""

    @pytest.fixture(params=[MemoryCache, DiskCache])
    def cache_instance(self, request, tmp_path):
        """Parametrized fixture that provides both cache types."""
        if request.param == MemoryCache:
            return MemoryCache()
        else:
            return DiskCache(str(tmp_path / "test_cache"))

    def test_set_and_get(self, cache_instance):
        """Test basic set and get operations."""
        # Test string value
        cache_instance.set("key1", "value1")
        assert cache_instance.get("key1") == "value1"

        # Test numeric value
        cache_instance.set("key2", 42)
        assert cache_instance.get("key2") == 42

        # Test list value
        cache_instance.set("key3", [1, 2, 3])
        assert cache_instance.get("key3") == [1, 2, 3]

        # Test dict value
        cache_instance.set("key4", {"nested": "dict"})
        assert cache_instance.get("key4") == {"nested": "dict"}

        # Test None value
        cache_instance.set("key5", None)
        assert cache_instance.get("key5") is None

    def test_get_nonexistent_key(self, cache_instance):
        """Test getting a key that doesn\'t exist."""
        assert cache_instance.get("nonexistent") is None

    def test_delete(self, cache_instance):
        """Test delete operation."""
        # Set a value
        cache_instance.set("test_key", "test_value")
        assert cache_instance.get("test_key") == "test_value"

        # Delete the value
        cache_instance.delete("test_key")
        assert cache_instance.get("test_key") is None

        # Delete non-existent key should not raise error
        cache_instance.delete("nonexistent")

    def test_contains(self, cache_instance):
        """Test contains operation."""
        # Initially should not contain key
        assert not cache_instance.contains("test_key")

        # After setting, should contain key
        cache_instance.set("test_key", "test_value")
        assert cache_instance.contains("test_key")

        # After deleting, should not contain key
        cache_instance.delete("test_key")
        assert not cache_instance.contains("test_key")

    def test_clear(self, cache_instance):
        """Test clear operation."""
        # Set multiple values
        cache_instance.set("key1", "value1")
        cache_instance.set("key2", "value2")
        cache_instance.set("key3", "value3")

        # Verify they exist
        assert cache_instance.get("key1") == "value1"
        assert cache_instance.get("key2") == "value2"
        assert cache_instance.get("key3") == "value3"

        # Clear cache
        cache_instance.clear()

        # Verify all values are gone
        assert cache_instance.get("key1") is None
        assert cache_instance.get("key2") is None
        assert cache_instance.get("key3") is None

    def test_overwrite_key(self, cache_instance):
        """Test overwriting an existing key."""
        cache_instance.set("key", "original_value")
        assert cache_instance.get("key") == "original_value"

        cache_instance.set("key", "new_value")
        assert cache_instance.get("key") == "new_value"


class TestTTLFunctionality:
    """Test TTL (Time To Live) functionality."""

    @pytest.fixture(params=[MemoryCache, DiskCache])
    def ttl_cache(self, request, tmp_path):
        """Parametrized fixture that provides TTL cache with both cache types."""
        import time as time_module  # Import to access the mocked time.time

        if request.param == MemoryCache:
            base_cache = MemoryCache()
        else:
            base_cache = DiskCache(str(tmp_path / "test_ttl_cache"))
        return TTLCache(
            base_cache, default_ttl=1, time_func=time_module.time
        )  # 1 second TTL

    @freeze_time("2023-01-01 12:00:00")
    def test_ttl_expiry_with_freezegun(self, tmp_path):
        """Test TTL expiry using freezegun."""
        import time as time_module  # Import to access the mocked time.time

        # Create fresh TTL cache instances with mocked time for this test
        memory_ttl_cache = TTLCache(
            MemoryCache(), default_ttl=1, time_func=time_module.time
        )
        disk_ttl_cache = TTLCache(
            DiskCache(str(tmp_path / "test_ttl_freezegun")),
            default_ttl=1,
            time_func=time_module.time,
        )

        for cache_name, ttl_cache in [
            ("memory", memory_ttl_cache),
            ("disk", disk_ttl_cache),
        ]:
            # Set a value with 60 second TTL
            ttl_cache.set("frozen_key", "frozen_value", ttl=60)

            # Should be available immediately
            assert (
                ttl_cache.get("frozen_key") == "frozen_value"
            ), f"{cache_name} cache: immediate get failed"
            assert ttl_cache.contains(
                "frozen_key"
            ), f"{cache_name} cache: immediate contains failed"

            # Move time forward by 30 seconds - should still be valid
            with freeze_time("2023-01-01 12:00:30"):
                assert (
                    ttl_cache.get("frozen_key") == "frozen_value"
                ), f"{cache_name} cache: 30s get failed"
                assert ttl_cache.contains(
                    "frozen_key"
                ), f"{cache_name} cache: 30s contains failed"

            # Move time forward by 70 seconds - should be expired
            with freeze_time("2023-01-01 12:01:10"):
                assert (
                    ttl_cache.get("frozen_key") is None
                ), f"{cache_name} cache: 70s get should be None"
                assert not ttl_cache.contains(
                    "frozen_key"
                ), f"{cache_name} cache: 70s contains should be False"

            # Clean up for next iteration
            ttl_cache.clear()

    @freeze_time("2023-01-01 00:00:00")
    def test_default_ttl(self, ttl_cache):
        """Test default TTL behavior."""
        # Set without explicit TTL (should use default 1s)
        ttl_cache.set("default_ttl_key", "value")
        assert ttl_cache.get("default_ttl_key") == "value"

        # Jump to 100ms later - should still be valid
        with freeze_time("2023-01-01 00:00:00.100000"):
            assert ttl_cache.get("default_ttl_key") == "value"

    def test_ttl_delete_cleanup(self, ttl_cache):
        """Test that manual delete removes TTL tracking."""
        ttl_cache.set("delete_test", "value", ttl=10)
        assert ttl_cache.get("delete_test") == "value"

        # Manual delete
        ttl_cache.delete("delete_test")
        assert ttl_cache.get("delete_test") is None

        # Should be able to set again with different TTL
        ttl_cache.set("delete_test", "new_value", ttl=20)
        assert ttl_cache.get("delete_test") == "new_value"

    def test_ttl_clear_cleanup(self, ttl_cache):
        """Test that clear removes all TTL tracking."""
        ttl_cache.set("clear_test1", "value1", ttl=10)
        ttl_cache.set("clear_test2", "value2", ttl=20)

        assert ttl_cache.get("clear_test1") == "value1"
        assert ttl_cache.get("clear_test2") == "value2"

        # Clear all
        ttl_cache.clear()
        assert ttl_cache.get("clear_test1") is None
        assert ttl_cache.get("clear_test2") is None


class TestDiskCacheErrorHandling:
    """Test error handling for DiskCache."""

    def test_unwritable_cache_directory(self, tmp_path):
        """Test error handling when cache directory is not writable."""
        # Use a different approach that works on Windows
        # Create a cache directory inside a file (which will fail)
        blocking_file = tmp_path / "blocking_file.txt"
        blocking_file.write_text("content")

        # Try to create cache directory inside the file (impossible)
        cache_dir = blocking_file / "cache"

        # This should fail during initialization
        with pytest.raises(CacheError, match="Error initializing disk cache"):
            DiskCache(str(cache_dir))

    def test_corrupted_cache_file(self, tmp_path):
        """Test handling of corrupted cache files."""
        cache_dir = tmp_path / "corrupted_cache"
        cache = DiskCache(str(cache_dir))

        # Set a valid value first
        cache.set("test_key", "test_value")

        # Corrupt the cache file by writing invalid JSON
        cache_path = cache._get_cache_path("test_key")
        with open(cache_path, "w") as f:
            f.write("invalid json content {")

        # Getting the corrupted value should raise CacheError
        with pytest.raises(CacheError, match="Error reading cache file"):
            cache.get("test_key")

    def test_missing_cache_file_with_index_entry(self, tmp_path):
        """Test handling when index has entry but cache file is missing."""
        cache_dir = tmp_path / "missing_file_cache"
        cache = DiskCache(str(cache_dir))

        # Set a value
        cache.set("test_key", "test_value")
        assert cache.get("test_key") == "test_value"

        # Remove the cache file but keep the index
        cache_path = cache._get_cache_path("test_key")
        os.remove(cache_path)

        # Getting should return None and clean up the index
        assert cache.get("test_key") is None
        assert not cache.contains("test_key")

    def test_invalid_cache_directory_creation(self, tmp_path):
        """Test error when cache directory cannot be created."""
        # Try to create cache in a location that can't be created
        # Use a file as the "directory" path
        blocking_file = tmp_path / "blocking_file"
        blocking_file.write_text("content")

        invalid_cache_dir = blocking_file / "cache"  # Can't create dir inside file

        with pytest.raises(CacheError, match="Error initializing disk cache"):
            DiskCache(str(invalid_cache_dir))

    def test_index_file_write_error(self, tmp_path):
        """Test error handling when index file cannot be written."""
        cache_dir = tmp_path / "index_error_cache"

        # Create cache instance first without mocking
        cache = DiskCache(str(cache_dir))

        # Now mock _save_index to raise a CacheError only for the set operation
        with patch.object(
            cache,
            "_save_index",
            side_effect=CacheError("Error saving cache index: Permission denied"),
        ):
            # This should fail when trying to save the index
            with pytest.raises(CacheError, match="Error saving cache index"):
                cache.set("test_key", "test_value")


class TestConcurrency:
    """Test concurrent operations on caches."""

    @pytest.mark.parametrize(
        "cache_type,num_threads",
        [
            (MemoryCache, 5),
            (MemoryCache, 10),
            (DiskCache, 3),  # Fewer threads for disk cache due to I/O overhead
            (DiskCache, 5),
        ],
    )
    def test_concurrent_set_and_get(self, cache_type, num_threads, tmp_path):
        """Test concurrent set and get operations."""
        if cache_type == MemoryCache:
            cache = MemoryCache()
        else:
            cache = DiskCache(str(tmp_path / f"concurrent_cache_{num_threads}"))

        results = []
        errors = []

        def worker(thread_id):
            """Worker function that performs cache operations."""
            try:
                key = f"thread_{thread_id}_key"
                value = f"thread_{thread_id}_value"

                # Set value
                cache.set(key, value)

                # Get value
                retrieved = cache.get(key)
                if retrieved == value:
                    results.append((thread_id, "success"))
                else:
                    results.append((thread_id, f"mismatch: {retrieved}"))

                # Test contains
                if cache.contains(key):
                    results.append((thread_id, "contains_ok"))
                else:
                    results.append((thread_id, "contains_fail"))

            except Exception as e:
                errors.append((thread_id, str(e)))

        # Run workers concurrently
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(worker, i) for i in range(num_threads)]
            for future in futures:
                future.result()  # Wait for completion

        # Check results
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert len(results) == num_threads * 2  # Each thread should have 2 results

        success_count = sum(1 for _, result in results if result == "success")
        contains_ok_count = sum(1 for _, result in results if result == "contains_ok")

        assert success_count == num_threads
        assert contains_ok_count == num_threads

    @pytest.mark.parametrize("cache_type", [MemoryCache, DiskCache])
    def test_concurrent_delete_operations(self, cache_type, tmp_path):
        """Test concurrent delete operations."""
        if cache_type == MemoryCache:
            cache = MemoryCache()
        else:
            cache = DiskCache(str(tmp_path / "concurrent_delete_cache"))

        # Pre-populate cache
        keys = [f"key_{i}" for i in range(20)]
        for key in keys:
            cache.set(key, f"value_{key}")

        # Verify all keys exist
        for key in keys:
            assert cache.get(key) == f"value_{key}"

        delete_results = []

        def delete_worker(key):
            """Worker that deletes a specific key."""
            try:
                cache.delete(key)
                # Verify it's deleted
                if cache.get(key) is None:
                    delete_results.append("success")
                else:
                    delete_results.append("failed")
            except Exception as e:
                delete_results.append(f"error: {e}")

        # Delete keys concurrently
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(delete_worker, key) for key in keys]
            for future in futures:
                future.result()

        # Check all deletions were successful
        assert len(delete_results) == len(keys)
        assert all(result == "success" for result in delete_results)

        # Verify cache is empty
        for key in keys:
            assert cache.get(key) is None
            assert not cache.contains(key)

    def test_concurrent_ttl_operations(self, tmp_path):
        """Test concurrent operations with TTL cache."""
        base_cache = MemoryCache()
        ttl_cache = TTLCache(
            base_cache, default_ttl=3600
        )  # 1 hour TTL to avoid expiry issues

        results = []
        errors = []

        def ttl_worker(thread_id):
            """Worker that performs TTL cache operations."""
            key = f"ttl_key_{thread_id}"
            value = f"ttl_value_{thread_id}"

            try:
                # Set with long TTL to avoid timing issues
                ttl_cache.set(key, value, ttl=3600)  # 1 hour TTL

                # Immediate get should work
                retrieved = ttl_cache.get(key)
                if retrieved == value:
                    results.append("set_get_ok")
                else:
                    results.append(f"set_get_fail: expected {value}, got {retrieved}")

                # Test contains
                if ttl_cache.contains(key):
                    results.append("contains_ok")
                else:
                    results.append("contains_fail")

                # Test delete
                ttl_cache.delete(key)
                if ttl_cache.get(key) is None and not ttl_cache.contains(key):
                    results.append("delete_ok")
                else:
                    results.append("delete_fail")

            except Exception as e:
                errors.append(f"thread_{thread_id}: {e}")

        # Run TTL workers concurrently
        num_workers = 5
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = [executor.submit(ttl_worker, i) for i in range(num_workers)]
            for future in futures:
                future.result()

        # Check for errors
        assert len(errors) == 0, f"Errors occurred: {errors}"

        # Check results
        set_get_ok_count = sum(1 for r in results if r == "set_get_ok")
        contains_ok_count = sum(1 for r in results if r == "contains_ok")
        delete_ok_count = sum(1 for r in results if r == "delete_ok")

        assert (
            set_get_ok_count == num_workers
        ), f"Expected {num_workers} successful set/get, got {set_get_ok_count}. Results: {results}"
        assert (
            contains_ok_count == num_workers
        ), f"Expected {num_workers} successful contains, got {contains_ok_count}. Results: {results}"
        assert (
            delete_ok_count == num_workers
        ), f"Expected {num_workers} successful deletes, got {delete_ok_count}. Results: {results}"

    def test_memory_cache_thread_safety(self):
        """Test thread safety of MemoryCache hit counter and operations."""
        cache = MemoryCache()

        # Pre-populate some keys
        for i in range(10):
            cache.set(f"shared_key_{i}", f"shared_value_{i}")

        results = []

        def concurrent_operations(thread_id):
            """Perform various operations concurrently."""
            try:
                # Mix of operations
                for i in range(50):
                    key = f"shared_key_{i % 10}"

                    # Get operation (should increment hits)
                    value = cache.get(key)
                    if value is not None:
                        results.append("hit")

                    # Occasional set operation
                    if i % 10 == 0:
                        cache.set(
                            f"new_key_{thread_id}_{i}", f"new_value_{thread_id}_{i}"
                        )
                        results.append("set")

                    # Occasional contains check
                    if i % 15 == 0:
                        if cache.contains(key):
                            results.append("contains")

            except Exception as e:
                results.append(f"error: {e}")

        # Run concurrent operations
        num_threads = 8
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [
                executor.submit(concurrent_operations, i) for i in range(num_threads)
            ]
            for future in futures:
                future.result()

        # Verify no errors occurred
        errors = [r for r in results if str(r).startswith("error")]
        assert len(errors) == 0, f"Errors in concurrent operations: {errors}"

        # Verify hit counter is reasonable
        hits = cache.get_hits()
        assert hits > 0, "Hit counter should have been incremented"

        # Verify some operations completed
        hit_count = sum(1 for r in results if r == "hit")
        set_count = sum(1 for r in results if r == "set")
        contains_count = sum(1 for r in results if r == "contains")

        assert hit_count > 0, "Should have some cache hits"
        assert set_count > 0, "Should have some set operations"
        assert contains_count > 0, "Should have some contains operations"

    def test_diskcache_thread_safety_clear(self, tmp_path):
        """Test thread safety ensuring no RuntimeError when clear() and set() occur in parallel."""
        cache = DiskCache(str(tmp_path / "thread_safety_clear_cache"))

        # Pre-populate some keys
        for i in range(10):
            cache.set(f"initial_key_{i}", f"initial_value_{i}")

        errors = []
        operations_completed = []

        def clear_worker():
            """Worker that repeatedly calls clear()."""
            try:
                for _ in range(20):  # Multiple clear operations
                    cache.clear()
                    operations_completed.append("clear")
                    time.sleep(
                        0.001
                    )  # Small delay to increase chance of race condition
            except Exception as e:
                errors.append(f"clear_worker: {e}")

        def set_worker(worker_id):
            """Worker that repeatedly calls set()."""
            try:
                for i in range(30):  # Multiple set operations
                    key = f"worker_{worker_id}_key_{i}"
                    value = f"worker_{worker_id}_value_{i}"
                    cache.set(key, value)
                    operations_completed.append("set")
                    time.sleep(
                        0.001
                    )  # Small delay to increase chance of race condition
            except Exception as e:
                errors.append(f"set_worker_{worker_id}: {e}")

        def get_worker():
            """Worker that repeatedly calls get() on existing keys."""
            try:
                for i in range(25):
                    # Try to get both initial and new keys
                    cache.get(f"initial_key_{i % 10}")
                    cache.get(f"worker_0_key_{i % 10}")
                    operations_completed.append("get")
                    time.sleep(0.001)
            except Exception as e:
                errors.append(f"get_worker: {e}")

        # Run workers concurrently
        with ThreadPoolExecutor(max_workers=6) as executor:
            futures = [
                executor.submit(clear_worker),
                executor.submit(set_worker, 0),
                executor.submit(set_worker, 1),
                executor.submit(set_worker, 2),
                executor.submit(get_worker),
            ]

            # Wait for all workers to complete
            for future in futures:
                future.result(timeout=30)  # 30 second timeout

        # Check that no RuntimeError or other errors occurred
        runtime_errors = [
            error
            for error in errors
            if "RuntimeError" in error or "dictionary changed size" in error
        ]
        assert (
            len(runtime_errors) == 0
        ), f"RuntimeError(s) occurred during concurrent operations: {runtime_errors}"

        # Check that no other errors occurred
        assert (
            len(errors) == 0
        ), f"Errors occurred during concurrent operations: {errors}"

        # Verify that operations completed (some may have been cleared)
        clear_count = sum(1 for op in operations_completed if op == "clear")
        set_count = sum(1 for op in operations_completed if op == "set")
        get_count = sum(1 for op in operations_completed if op == "get")

        assert clear_count > 0, "Clear operations should have completed"
        assert set_count > 0, "Set operations should have completed"
        assert get_count > 0, "Get operations should have completed"

        # Final verification that cache is in a consistent state
        # (We can't predict exact contents due to race conditions, but it should not crash)
        try:
            cache.clear()  # Final clear should work without error
        except Exception as e:
            raise AssertionError(f"Final clear operation failed: {e}")


class TestCacheIntegration:
    """Integration tests for cache functionality."""

    def test_disk_cache_persistence(self, tmp_path):
        """Test that DiskCache persists data across instances."""
        cache_dir = tmp_path / "persistence_test"

        # Create first cache instance and set data
        cache1 = DiskCache(str(cache_dir))
        cache1.set("persistent_key", "persistent_value")
        cache1.set("complex_data", {"list": [1, 2, 3], "nested": {"key": "value"}})

        # Create second cache instance pointing to same directory
        cache2 = DiskCache(str(cache_dir))

        # Should be able to retrieve data from second instance
        assert cache2.get("persistent_key") == "persistent_value"
        assert cache2.get("complex_data") == {
            "list": [1, 2, 3],
            "nested": {"key": "value"},
        }
        assert cache2.contains("persistent_key")
        assert cache2.contains("complex_data")

    def test_memory_cache_isolation(self):
        """Test that MemoryCache instances are isolated."""
        cache1 = MemoryCache()
        cache2 = MemoryCache()

        # Set data in first cache
        cache1.set("isolation_test", "cache1_value")

        # Second cache should not see the data
        assert cache2.get("isolation_test") is None
        assert not cache2.contains("isolation_test")

        # Set different data in second cache
        cache2.set("isolation_test", "cache2_value")

        # Each cache should have its own value
        assert cache1.get("isolation_test") == "cache1_value"
        assert cache2.get("isolation_test") == "cache2_value"

    def test_cache_with_special_characters(self, tmp_path):
        """Test cache with keys and values containing special characters."""
        # Test both cache types
        memory_cache = MemoryCache()
        disk_cache = DiskCache(str(tmp_path / "special_chars_cache"))

        special_cases = [
            ("key with spaces", "value with spaces"),
            ("key/with/slashes", "value\\with\\backslashes"),
            ("key.with.dots", "value.with.dots"),
            ("key-with-dashes", "value_with_underscores"),
            ("unicode_key_🔑", "unicode_value_🎯"),
            ("key\nwith\nnewlines", "value\twith\ttabs"),
            ("", "empty_key_test"),  # Empty key
            ("normal_key", ""),  # Empty value
        ]

        for cache in [memory_cache, disk_cache]:
            for key, value in special_cases:
                # Test set and get
                cache.set(key, value)
                assert cache.get(key) == value
                assert cache.contains(key)

                # Test delete
                cache.delete(key)
                assert cache.get(key) is None
                assert not cache.contains(key)

    def test_large_data_handling(self, tmp_path):
        """Test cache handling of large data structures."""
        memory_cache = MemoryCache()
        disk_cache = DiskCache(str(tmp_path / "large_data_cache"))

        # Create large data structure
        large_list = list(range(10000))
        large_dict = {f"key_{i}": f"value_{i}" for i in range(1000)}
        large_string = "x" * 100000

        test_data = [
            ("large_list", large_list),
            ("large_dict", large_dict),
            ("large_string", large_string),
        ]

        for cache in [memory_cache, disk_cache]:
            for key, data in test_data:
                # Set large data
                cache.set(key, data)

                # Retrieve and verify
                retrieved = cache.get(key)
                assert retrieved == data
                assert cache.contains(key)

                # Clean up
                cache.delete(key)
                assert cache.get(key) is None


if __name__ == "__main__":
    pytest.main([__file__])
