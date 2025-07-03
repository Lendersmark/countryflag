"""
Regression test to guard against future deadlocks without risking the main test run.

This test forks a separate Python process using multiprocessing.Process to run
operations that previously caused deadlocks. The parent process joins with a
2-second timeout; if the process is still alive, the test fails.
"""

import multiprocessing
import sys
import time
import unittest
from typing import Any


def deadlock_prone_sequence():
    """
    Function that runs the previously deadlocking sequence in a child process.

    This simulates the scenario where two consecutive get() calls on a cache
    used to cause freezing/deadlocks.
    """
    try:
        # Import inside the function to avoid issues with multiprocessing
        from src.countryflag.cache.memory import MemoryCache

        # Create a cache instance
        cache = MemoryCache()

        # Set a test value
        cache.set("test_key", "test_value")

        # Perform two consecutive get() calls that used to deadlock
        # This pattern was identified from the test_memory_cache_hits.py file
        result1 = cache.get("test_key")
        result2 = cache.get("test_key")

        # Verify the results are correct
        if result1 != "test_value" or result2 != "test_value":
            sys.exit(1)  # Exit with error code if results are wrong

        # Also test with CountryFlag operations that use cache
        from src.countryflag.core.flag import CountryFlag

        cf = CountryFlag()

        # Perform operations that involve cache get() calls
        flags1, pairs1 = cf.get_flag(["Germany"])
        flags2, pairs2 = cf.get_flag(["Germany"])  # Second call should hit cache

        # Verify results
        if flags1 and flags2 and flags1 == flags2:
            sys.exit(0)
        else:
            sys.exit(1)

        # If we reach here, everything completed successfully
        sys.exit(0)

    except Exception as e:
        # Exit with error code if any exception occurs
        print(f"Error in child process: {e}", file=sys.stderr)
        sys.exit(1)


def mixed_operations_sequence():
    """Run mixed cache operations that could potentially deadlock."""
    try:
        from src.countryflag.cache.memory import MemoryCache
        from src.countryflag.core.flag import CountryFlag

        # Test with MemoryCache directly
        cache = MemoryCache()

        # Sequence of operations that might cause issues
        cache.set("key1", "value1")
        cache.set("key2", "value2")

        # Multiple gets with contains checks
        result1 = cache.get("key1")
        exists1 = cache.contains("key1")
        result2 = cache.get("key2")
        exists2 = cache.contains("key2")

        # Get non-existent key
        result3 = cache.get("non_existent")
        exists3 = cache.contains("non_existent")

        # Test with CountryFlag (which uses cache internally)
        cf = CountryFlag()

        # Multiple flag operations
        flags1, _ = cf.get_flag(["United States"])
        flags2, _ = cf.get_flag(["Canada"])
        flags3, _ = cf.get_flag(["United States"])  # Should hit cache

        # Validate results
        if (
            result1 != "value1"
            or result2 != "value2"
            or result3 is not None
            or not exists1
            or not exists2
            or exists3
            or not flags1
            or not flags2
            or not flags3
        ):
            sys.exit(1)

        sys.exit(0)

    except Exception as e:
        print(f"Error in mixed operations: {e}", file=sys.stderr)
        sys.exit(1)


class TestDeadlockRegression(unittest.TestCase):
    """Regression test for deadlock prevention."""

    def setUp(self):
        """Set up test environment."""
        setup_multiprocessing()

    def test_no_deadlock_on_consecutive_cache_gets(self):
        """
        Test that consecutive cache get() calls don't cause deadlocks.

        This test forks a separate Python process to run the previously
        deadlocking sequence. The parent joins with a 2-second timeout;
        if the process is still alive, the test fails.
        """
        # Create a new process to run the deadlock-prone sequence
        process = multiprocessing.Process(target=deadlock_prone_sequence)

        # Start the process
        start_time = time.time()
        process.start()

        # Join with a 10-second timeout (Windows processes can be slow to start)
        process.join(timeout=10.0)

        # Check if the process is still alive (indicates potential deadlock)
        if process.is_alive():
            # Force terminate the process
            process.terminate()
            process.join()  # Wait for termination to complete

            elapsed_time = time.time() - start_time
            self.fail(
                f"Process is still alive after 10-second timeout "
                f"(elapsed: {elapsed_time:.2f}s). This indicates a potential "
                f"deadlock in consecutive cache get() operations."
            )

        # Check the exit code
        if process.exitcode != 0:
            self.fail(
                f"Child process exited with non-zero code: {process.exitcode}. "
                f"This indicates an error in the cache operations."
            )

        # If we reach here, the test passed
        elapsed_time = time.time() - start_time
        print(f"✓ Deadlock regression test passed (completed in {elapsed_time:.2f}s)")

    def test_no_deadlock_on_mixed_cache_operations(self):
        """
        Test that mixed cache operations (set/get/contains) don't cause deadlocks.

        This test runs a more complex sequence of cache operations that could
        potentially cause deadlocks in concurrent scenarios.
        """
        # Create and run the process
        process = multiprocessing.Process(target=mixed_operations_sequence)
        start_time = time.time()
        process.start()

        # Join with timeout (Windows processes can be slow to start)
        process.join(timeout=10.0)

        # Check for deadlock
        if process.is_alive():
            process.terminate()
            process.join()

            elapsed_time = time.time() - start_time
            self.fail(
                f"Mixed operations process deadlocked after 10-second timeout "
                f"(elapsed: {elapsed_time:.2f}s)."
            )

        # Check exit code
        if process.exitcode != 0:
            self.fail(
                f"Mixed operations process failed with exit code: {process.exitcode}"
            )

        elapsed_time = time.time() - start_time
        print(
            f"✓ Mixed operations deadlock test passed (completed in {elapsed_time:.2f}s)"
        )


def setup_multiprocessing():
    """Set up multiprocessing for Windows compatibility."""
    if hasattr(multiprocessing, "set_start_method"):
        try:
            multiprocessing.set_start_method("spawn", force=True)
        except RuntimeError:
            # Method already set, continue
            pass


if __name__ == "__main__":
    setup_multiprocessing()
    unittest.main()
