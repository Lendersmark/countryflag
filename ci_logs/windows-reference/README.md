# Windows CI Reference Logs

This directory contains the exact stdout/stderr logs from failed GitHub Actions Windows CI jobs for later diffing and analysis.

## Files Overview

### Analysis
- **`ANALYSIS_SUMMARY.md`** - Detailed analysis of the Windows CI failures, root causes, and next steps

### Individual Job Logs (Latest Run: 15901720048)
- **`windows-py3.9-job-44846090814.log`** - Python 3.9 Windows job failure log
- **`windows-py3.10-job-44846090819.log`** - Python 3.10 Windows job failure log  
- **`windows-py3.11-job-44846090816.log`** - Python 3.11 Windows job failure log
- **`windows-py3.12-job-44846090841.log`** - Python 3.12 Windows job failure log

### Previous Run Logs (For Comparison)
- **`run-15901195739-failed.log`** - Failed logs from previous run 15901195739
- **`run-15900970285-failed.log`** - Failed logs from previous run 15900970285
- **`windows-py3.9-failed.log`** - Alternative capture of Python 3.9 failures

## Key Issues Found

1. **Unicode/Encoding Issues**: Flag emojis corrupted (`🇫🇷` → `ðŸ‡«ðŸ‡·`)
2. **Module Import Issues**: `python3` command not finding countryflag module
3. **Performance Test Issues**: Cache performance assertions failing

## Usage

These logs can be used for:
- Comparing output before/after fixes
- Understanding exact failure patterns  
- Debugging Windows-specific issues
- Validating fix effectiveness

Generated: 2025-06-26T17:08:00Z
Source: GitHub Actions Windows CI failures
