# CI Failure Analysis - Windows Environment

## Environment Details
- **OS**: Windows 10 Home, Version 2009
- **Python**: 3.10.11
- **pytest**: 8.4.1
- **Working Directory**: C:\Users\simon\Documents\GitHub\countryflag
- **Branch**: feat/cli-positional-args
- **Virtual Environment**: Active

## Test Execution
Command run: `pytest -m "not slow"`

## Test Results Summary
- **Total tests**: 247 collected
- **Failed**: 72 tests
- **Passed**: 175 tests
- **Warnings**: 1

## Primary Failure Pattern

### Unicode Encoding Error (Main Issue)
The most critical failure is a **Unicode encoding error** that appears consistently across all CLI tests:

```
Error: 'charmap' codec can't encode characters in position 0-1: character maps to <undefined>
```

This error occurs when trying to output Unicode flag emojis (🇩🇪, 🇫🇷, etc.) to the Windows console, which uses the 'charmap' codec by default and cannot handle Unicode emoji characters.

### Affected Test Categories

#### 1. CLI Module Tests (`tests/test_cli.py`) - 57 failures
All CLI tests fail due to the Unicode encoding issue when trying to output flag emojis:
- `test_help_displays_correctly`
- `test_countries_flag_single_country` 
- `test_countries_flag_multiple_countries`
- All positional argument tests
- All output format tests (JSON, CSV, text)
- Entrypoint tests

#### 2. Core Module Tests (`tests/test_countryflag.py`) - 5 failures
- `test_runas_module` - Unicode encoding error
- `test_entrypoint` - Entrypoint not found/working
- `test_example_command` - Unicode encoding error
- `test_cli_singlecountry` - Unicode encoding error
- `test_cli_multiplecountries` - Unicode encoding error

#### 3. Error Handling Tests (`tests/test_error_handling.py`) - 3 failures
- All fail due to Unicode encoding when testing valid output

#### 4. Integration Tests (`tests/test_final_error_integration.py`) - 3 failures
- All fail due to Unicode encoding issues

#### 5. Other Issues
- Some tests expect specific error messages that don't match current implementation
- Entrypoint scripts not properly installed/accessible

## Key Technical Issues Identified

### 1. Windows Console Unicode Support
The primary issue is that Windows console (cmd/PowerShell) uses 'charmap' encoding which cannot display Unicode emoji characters. This affects all tests that expect emoji output.

### 2. Entrypoint Installation
Multiple tests fail because the `countryflag` and `countryflag.exe` commands are not available in the PATH, suggesting entrypoint installation issues.

### 3. Error Message Mismatches
Some tests expect specific error messages like "country names cannot be empty" but get "Country not found" instead.

## Successful Test Categories
- Performance benchmarks (all passing)
- Property-based tests (all passing) 
- Memory cache tests (all passing)
- Lookup tests (all passing)
- Core functionality tests (most passing)

## Next Steps for Fixes
1. **Priority 1**: Fix Unicode output encoding for Windows console
2. **Priority 2**: Fix entrypoint installation and accessibility
3. **Priority 3**: Align error messages with test expectations
4. **Priority 4**: Test fixes iteratively on this Windows environment

## Environment Validation
This Windows 10 environment successfully reproduces the CI failures, providing an ideal testing ground for implementing and validating fixes before pushing to CI.
