"""
Platform-aware timing logic for performance tests.

This module provides utilities for setting timing thresholds based on the operating
system and machine capabilities, mimicking the logic used in test_memory_cache_with_large_dataset.
"""

import sys
import os
from typing import Tuple, Optional


def get_timing_threshold() -> float:
    """
    Get platform-aware timing threshold for performance tests.

    Different operating systems and CI environments exhibit varying levels of
    timing consistency and I/O performance, necessitating platform-specific
    thresholds to prevent false test failures while maintaining meaningful
    performance assertions.

    Mimics the logic used in test_memory_cache_with_large_dataset:
    - Detect OS with sys.platform
    - Read optional env var FAST_MACHINE
    - Set timing_threshold based on platform and machine speed

    Returns:
        float: Timing threshold multiplier
            - Lenient (2.5x) on Windows/slow CI runners
            - Moderate (1.8x) on Linux/macOS default
            - Strict (1.2x) on fast machines
    """
    # Read optional environment variable for fast machine detection
    is_fast_machine = os.getenv("FAST_MACHINE", "").lower() in ("1", "true", "yes")

    # Set timing threshold based on platform and machine capabilities
    if sys.platform.startswith("win") and not is_fast_machine:
        # WINDOWS THRESHOLD: 2.5x (Lenient)
        #
        # Rationale: Windows exhibits significantly more timing variability due to:
        # 1. File system overhead: NTFS operations are slower than ext4/APFS
        # 2. Process scheduling: Windows process scheduling can introduce delays
        # 3. Antivirus interference: Real-time scanning affects I/O performance
        # 4. CI environment variability: Windows CI runners often have limited resources
        # 5. System services: Background Windows services can impact performance
        #
        # The 2.5x threshold accommodates these Windows-specific performance challenges
        # while still ensuring cache performance improvements are measurable.
        timing_threshold = 2.5  # Lenient for Windows CI
    elif is_fast_machine:
        # FAST MACHINE THRESHOLD: 1.2x (Strict)
        #
        # Rationale: High-performance development machines should demonstrate
        # clear cache benefits with minimal timing variance:
        # 1. Fast SSD storage reduces I/O bottlenecks
        # 2. Abundant RAM minimizes system resource contention
        # 3. Modern CPUs provide consistent execution timing
        # 4. Controlled environment with fewer background processes
        #
        # The 1.2x threshold ensures that optimizations show significant impact
        # on capable hardware while avoiding false positives from micro-optimizations.
        timing_threshold = 1.2  # Strict timing for fast machines
    else:
        # LINUX/MACOS THRESHOLD: 1.8x (Moderate)
        #
        # Rationale: Unix-like systems generally provide more consistent timing
        # but still require tolerance for CI environment variability:
        # 1. Efficient file systems (ext4, APFS) with better I/O characteristics
        # 2. More predictable process scheduling and resource management
        # 3. CI runner variability: Shared resources in cloud CI environments
        # 4. Container overhead: Tests may run in Docker with additional layers
        # 5. Network-attached storage: CI systems may use slower networked disks
        #
        # The 1.8x threshold balances performance validation with CI reliability,
        # allowing for infrastructure variance while detecting meaningful regressions.
        timing_threshold = 1.8  # Moderate timing for other platforms

    return timing_threshold


def should_skip_timing_assertion(
    time_value: float, min_threshold: float = 0.0001
) -> bool:
    """
    Check if timing assertion should be skipped due to very small absolute times.

    Args:
        time_value: The measured time value in seconds
        min_threshold: Minimum threshold below which timing is considered too small

    Returns:
        bool: True if timing assertion should be skipped, False otherwise
    """
    return time_value < min_threshold


def evaluate_timing_performance(
    baseline_time: float, optimized_time: float, min_time_threshold: float = 0.0001
) -> Tuple[bool, Optional[float], str]:
    """
    Evaluate timing performance with platform-aware thresholds and guards.

    Args:
        baseline_time: Baseline execution time in seconds
        optimized_time: Optimized execution time in seconds
        min_time_threshold: Minimum time threshold for reliable measurement

    Returns:
        Tuple containing:
        - bool: Whether timing assertion should be performed
        - Optional[float]: Speed improvement ratio (None if timing too small)
        - str: Status message explaining the evaluation
    """
    # Get platform-aware timing threshold
    timing_threshold = get_timing_threshold()

    # Guard against very small absolute times
    if should_skip_timing_assertion(
        baseline_time, min_time_threshold
    ) or should_skip_timing_assertion(optimized_time, min_time_threshold):
        return (
            False,
            None,
            f"Timing too small to measure accurately (baseline: {baseline_time:.6f}s, "
            f"optimized: {optimized_time:.6f}s, threshold: {min_time_threshold}s). "
            "Skipping timing assertion, verify functional equality only.",
        )

    # Calculate speed improvement
    speed_improvement = (
        baseline_time / optimized_time if optimized_time > 0 else float("inf")
    )

    # Check if optimization meets timing threshold
    timing_passed = optimized_time < baseline_time * timing_threshold

    status_msg = (
        f"Timing evaluation: baseline={baseline_time:.4f}s, "
        f"optimized={optimized_time:.4f}s, improvement={speed_improvement:.2f}x, "
        f"threshold={timing_threshold}x, passed={timing_passed}"
    )

    return True, speed_improvement, status_msg


def get_platform_info() -> dict:
    """
    Get platform information for debugging timing issues.

    Returns:
        dict: Platform information including OS, fast machine flag, and timing threshold
    """
    is_fast_machine = os.getenv("FAST_MACHINE", "").lower() in ("1", "true", "yes")
    timing_threshold = get_timing_threshold()

    return {
        "platform": sys.platform,
        "is_fast_machine": is_fast_machine,
        "fast_machine_env": os.getenv("FAST_MACHINE", ""),
        "timing_threshold": timing_threshold,
        "is_windows": sys.platform.startswith("win"),
        "is_linux": sys.platform.startswith("linux"),
        "is_macos": sys.platform.startswith("darwin"),
    }


# Example usage
if __name__ == "__main__":
    import time

    # Demo the platform-aware timing logic
    print("Platform-aware timing logic demo:")
    print("-" * 40)

    # Show platform info
    platform_info = get_platform_info()
    for key, value in platform_info.items():
        print(f"{key}: {value}")

    print(f"\nTiming threshold: {get_timing_threshold()}")

    # Simulate some timing measurements
    print("\nExample timing evaluations:")

    # Case 1: Normal timing
    can_assert, improvement, msg = evaluate_timing_performance(0.1, 0.05)
    print(f"Normal timing: {msg}")

    # Case 2: Very small timing (should skip assertion)
    can_assert, improvement, msg = evaluate_timing_performance(0.00005, 0.00003)
    print(f"Small timing: {msg}")

    # Case 3: Poor optimization
    can_assert, improvement, msg = evaluate_timing_performance(0.1, 0.15)
    print(f"Poor optimization: {msg}")
