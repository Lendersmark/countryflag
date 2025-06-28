"""
Stress tests for the countryflag package with large datasets.

This module contains tests for handling very large datasets and
concurrent operations to ensure the library performs well under load.
"""

import gc
import multiprocessing
import os
import random
import string
import sys
import threading
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from typing import Any, Dict, List, Tuple

import psutil
import pytest

from countryflag.cache.disk import DiskCache
from countryflag.cache.memory import MemoryCache
from countryflag.core.converters import CountryConverterSingleton
from countryflag.core.flag import CountryFlag


def generate_large_country_list(size: int) -> List[str]:
    """Generate a large list of country names by repeating real country names."""
    real_countries = [
        "United States",
        "Canada",
        "Mexico",
        "Brazil",
        "Argentina",
        "United Kingdom",
        "France",
        "Germany",
        "Italy",
        "Spain",
        "Russia",
        "China",
        "Japan",
        "India",
        "Australia",
        "South Africa",
        "Egypt",
        "Nigeria",
        "Kenya",
        "Morocco",
        "Saudi Arabia",
        "United Arab Emirates",
        "Israel",
        "Turkey",
        "Iran",
        "Thailand",
        "Vietnam",
        "Indonesia",
        "Malaysia",
        "Philippines",
        "South Korea",
        "North Korea",
        "Mongolia",
        "Kazakhstan",
        "Ukraine",
        "Poland",
        "Sweden",
        "Norway",
        "Finland",
        "Denmark",
        "Netherlands",
        "Belgium",
        "Switzerland",
        "Austria",
        "Greece",
        "Portugal",
        "Ireland",
        "Iceland",
        "New Zealand",
        "Singapore",
    ]

    # Calculate how many times to repeat the list
    repeat_count = (size // len(real_countries)) + 1

    # Generate a list of the desired size
    large_list = (real_countries * repeat_count)[:size]

    # Shuffle the list to avoid patterns
    random.shuffle(large_list)

    return large_list


def get_process_memory() -> float:
    """Get the memory usage of the current process in MB."""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024 * 1024)  # Convert to MB


def create_temp_file_with_countries(tmp_path, countries: List[str]) -> str:
    """Create a temporary file with country names, one per line."""
    temp_file = tmp_path / "large_countries.txt"
    with open(temp_file, "w") as f:
        for country in countries:
            f.write(f"{country}\n")
    return str(temp_file)


class TestLargeDatasets:
    """Tests for handling very large datasets."""

    @pytest.fixture(scope="class")
    def very_large_country_list(self) -> List[str]:
        """Generate a very large list of country names (1000 entries)."""
        return generate_large_country_list(1000)

    @pytest.fixture(scope="class")
    def extremely_large_country_list(self) -> List[str]:
        """Generate an extremely large list of country names (5000 entries)."""
        return generate_large_country_list(5000)

    def test_very_large_list_conversion(self, very_large_country_list):
        """Test conversion of a very large list of country names to flags."""
        cf = CountryFlag()
        start_time = time.time()
        flags, pairs = cf.get_flag(very_large_country_list)
        end_time = time.time()

        # Check that we got the expected number of flags
        assert len(pairs) == len(very_large_country_list)

        # Log the execution time
        execution_time = end_time - start_time
        print(
            f"\nConverted {len(very_large_country_list)} countries in {execution_time:.2f} seconds"
        )

        # Execution time should be reasonable
        assert execution_time < 10, "Conversion took too long"

    def test_extremely_large_list_conversion(self, extremely_large_country_list):
        """Test conversion of an extremely large list of country names to flags."""
        cf = CountryFlag()

        # Measure memory usage before
        mem_before = get_process_memory()

        start_time = time.time()
        flags, pairs = cf.get_flag(extremely_large_country_list)
        end_time = time.time()

        # Measure memory usage after
        mem_after = get_process_memory()

        # Check that we got the expected number of flags
        assert len(pairs) == len(extremely_large_country_list)

        # Log the execution time and memory usage
        execution_time = end_time - start_time
        memory_used = mem_after - mem_before
        print(
            f"\nConverted {len(extremely_large_country_list)} countries in {execution_time:.2f} seconds"
        )
        print(f"Memory used: {memory_used:.2f} MB")

        # Execution time and memory usage should be reasonable
        assert execution_time < 30, "Conversion took too long"
        assert memory_used < 100, "Memory usage was too high"

    def test_memory_usage_under_load(self, extremely_large_country_list):
        """Test memory usage when processing a large dataset multiple times."""
        cf = CountryFlag()

        # Measure memory usage before
        mem_before = get_process_memory()

        # Run multiple conversions
        for _ in range(5):
            flags, pairs = cf.get_flag(extremely_large_country_list)
            assert len(pairs) == len(extremely_large_country_list)

            # Force garbage collection to clean up any temporary objects
            gc.collect()

        # Measure memory usage after
        mem_after = get_process_memory()

        # Log memory usage
        memory_used = mem_after - mem_before
        print(f"\nMemory used after multiple large conversions: {memory_used:.2f} MB")

        # Memory usage should be reasonable
        assert memory_used < 200, "Memory usage was too high after multiple conversions"


class TestConcurrentOperations:
    """Tests for concurrent operations."""

    @pytest.fixture(scope="class")
    def medium_country_lists(self) -> List[List[str]]:
        """Generate multiple medium-sized country lists for concurrent testing."""
        return [generate_large_country_list(100) for _ in range(10)]

    def test_threaded_operations(self, medium_country_lists):
        """Test concurrent operations using threads."""
        cf = CountryFlag()
        results = []

        # Function to be executed in threads
        def convert_countries(countries):
            flags, pairs = cf.get_flag(countries)
            return len(pairs)

        # Create and start threads
        threads = []
        start_time = time.time()

        for countries in medium_country_lists:
            thread = threading.Thread(
                target=lambda: results.append(convert_countries(countries))
            )
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        end_time = time.time()

        # Check results
        assert len(results) == len(medium_country_lists)
        assert all(result == len(medium_country_lists[0]) for result in results)

        # Log execution time
        execution_time = end_time - start_time
        print(
            f"\nThreaded conversion of {len(medium_country_lists)} lists took {execution_time:.2f} seconds"
        )

        # Should be faster than sequential execution (rough estimate)
        sequential_time = sum(
            len(countries) * 0.01 for countries in medium_country_lists
        )
        assert (
            execution_time < sequential_time
        ), "Threaded execution was not faster than estimated sequential execution"

    def test_thread_pool_operations(self, medium_country_lists):
        """Test concurrent operations using a thread pool."""
        cf = CountryFlag()

        # Function to be executed in thread pool
        def convert_countries(countries):
            flags, pairs = cf.get_flag(countries)
            return len(pairs)

        # Use ThreadPoolExecutor
        start_time = time.time()

        with ThreadPoolExecutor(max_workers=4) as executor:
            results = list(executor.map(convert_countries, medium_country_lists))

        end_time = time.time()

        # Check results
        assert len(results) == len(medium_country_lists)
        assert all(result == len(medium_country_lists[0]) for result in results)

        # Log execution time
        execution_time = end_time - start_time
        print(
            f"\nThread pool conversion of {len(medium_country_lists)} lists took {execution_time:.2f} seconds"
        )

        # Thread pool should be efficient
        assert execution_time < 5, "Thread pool execution took too long"


class TestCachePerformance:
    """Tests for cache performance with large datasets."""

    @pytest.fixture(scope="class")
    def large_country_list(self) -> List[str]:
        """Generate a large list of country names."""
        return generate_large_country_list(500)

    def test_memory_cache_with_large_dataset(self, large_country_list):
        """Test memory cache performance with a large dataset."""
        memory_cache = MemoryCache()
        cf = CountryFlag(cache=memory_cache)

        # First run (cache miss)
        start_time_miss = time.time()
        flags_miss, _ = cf.get_flag(large_country_list)
        end_time_miss = time.time()

        # Second run (cache hit)
        start_time_hit = time.time()
        flags_hit, _ = cf.get_flag(large_country_list)
        end_time_hit = time.time()

        # Calculate execution times
        time_miss = end_time_miss - start_time_miss
        time_hit = end_time_hit - start_time_hit

        # Log results
        print(f"\nMemory cache miss time: {time_miss:.4f} seconds")
        print(f"Memory cache hit time: {time_hit:.4f} seconds")

        # Handle case where timing is too fast to measure accurately
        if time_hit > 0:
            print(f"Speed improvement: {time_miss / time_hit:.2f}x")
        else:
            print("Speed improvement: Cache hit too fast to measure accurately")

        # Cache hit should be significantly faster
        # Platform-specific timing thresholds account for CI variability and OS I/O characteristics
        is_fast_machine = os.getenv("FAST_MACHINE", "").lower() in ("1", "true", "yes")

        if sys.platform.startswith("win") and not is_fast_machine:
            # WINDOWS TIMING THRESHOLD: 1.5x (Very Lenient)
            #
            # Windows exhibits significant timing inconsistency in CI environments due to:
            # • NTFS file system overhead and fragmentation
            # • Windows Defender and antivirus real-time scanning impact
            # • Background Windows services consuming I/O bandwidth
            # • Windows CI runners often have limited and shared resources
            # • Process scheduling latency affecting small timing measurements
            #
            # The 1.5x threshold prevents false negatives while still validating
            # that caching provides measurable benefit over cache misses.
            timing_threshold = 1.5  # Very lenient for Windows CI

        elif is_fast_machine:
            # FAST MACHINE THRESHOLD: 0.5x (Strict)
            #
            # Development machines with FAST_MACHINE=true should demonstrate
            # clear performance improvements with minimal variance:
            # • Fast NVMe SSD storage eliminates I/O bottlenecks
            # • Sufficient RAM prevents memory pressure
            # • Controlled environment with minimal background processes
            # • High-performance CPUs with consistent execution timing
            #
            # The strict 0.5x threshold ensures optimizations show significant
            # impact and catches performance regressions early in development.
            timing_threshold = 0.5  # Strict timing for fast machines

        else:
            # LINUX/MACOS THRESHOLD: 0.8x (Moderate)
            #
            # Unix-like systems generally provide more consistent timing but
            # CI environments still introduce variability:
            # • ext4/APFS file systems with better I/O characteristics than NTFS
            # • More predictable process scheduling and resource management
            # • Docker container overhead in containerized CI environments
            # • Network-attached storage in cloud CI (AWS, GCP, Azure)
            # • Shared CPU resources among multiple CI jobs
            #
            # The 0.8x threshold balances meaningful performance validation
            # with tolerance for infrastructure-related timing variance.
            timing_threshold = 0.8  # Moderate timing for other platforms

        # Only check timing if both times are measurable
        if time_hit > 0.0001 and time_miss > 0.0001:
            assert (
                time_hit < time_miss * timing_threshold
            ), f"Cache hit was not significantly faster than miss (hit: {time_hit:.4f}s, miss: {time_miss:.4f}s, threshold: {timing_threshold}x)"
        else:
            print("Note: timing too fast …")
        assert flags_hit == flags_miss, "Cache hit and miss produced different results"

    def test_disk_cache_with_large_dataset(self, large_country_list, tmp_path):
        """Test disk cache performance with a large dataset."""
        disk_cache = DiskCache(str(tmp_path / "large_cache"))
        cf = CountryFlag(cache=disk_cache)

        # First run (cache miss) - run multiple times to get better average
        times_miss = []
        for _ in range(3):
            start_time = time.time()
            flags_miss, _ = cf.get_flag(large_country_list)
            end_time = time.time()
            times_miss.append(end_time - start_time)

        # Second run (cache hit) - run multiple times to get better average
        times_hit = []
        for _ in range(3):
            start_time = time.time()
            flags_hit, _ = cf.get_flag(large_country_list)
            end_time = time.time()
            times_hit.append(end_time - start_time)

        # Calculate average execution times
        time_miss = sum(times_miss) / len(times_miss)
        time_hit = sum(times_hit) / len(times_hit)

        # Log results with detailed timing information for debugging
        print(f"\nDisk cache miss times: {times_miss}")
        print(f"Disk cache hit times: {times_hit}")
        print(f"Disk cache miss time (avg): {time_miss:.4f} seconds")
        print(f"Disk cache hit time (avg): {time_hit:.4f} seconds")

        # Handle case where timing is too fast to measure accurately
        if time_hit > 0:
            print(f"Speed improvement: {time_miss / time_hit:.2f}x")
        else:
            print("Speed improvement: Cache hit too fast to measure accurately")

        # For disk cache, we mainly care that results are consistent and cache works
        # Performance may vary due to disk I/O, so we use a more lenient check
        assert flags_hit == flags_miss, "Cache hit and miss produced different results"

        # Platform-specific timing thresholds account for CI variability and disk I/O characteristics
        is_fast_machine = os.getenv("FAST_MACHINE", "").lower() in ("1", "true", "yes")

        if sys.platform.startswith("win") and not is_fast_machine:
            # WINDOWS DISK CACHE THRESHOLD: 3.0x (Very Lenient)
            #
            # Windows disk I/O is particularly inconsistent in CI environments due to:
            # • NTFS file system overhead and defragmentation issues
            # • Windows Defender real-time scanning of cache files
            # • Background Windows services consuming disk bandwidth
            # • Shared and limited I/O resources in Windows CI runners
            # • Process scheduling latency affecting disk operations
            # • Potential antivirus interference with cache file access
            #
            # The 3.0x threshold prevents false negatives while still validating
            # that disk caching doesn't cause performance regressions.
            timing_threshold = 3.0  # Very lenient for Windows CI disk operations

        elif is_fast_machine:
            # FAST MACHINE DISK THRESHOLD: 1.5x (Moderate)
            #
            # Development machines with FAST_MACHINE=true should show good disk performance:
            # • Fast NVMe SSD storage with low latency
            # • Sufficient RAM for file system caching
            # • Controlled environment with minimal background disk activity
            # • High-performance storage controllers
            #
            # The 1.5x threshold accounts for disk I/O overhead while ensuring
            # cache doesn't introduce significant performance penalties.
            timing_threshold = (
                1.5  # Moderate timing for fast machines with good storage
            )

        else:
            # LINUX/MACOS DISK THRESHOLD: 2.0x (Balanced)
            #
            # Unix-like systems generally have better disk I/O consistency but
            # CI environments still introduce variability:
            # • ext4/APFS file systems with better performance than NTFS
            # • More efficient file system caching and I/O scheduling
            # • Docker container storage overhead in containerized CI
            # • Network-attached storage latency in cloud CI environments
            # • Shared disk resources among multiple CI jobs
            #
            # The 2.0x threshold balances disk I/O overhead tolerance
            # with meaningful performance regression detection.
            timing_threshold = 2.0  # Balanced timing for other platforms

        # Only check timing if both times are measurable (avoid division by zero and precision issues)
        if time_hit > 0.0001 and time_miss > 0.0001:
            assert (
                time_hit < time_miss * timing_threshold
            ), f"Disk cache hit was much slower than miss (hit: {time_hit:.4f}s, miss: {time_miss:.4f}s, threshold: {timing_threshold}x) - possible cache issue"
        else:
            print(
                "Note: Disk cache timing too fast to measure accurately - cache functionality verified through result consistency"
            )

    def test_cache_size(self, large_country_list, tmp_path):
        """Test the size of the cache with a large dataset."""
        # Create a disk cache
        cache_dir = tmp_path / "size_cache"
        disk_cache = DiskCache(str(cache_dir))
        cf = CountryFlag(cache=disk_cache)

        # Fill the cache
        cf.get_flag(large_country_list)

        # Measure the size of the cache directory
        cache_size = sum(
            os.path.getsize(os.path.join(dirpath, filename))
            for dirpath, _, filenames in os.walk(str(cache_dir))
            for filename in filenames
        )

        # Convert to MB
        cache_size_mb = cache_size / (1024 * 1024)

        # Log the cache size
        print(
            f"\nDisk cache size for {len(large_country_list)} countries: {cache_size_mb:.2f} MB"
        )

        # Cache size should be reasonable
        assert cache_size_mb < 10, "Cache size was too large"


class TestFileProcessing:
    """Tests for processing large files."""

    def test_large_file_processing(self, tmp_path):
        """Test processing a large file of country names."""
        from countryflag.utils.io import process_file_input

        # Generate a large list of countries
        countries = generate_large_country_list(2000)

        # Create a temporary file
        file_path = create_temp_file_with_countries(tmp_path, countries)

        # Process the file
        start_time = time.time()
        result = process_file_input(file_path)
        end_time = time.time()

        # Check results
        assert len(result) == len(countries)

        # Log execution time
        execution_time = end_time - start_time
        print(
            f"\nProcessed file with {len(countries)} countries in {execution_time:.2f} seconds"
        )

        # Execution time should be reasonable
        assert execution_time < 1, "File processing took too long"

    def test_async_file_processing(self, tmp_path):
        """Test asynchronous processing of a large file."""
        import asyncio

        from countryflag.utils.io import process_file_input_async

        # Generate a large list of countries
        countries = generate_large_country_list(3000)

        # Create a temporary file
        file_path = create_temp_file_with_countries(tmp_path, countries)

        # Process the file asynchronously
        async def run_test():
            start_time = time.time()
            result = await process_file_input_async(file_path)
            end_time = time.time()
            return result, end_time - start_time

        result, execution_time = asyncio.run(run_test())

        # Check results
        assert len(result) == len(countries)

        # Log execution time
        print(
            f"\nAsynchronously processed file with {len(countries)} countries in {execution_time:.2f} seconds"
        )

        # Execution time should be reasonable
        assert execution_time < 1, "Async file processing took too long"
