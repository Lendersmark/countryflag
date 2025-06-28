# PEP-517 Build Process Migration

This document explains the changes made to ensure the test environment uses the PEP-517 build process after removing `install_requires` from setup.py.

## Changes Made

### 1. Dependencies Management
- **Removed**: `install_requires` from `setup.py` (already done in previous steps)
- **Current**: All dependencies are now managed in `pyproject.toml` under `[project.dependencies]`
- **Effect**: Ensures single source of truth for dependency management

### 2. Build System Configuration
The project already had proper PEP-517 configuration:
- `pyproject.toml` contains `[build-system]` with `setuptools.build_meta` backend
- `tox.ini` has `isolated_build = True` which enables PEP-517 builds
- This ensures all environments use the modern build process

### 3. Test Environment Updates

#### tox.ini Changes
- **Added**: New `[testenv:build]` environment that explicitly tests the PEP-517 build workflow
- **Process**: `python -m build` → `pip install dist/*.whl` → `pytest`
- **Purpose**: Validates that the build → install → test process works correctly

#### CI Workflow (.github/workflows/ci.yml) Changes
- **Added**: New `build-test` job that runs the explicit PEP-517 build test
- **Added**: Comments clarifying that tox uses PEP-517 due to `isolated_build = True`
- **Effect**: Every CI job now uses the PEP-517 build process

## How It Works

### Standard Test Environments (py39, py310, etc.)
1. tox creates an isolated build environment
2. Uses PEP-517 to build the package from `pyproject.toml`
3. Installs the package with `.[test]` extra dependencies
4. Runs pytest

### Explicit Build Test Environment
1. Builds the package using `python -m build` (PEP-517)
2. Installs the built wheel with `pip install dist/*.whl`
3. Runs tests to verify the installed package works

## Benefits

1. **Consistency**: All environments use the same build process
2. **Modern Standards**: Follows PEP-517 and PEP-518 specifications
3. **Reliability**: Dependencies are resolved from `pyproject.toml` consistently
4. **Isolation**: Build environments are isolated from the host environment
5. **Validation**: Explicit test ensures the build → install → test workflow works

## Running Tests

```bash
# Run all tests (uses PEP-517 automatically)
tox

# Run specific environment
tox -e py39

# Test explicit PEP-517 build process
tox -e build

# Manual PEP-517 build
python -m build
pip install dist/*.whl
```

## Verification

The setup has been verified to work correctly:
- ✅ `python -m build` successfully creates sdist and wheel
- ✅ Dependencies are properly resolved from `pyproject.toml`
- ✅ All test environments use isolated builds
- ✅ CI workflow includes explicit PEP-517 testing
