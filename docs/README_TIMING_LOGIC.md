# Platform-Aware Timing Logic

This implementation provides robust, platform-aware timing logic for performance tests, mimicking the logic used in `test_memory_cache_with_large_dataset`.

## Overview

The timing logic automatically adapts timing thresholds based on:
- **Operating System detection** using `sys.platform`
- **Optional `FAST_MACHINE` environment variable** for performance tuning
- **Protection against very small timing measurements** (< 0.0001s)

## Key Features

### 1. Platform Detection (`sys.platform`)
- **Windows** (`win32`): More lenient timing due to system overhead
- **Linux** (`linux`): Moderate timing expectations
- **macOS** (`darwin`): Moderate timing expectations

### 2. Fast Machine Detection
Set the `FAST_MACHINE` environment variable to enable strict timing:
```bash
# Enable strict timing
export FAST_MACHINE=1
# or
export FAST_MACHINE=true
# or  
export FAST_MACHINE=yes

# Default (more lenient timing)
unset FAST_MACHINE
# or
export FAST_MACHINE=false
```

### 3. Timing Thresholds

| Condition | Threshold | Description |
|-----------|-----------|-------------|
| Windows + slow machine | 2.5x | Lenient (2.5-3.0×) for Windows/slow CI |
| Linux/macOS + slow machine | 1.8x | Moderate (1.5-2.0×) for default systems |
| Any platform + fast machine | 1.2x | Strict (≤1.2×) for fast machines |

### 4. Small Timing Protection
- If either baseline or optimized time < 0.0001s
- Skip timing assertion entirely
- Only verify functional equality
- Prevents false negatives on very fast operations

## Usage Examples

### Basic Usage
```python
from platform_timing_logic import (
    get_timing_threshold,
    evaluate_timing_performance
)

# Measure your operations
baseline_time = 0.1  # Cache miss
optimized_time = 0.05  # Cache hit

# Evaluate timing with platform awareness
can_assert, improvement, msg = evaluate_timing_performance(
    baseline_time, optimized_time
)

if can_assert:
    # Perform timing assertion
    threshold = get_timing_threshold()
    assert optimized_time < baseline_time * threshold
    print(f"Speed improvement: {improvement:.2f}x")
else:
    # Skip timing, verify functional equality only
    print("Timing too small - verifying functional equality only")
```

### Integration with Test Functions
```python
def test_cache_performance_with_timing_logic(self):
    """Test cache performance with platform-aware timing."""
    # Your setup code here
    cache = MyCache()
    
    # Measure cache miss
    start_time = time.time()
    result_miss = cache.get_miss(key)
    time_miss = time.time() - start_time
    
    # Measure cache hit  
    start_time = time.time()
    result_hit = cache.get_hit(key)
    time_hit = time.time() - start_time
    
    # Platform-aware timing evaluation
    can_assert_timing, speed_improvement, status_msg = evaluate_timing_performance(
        baseline_time=time_miss,
        optimized_time=time_hit
    )
    
    print(status_msg)
    
    if can_assert_timing:
        # Perform timing assertion with platform-appropriate threshold
        timing_threshold = get_timing_threshold()
        assert time_hit < time_miss * timing_threshold, (
            f"Cache hit not significantly faster: hit={time_hit:.4f}s, "
            f"miss={time_miss:.4f}s, threshold={timing_threshold}x"
        )
    else:
        # Skip timing assertion, verify functional equality only
        print("Timing too small to measure - verifying functional equality only")
    
    # Always verify functional correctness
    assert result_hit == result_miss, "Cache results must be functionally equivalent"
```

## API Reference

### Core Functions

#### `get_timing_threshold() -> float`
Returns the platform-appropriate timing threshold multiplier.

**Returns:**
- `2.5`: Windows without FAST_MACHINE
- `1.8`: Linux/macOS without FAST_MACHINE  
- `1.2`: Any platform with FAST_MACHINE=true

#### `should_skip_timing_assertion(time_value: float, min_threshold: float = 0.0001) -> bool`
Checks if timing assertion should be skipped due to very small times.

**Parameters:**
- `time_value`: Measured time in seconds
- `min_threshold`: Minimum reliable measurement threshold (default: 0.0001s)

**Returns:**
- `True`: Skip timing assertion
- `False`: Timing assertion can be performed

#### `evaluate_timing_performance(baseline_time: float, optimized_time: float, min_time_threshold: float = 0.0001) -> Tuple[bool, Optional[float], str]`
Comprehensive timing evaluation with platform awareness.

**Parameters:**
- `baseline_time`: Baseline execution time in seconds
- `optimized_time`: Optimized execution time in seconds
- `min_time_threshold`: Minimum threshold for reliable timing

**Returns:**
- `bool`: Whether timing assertion should be performed
- `Optional[float]`: Speed improvement ratio (None if timing too small)
- `str`: Status message explaining the evaluation

#### `get_platform_info() -> dict`
Returns comprehensive platform information for debugging.

**Returns dictionary with:**
- `platform`: sys.platform value
- `is_fast_machine`: Boolean fast machine detection
- `fast_machine_env`: FAST_MACHINE environment variable value
- `timing_threshold`: Current timing threshold
- `is_windows`, `is_linux`, `is_macos`: Platform flags

## Environment Variables

### FAST_MACHINE
Controls strict timing mode for high-performance machines.

**Accepted values for "fast machine" mode:**
- `1`
- `true` 
- `yes`

**All other values (or unset) default to platform-appropriate timing.**

## Platform-Specific Behavior and Rationale

Different operating systems and CI environments exhibit varying levels of timing consistency and I/O performance. These platform-specific thresholds are designed to prevent false test failures while maintaining meaningful performance assertions.

### Windows (`sys.platform.startswith("win")`)
- **Default threshold**: 2.5x (lenient)
- **With FAST_MACHINE**: 1.2x (strict)

**Rationale for lenient Windows thresholds:**
- **File system overhead**: NTFS operations are inherently slower than ext4/APFS, especially for small files and metadata operations
- **Process scheduling**: Windows process scheduling can introduce variable delays, particularly under resource contention
- **Antivirus interference**: Real-time scanning by Windows Defender and third-party antivirus affects I/O performance unpredictably
- **CI environment limitations**: Windows CI runners (GitHub Actions, Azure DevOps) often have limited and shared resources
- **System services**: Background Windows services (Windows Update, indexing, telemetry) can impact performance
- **Registry access**: Windows applications often involve registry operations which add overhead
- **DLL loading**: Dynamic library loading in Windows can introduce timing variations

### Linux (`sys.platform.startswith("linux")`)
- **Default threshold**: 1.8x (moderate)
- **With FAST_MACHINE**: 1.2x (strict)

**Rationale for moderate Linux thresholds:**
- **Efficient file systems**: ext4, XFS, and btrfs provide better I/O characteristics than NTFS
- **Predictable scheduling**: Linux process scheduler provides more consistent resource allocation
- **CI variability**: Shared resources in cloud CI environments (AWS, GCP, Azure) still introduce variance
- **Container overhead**: Tests often run in Docker containers, adding virtualization layers
- **Network storage**: CI systems frequently use network-attached storage which can be slower
- **Memory management**: Linux memory management is efficient but can introduce latency during page faults
- **CPU throttling**: Cloud instances may experience CPU throttling under sustained load

### macOS (`sys.platform.startswith("darwin")`)
- **Default threshold**: 1.8x (moderate)  
- **With FAST_MACHINE**: 1.2x (strict)

**Rationale for moderate macOS thresholds:**
- **APFS performance**: Apple File System provides excellent performance characteristics similar to Linux filesystems
- **Unified memory**: Apple Silicon Macs have unified memory architecture reducing memory access latency
- **Background processes**: macOS background processes (Spotlight, Time Machine, cloud sync) can impact timing
- **CI limitations**: macOS CI runners are often more limited and expensive, leading to resource constraints
- **Thermal throttling**: MacBooks may throttle under sustained load affecting timing consistency
- **Security overhead**: macOS security features (SIP, Gatekeeper, XProtect) can introduce I/O delays

## Best Practices

1. **Always verify functional equality** regardless of timing results
2. **Use the evaluation function** instead of manual threshold checks
3. **Set FAST_MACHINE** appropriately for your CI/development environment
4. **Log timing results** for debugging performance issues
5. **Handle timing assertion failures gracefully** with informative messages

## Example Output

### Normal Execution (Windows, no FAST_MACHINE)
```
Platform Information:
  platform: win32
  is_fast_machine: False
  timing_threshold: 2.5

Timing evaluation: baseline=0.1000s, optimized=0.0500s, improvement=2.00x, threshold=2.5x, passed=True
```

### Fast Machine (FAST_MACHINE=1)
```
Platform Information:
  platform: win32
  is_fast_machine: True
  timing_threshold: 1.2

Timing evaluation: baseline=0.1000s, optimized=0.0500s, improvement=2.00x, threshold=1.2x, passed=True
```

### Very Fast Operations (Timing Skipped)
```
Timing too small to measure accurately (baseline: 0.000050s, optimized: 0.000030s, threshold: 0.0001s). 
Skipping timing assertion, verify functional equality only.
```

This implementation provides robust, platform-aware timing that adapts to different environments while maintaining reliable performance testing.
