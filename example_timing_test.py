"""
Example of how to use the platform-aware timing logic in tests.

This demonstrates how to integrate the timing logic into performance tests,
following the same pattern as test_memory_cache_with_large_dataset.
"""

import time
import sys
import os
from platform_timing_logic import (
    get_timing_threshold,
    should_skip_timing_assertion,
    evaluate_timing_performance,
    get_platform_info,
)


def example_cache_performance_test():
    """
    Example test function demonstrating platform-aware timing logic.

    This mimics the structure of test_memory_cache_with_large_dataset
    but uses the extracted timing logic functions.
    """
    print("Running example cache performance test...")
    print("=" * 50)

    # Show platform information
    platform_info = get_platform_info()
    print("Platform Information:")
    for key, value in platform_info.items():
        print(f"  {key}: {value}")
    print()

    # Simulate cache miss (slower operation)
    print("Simulating cache miss...")
    start_time_miss = time.time()
    # Simulate some work (replace with actual cache miss operation)
    time.sleep(0.1)  # Simulate 100ms operation
    end_time_miss = time.time()

    # Simulate cache hit (faster operation)
    print("Simulating cache hit...")
    start_time_hit = time.time()
    # Simulate faster cached operation
    time.sleep(0.02)  # Simulate 20ms cached operation
    end_time_hit = time.time()

    # Calculate execution times
    time_miss = end_time_miss - start_time_miss
    time_hit = end_time_hit - start_time_hit

    # Log results
    print(f"Cache miss time: {time_miss:.4f} seconds")
    print(f"Cache hit time: {time_hit:.4f} seconds")

    # Use platform-aware timing evaluation
    # This accounts for different OS and CI environment characteristics:
    # • Windows: Higher thresholds due to I/O overhead and CI variability
    # • Linux/macOS: Moderate thresholds for balanced performance validation
    # • Fast machines: Strict thresholds for development environments
    can_assert_timing, speed_improvement, status_msg = evaluate_timing_performance(
        baseline_time=time_miss, optimized_time=time_hit
    )

    print(f"\\nTiming Analysis:")
    print(f"  {status_msg}")

    if can_assert_timing:
        # Get the current platform's timing threshold
        timing_threshold = get_timing_threshold()

        print(f"  Can perform timing assertion: Yes")
        print(f"  Speed improvement: {speed_improvement:.2f}x")
        print(f"  Timing threshold: {timing_threshold}x")

        # Perform the timing assertion
        timing_passed = time_hit < time_miss * timing_threshold
        print(f"  Timing assertion passed: {timing_passed}")

        if not timing_passed:
            print(f"  WARNING: Cache hit was not significantly faster than miss!")
            print(f"    Expected: hit_time < {time_miss * timing_threshold:.4f}s")
            print(f"    Actual: hit_time = {time_hit:.4f}s")
        else:
            print(f"  SUCCESS: Cache performance meets platform expectations")

    else:
        print(f"  Can perform timing assertion: No")
        print(f"  Reason: Timing too small to measure accurately")
        print(f"  Fallback: Only verify functional equality")

    # Always verify functional equality (this would be your actual assertion)
    print(f"\\nFunctional verification: Cache hit and miss produce same results ✓")

    return can_assert_timing, speed_improvement if can_assert_timing else None


def example_with_different_scenarios():
    """
    Demonstrate how the timing logic behaves under different scenarios.
    """
    print("\\n" + "=" * 60)
    print("Testing different timing scenarios...")
    print("=" * 60)

    scenarios = [
        {
            "name": "Fast operations (should skip timing)",
            "baseline": 0.00005,
            "optimized": 0.00003,
        },
        {
            "name": "Moderate operations (should test timing)",
            "baseline": 0.05,
            "optimized": 0.02,
        },
        {
            "name": "Slow operations (should test timing)",
            "baseline": 0.5,
            "optimized": 0.1,
        },
        {
            "name": "Poor optimization (timing test should fail)",
            "baseline": 0.1,
            "optimized": 0.4,
        },
    ]

    for scenario in scenarios:
        print(f"\\nScenario: {scenario['name']}")
        print("-" * 40)

        can_assert, improvement, msg = evaluate_timing_performance(
            scenario["baseline"], scenario["optimized"]
        )

        print(f"  {msg}")

        if can_assert:
            timing_threshold = get_timing_threshold()
            passed = scenario["optimized"] < scenario["baseline"] * timing_threshold
            print(f"  Would timing assertion pass? {passed}")
        else:
            print(f"  Timing assertion skipped - verify functional equality only")


def demonstrate_environment_variable_effect():
    """
    Demonstrate how the FAST_MACHINE environment variable affects timing thresholds.
    """
    print("\\n" + "=" * 60)
    print("Demonstrating FAST_MACHINE environment variable effect...")
    print("=" * 60)

    # Save original environment
    original_fast_machine = os.environ.get("FAST_MACHINE", "")

    scenarios = [
        ("Not set", ""),
        ("Set to '1'", "1"),
        ("Set to 'true'", "true"),
        ("Set to 'yes'", "yes"),
        ("Set to 'false'", "false"),
    ]

    for desc, value in scenarios:
        # Set environment variable
        if value:
            os.environ["FAST_MACHINE"] = value
        else:
            os.environ.pop("FAST_MACHINE", None)

        # Get timing threshold
        threshold = get_timing_threshold()
        platform_info = get_platform_info()

        print(f"\\nFAST_MACHINE {desc} ('{value}'):")
        print(f"  Is fast machine: {platform_info['is_fast_machine']}")
        print(f"  Timing threshold: {threshold}x")
        print(f"  Platform: {platform_info['platform']}")

    # Restore original environment
    if original_fast_machine:
        os.environ["FAST_MACHINE"] = original_fast_machine
    else:
        os.environ.pop("FAST_MACHINE", None)


if __name__ == "__main__":
    # Run the example test
    example_cache_performance_test()

    # Show different scenarios
    example_with_different_scenarios()

    # Demonstrate environment variable effect
    demonstrate_environment_variable_effect()
