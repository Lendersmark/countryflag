"""
File I/O utility functions for the countryflag package.

This module contains utility functions for reading and processing files.
"""

import asyncio
import concurrent.futures
import logging
import os
from pathlib import Path
from typing import Any, Callable, List, TypeVar

# Configure logging
logger = logging.getLogger("countryflag.utils.io")

# Type variable for generic functions
T = TypeVar("T")


def process_file_input(file_path: str) -> List[str]:
    """
    Process a file containing country names, one per line.

    Args:
        file_path: The path to the file.

    Returns:
        List[str]: A list of country names.

    Raises:
        IOError: If the file cannot be read.

    Example:
        >>> process_file_input("countries.txt")  # File contains "USA\\nCanada"
        ['USA', 'Canada']
    """
    try:
        with open(file_path, encoding="utf-8") as f:
            # Read lines and strip whitespace
            return [line.strip() for line in f if line.strip()]
    except OSError as e:
        logger.error(f"Error reading file {file_path}: {e}")
        raise


async def process_file_input_async(file_path: str) -> List[str]:
    """
    Process a file containing country names asynchronously.

    Args:
        file_path: The path to the file.

    Returns:
        List[str]: A list of country names.

    Raises:
        IOError: If the file cannot be read.

    Example:
        >>> async def example():
        ...     return await process_file_input_async("countries.txt")
        >>> asyncio.run(example())  # File contains "USA\\nCanada"
        ['USA', 'Canada']
    """
    try:
        # For very large files, this will be more efficient
        loop = asyncio.get_event_loop()

        # Use ThreadPoolExecutor for file I/O operations
        with concurrent.futures.ThreadPoolExecutor() as pool:
            contents = await loop.run_in_executor(
                pool, lambda: Path(file_path).read_text(encoding="utf-8")
            )

            # Process the file contents
            return [line.strip() for line in contents.splitlines() if line.strip()]
    except OSError as e:
        logger.error(f"Error reading file {file_path}: {e}")
        raise


def process_multiple_files(file_paths: List[str], max_workers: int = 4) -> List[str]:
    """
    Process multiple files containing country names in parallel.

    Args:
        file_paths: A list of paths to files.
        max_workers: The maximum number of worker threads.

    Returns:
        List[str]: A combined list of country names from all files.

    Raises:
        IOError: If any file cannot be read.

    Example:
        >>> process_multiple_files(["countries1.txt", "countries2.txt"])
        ['USA', 'Canada', 'Germany', 'Japan']
    """
    results: List[str] = []

    # Use ThreadPoolExecutor for parallel file processing
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_file = {
            executor.submit(process_file_input, file_path): file_path
            for file_path in file_paths
        }

        for future in concurrent.futures.as_completed(future_to_file):
            file_path = future_to_file[future]
            try:
                # Add the results from this file to our combined results
                results.extend(future.result())
            except Exception as e:
                logger.error(f"Error processing file {file_path}: {e}")
                # Re-raise the exception
                raise

    return results
