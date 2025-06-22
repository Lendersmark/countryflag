#!/usr/bin/env python3
"""
Example of batch processing with countryflag.

This example demonstrates how to efficiently process large datasets
of country names using various techniques:

1. Chunking
2. Parallel processing
3. Asynchronous processing
4. Caching
"""

import asyncio
import concurrent.futures
import os
import random
import time
from typing import Any, Dict, List, Tuple

from countryflag.cache import DiskCache, MemoryCache
from countryflag.core import CountryFlag
from countryflag.utils.io import (
    process_file_input,
    process_file_input_async,
    process_multiple_files,
)

# Sample countries for generating test data
SAMPLE_COUNTRIES = [
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


def generate_large_dataset(size: int) -> List[str]:
    """
    Generate a large dataset of country names.

    Args:
        size: The number of country names to generate.

    Returns:
        List[str]: A list of country names.
    """
    # If size is smaller than the sample, return a subset
    if size <= len(SAMPLE_COUNTRIES):
        return random.sample(SAMPLE_COUNTRIES, size)

    # Otherwise, randomly sample with replacement
    return [random.choice(SAMPLE_COUNTRIES) for _ in range(size)]


def create_test_file(filename: str, size: int) -> str:
    """
    Create a test file with random country names.

    Args:
        filename: The name of the file to create.
        size: The number of country names to generate.

    Returns:
        str: The path to the created file.
    """
    countries = generate_large_dataset(size)

    with open(filename, "w") as f:
        for country in countries:
            f.write(f"{country}\n")

    return filename


def process_in_chunks(
    countries: List[str], chunk_size: int = 500
) -> List[Tuple[str, str]]:
    """
    Process a large list of countries in chunks.

    Args:
        countries: The list of country names to process.
        chunk_size: The size of each chunk.

    Returns:
        List[Tuple[str, str]]: A list of (country, flag) pairs.
    """
    cf = CountryFlag()
    result_pairs = []

    # Process in chunks
    for i in range(0, len(countries), chunk_size):
        chunk = countries[i : i + chunk_size]
        _, pairs = cf.get_flag(chunk)
        result_pairs.extend(pairs)

    return result_pairs


def process_in_parallel(
    countries: List[str], num_workers: int = 4, chunk_size: int = 500
) -> List[Tuple[str, str]]:
    """
    Process a large list of countries in parallel.

    Args:
        countries: The list of country names to process.
        num_workers: The number of worker threads.
        chunk_size: The size of each chunk.

    Returns:
        List[Tuple[str, str]]: A list of (country, flag) pairs.
    """
    # Create chunks
    chunks = []
    for i in range(0, len(countries), chunk_size):
        chunks.append(countries[i : i + chunk_size])

    # Function to process a chunk
    def process_chunk(chunk: List[str]) -> List[Tuple[str, str]]:
        cf = CountryFlag()
        _, pairs = cf.get_flag(chunk)
        return pairs

    # Process chunks in parallel
    result_pairs = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = [executor.submit(process_chunk, chunk) for chunk in chunks]
        for future in concurrent.futures.as_completed(futures):
            result_pairs.extend(future.result())

    return result_pairs


async def process_async(
    countries: List[str], chunk_size: int = 500
) -> List[Tuple[str, str]]:
    """
    Process a large list of countries asynchronously.

    Args:
        countries: The list of country names to process.
        chunk_size: The size of each chunk.

    Returns:
        List[Tuple[str, str]]: A list of (country, flag) pairs.
    """
    # Create chunks
    chunks = []
    for i in range(0, len(countries), chunk_size):
        chunks.append(countries[i : i + chunk_size])

    # Function to process a chunk
    async def process_chunk(chunk: List[str]) -> List[Tuple[str, str]]:
        # Run in a thread pool
        loop = asyncio.get_event_loop()
        cf = CountryFlag()
        _, pairs = await loop.run_in_executor(None, lambda: cf.get_flag(chunk))
        return pairs

    # Process chunks concurrently
    tasks = [process_chunk(chunk) for chunk in chunks]
    results = await asyncio.gather(*tasks)

    # Combine results
    result_pairs = []
    for pairs in results:
        result_pairs.extend(pairs)

    return result_pairs


def process_with_cache(
    countries: List[str], cache_type: str = "memory"
) -> List[Tuple[str, str]]:
    """
    Process a large list of countries with caching.

    Args:
        countries: The list of country names to process.
        cache_type: The type of cache to use ("memory" or "disk").

    Returns:
        List[Tuple[str, str]]: A list of (country, flag) pairs.
    """
    # Create the appropriate cache
    if cache_type == "disk":
        cache = DiskCache("./cache")
    else:
        cache = MemoryCache()

    # Create a CountryFlag instance with the cache
    cf = CountryFlag(cache=cache)

    # Process the countries
    _, pairs = cf.get_flag(countries)

    return pairs


def benchmark_methods():
    """Benchmark different processing methods."""
    # Generate a large dataset
    print("Generating dataset...")
    large_dataset = generate_large_dataset(10000)
    print(f"Generated {len(large_dataset)} country names")

    # Create test files
    print("Creating test files...")
    test_file1 = create_test_file("test_file1.txt", 2500)
    test_file2 = create_test_file("test_file2.txt", 2500)
    test_file3 = create_test_file("test_file3.txt", 2500)
    test_file4 = create_test_file("test_file4.txt", 2500)
    test_files = [test_file1, test_file2, test_file3, test_file4]

    # Benchmark chunking
    print("\nBenchmarking chunking method...")
    start_time = time.time()
    chunk_results = process_in_chunks(large_dataset)
    chunk_time = time.time() - start_time
    print(f"Processed {len(chunk_results)} countries in {chunk_time:.2f} seconds")

    # Benchmark parallel processing
    print("\nBenchmarking parallel processing method...")
    start_time = time.time()
    parallel_results = process_in_parallel(large_dataset)
    parallel_time = time.time() - start_time
    print(f"Processed {len(parallel_results)} countries in {parallel_time:.2f} seconds")

    # Benchmark async processing
    print("\nBenchmarking async processing method...")
    start_time = time.time()
    async_results = asyncio.run(process_async(large_dataset))
    async_time = time.time() - start_time
    print(f"Processed {len(async_results)} countries in {async_time:.2f} seconds")

    # Benchmark file processing
    print("\nBenchmarking file processing method...")
    start_time = time.time()
    file_results = process_file_input(test_file1)
    file_time = time.time() - start_time
    print(
        f"Processed {len(file_results)} countries from file in {file_time:.2f} seconds"
    )

    # Benchmark async file processing
    print("\nBenchmarking async file processing method...")
    start_time = time.time()
    async_file_results = asyncio.run(process_file_input_async(test_file2))
    async_file_time = time.time() - start_time
    print(
        f"Processed {len(async_file_results)} countries from file in {async_file_time:.2f} seconds"
    )

    # Benchmark multiple files processing
    print("\nBenchmarking multiple files processing method...")
    start_time = time.time()
    multiple_files_results = process_multiple_files(test_files)
    multiple_files_time = time.time() - start_time
    print(
        f"Processed {len(multiple_files_results)} countries from multiple files in {multiple_files_time:.2f} seconds"
    )

    # Benchmark memory cache
    print("\nBenchmarking memory cache method...")
    # First run (cache miss)
    start_time = time.time()
    memory_cache_results = process_with_cache(large_dataset, "memory")
    memory_cache_miss_time = time.time() - start_time
    print(
        f"Processed {len(memory_cache_results)} countries with memory cache (miss) in {memory_cache_miss_time:.2f} seconds"
    )

    # Second run (cache hit)
    start_time = time.time()
    memory_cache_results = process_with_cache(large_dataset, "memory")
    memory_cache_hit_time = time.time() - start_time
    print(
        f"Processed {len(memory_cache_results)} countries with memory cache (hit) in {memory_cache_hit_time:.2f} seconds"
    )
    print(
        f"Memory cache speedup: {memory_cache_miss_time / memory_cache_hit_time:.2f}x"
    )

    # Benchmark disk cache
    print("\nBenchmarking disk cache method...")
    # First run (cache miss)
    start_time = time.time()
    disk_cache_results = process_with_cache(large_dataset, "disk")
    disk_cache_miss_time = time.time() - start_time
    print(
        f"Processed {len(disk_cache_results)} countries with disk cache (miss) in {disk_cache_miss_time:.2f} seconds"
    )

    # Second run (cache hit)
    start_time = time.time()
    disk_cache_results = process_with_cache(large_dataset, "disk")
    disk_cache_hit_time = time.time() - start_time
    print(
        f"Processed {len(disk_cache_results)} countries with disk cache (hit) in {disk_cache_hit_time:.2f} seconds"
    )
    print(f"Disk cache speedup: {disk_cache_miss_time / disk_cache_hit_time:.2f}x")

    # Summary
    print("\nSummary:")
    print(f"Chunking: {chunk_time:.2f} seconds")
    print(
        f"Parallel: {parallel_time:.2f} seconds (Speedup: {chunk_time / parallel_time:.2f}x)"
    )
    print(f"Async: {async_time:.2f} seconds (Speedup: {chunk_time / async_time:.2f}x)")
    print(
        f"Memory Cache (hit): {memory_cache_hit_time:.2f} seconds (Speedup: {chunk_time / memory_cache_hit_time:.2f}x)"
    )
    print(
        f"Disk Cache (hit): {disk_cache_hit_time:.2f} seconds (Speedup: {chunk_time / disk_cache_hit_time:.2f}x)"
    )

    # Clean up
    print("\nCleaning up...")
    for file in test_files:
        os.remove(file)
    if os.path.exists("./cache"):
        import shutil

        shutil.rmtree("./cache")


if __name__ == "__main__":
    benchmark_methods()
