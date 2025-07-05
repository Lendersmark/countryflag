# Developer Notes - CountryFlag Project

## Project Overview
- **Repository**: https://github.com/Lendersmark/countryflag
- **Documentation**: https://countryflag.readthedocs.io/en/latest/
- **Package**: Python library for converting country names to emoji flags
- **Current Version**: 1.1.1

## Technical Stack
- **Python**: 3.9, 3.10, 3.11, 3.12 support
- **Build System**: setuptools with pyproject.toml (PEP-517)
- **Testing**: pytest + pytest-cov + pytest-benchmark
- **Linting**: black + isort + flake8 + mypy
- **Documentation**: Sphinx + sphinx-rtd-theme
- **CI/CD**: GitHub Actions (Ubuntu, Windows, macOS)
- **Coverage**: Codecov integration
- **Environment Management**: tox for isolated testing

## Project Structure
```
countryflag/
├── src/countryflag/           # Main package source
│   ├── cli/                   # Command-line interface
│   ├── core/                  # Core functionality
│   ├── cache/                 # Caching implementations
│   ├── utils/                 # Utilities
│   └── plugins/               # Plugin system
├── tests/                     # Test suite
│   ├── unit/                  # Unit tests
│   ├── stress/                # Stress/performance tests
│   ├── performance/           # Benchmark tests
│   └── property/              # Property-based tests
├── docs/                      # Sphinx documentation
└── examples/                  # Usage examples
```

## Platform-Aware Testing Configuration

### Timing Thresholds (Implemented June 2025)
- **Windows**: 2.5x threshold (accounts for NTFS, antivirus, CI overhead)
- **Linux/macOS**: 1.8x threshold (moderate for CI variability)
- **Fast Machines**: 1.2x threshold (strict, via FAST_MACHINE=1|true|yes)
- **Small Timing Guard**: Skip assertions for operations < 0.0001s

### Key Files
- `platform_timing_logic.py` - Core timing logic implementation
- `tests/stress/test_large_datasets.py` - Uses conditional timing assertions
|- `examples/example_timing_test.py` - Demonstrates timing logic usage
- `README_TIMING_LOGIC.md` - Comprehensive documentation

## CI/CD Configuration

### GitHub Actions (.github/workflows/ci.yml)
- **Test Matrix**: 3 OS × 4 Python versions = 12 test combinations
- **Jobs**: test, lint, docs, build-test
- **Coverage**: Uploads to Codecov with XML reports

### Tox Environments (tox.ini)
- `py39,py310,py311,py312` - Python version testing
- `flake8` - Code style and linting
- `mypy` - Type checking
- `docs` - Documentation building
- `build` - PEP-517 build process testing

## Development Tools Configuration

### Code Quality
- **black**: Line length 88, Python 3.9+ target
- **isort**: Black-compatible profile
- **flake8**: Max line length 120, custom ignore rules
- **mypy**: Python 3.10 target, strict typing (with platform-specific ignores)

### Testing
- **pytest**: Coverage reporting, benchmarking support
- **hypothesis**: Property-based testing
- **pytest-benchmark**: Performance benchmarking

## Service Integrations

### ReadTheDocs
- **URL**: https://countryflag.readthedocs.io/
- **Config**: .readthedocs.yml (Python 3.10, ubuntu-22.04)
- **Build**: Sphinx with RTD theme
- **Formats**: HTML, PDF, HTMLZip

### Codecov
- **Config**: pytest generates coverage.xml
- **Upload**: GitHub Actions with CODECOV_TOKEN
- **Coverage**: Currently ~23% baseline

## Recent Major Changes (June 2025)

### Platform-Aware Timing Logic
- Added comprehensive timing logic to prevent flaky CI failures
- Windows gets lenient thresholds due to I/O overhead
- Linux/macOS get moderate thresholds for CI reliability
- Fast machines can use strict thresholds for development
- All changes documented and tested on Windows

### Configuration Fixes
- Fixed ReadTheDocs version mismatch (0.2.0 → 1.1.1)
- Updated mypy configuration syntax and Python target
- Added py.typed marker for type checking
- Configured Codecov XML report generation
- Applied code formatting fixes for lint compliance

## Commands Reference

### Local Development
```bash
# Install development dependencies
pip install -e .[dev]

# Run all tests
tox

# Run specific test environments
tox -e py310        # Python 3.10 tests
tox -e flake8       # Linting
tox -e mypy         # Type checking
tox -e docs         # Build documentation

# Run tests with coverage
pytest --cov=countryflag --cov-report=term-missing --cov-report=xml

# Format code
black src tests examples
isort src tests examples
```

### Platform Testing
```bash
# Test with Windows timing thresholds (default on Windows)
pytest tests/stress/

# Test with fast machine timing thresholds
FAST_MACHINE=1 pytest tests/stress/

# Test platform timing logic
python platform_timing_logic.py
python examples/example_timing_test.py
```

## Environment Variables
- `FAST_MACHINE=1|true|yes` - Enable strict timing thresholds
- `CODECOV_TOKEN` - Required for Codecov uploads in CI

## Dependencies Management
- **Runtime**: emoji-country-flag, country_converter, typeguard, prompt_toolkit, aioconsole
- **Development**: black, isort, mypy, pytest, pytest-cov, tox, sphinx, flake8 + extensions
- **Testing**: pytest-benchmark, hypothesis, psutil, cli_test_helpers

## Demo File Cleanup (June 2025)

### Retention/Deletion Decisions
- **KEEP**: `demo_cache_sharing.py` - Useful cache-sharing demonstration
- **KEEP**: `example_timing_test.py` - Timing-logic demonstration and reference

*Rationale: Keep educational demos that demonstrate specific features, remove development scaffolding that has been superseded by proper test coverage.*

## Notes for Future Development
- All tests must pass on Windows, Linux, and macOS
- Performance tests use platform-aware timing to prevent flaky failures
- Documentation must build without errors (warnings are acceptable)
- Code must pass black formatting and mypy type checking
- New features should include comprehensive tests and documentation
