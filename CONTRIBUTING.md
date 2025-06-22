# Contributing to CountryFlag

Thank you for considering contributing to CountryFlag! This document provides guidelines and instructions for contributing to this project.

## Code of Conduct

By participating in this project, you are expected to uphold our Code of Conduct: be respectful, considerate, and collaborative.

## How to Contribute

### Reporting Bugs

- Check if the bug has already been reported in the [Issues](https://github.com/lendersmark/countryflag/issues)
- If not, create a new issue with a clear title and description
- Include steps to reproduce, expected behavior, and actual behavior
- Include screenshots if applicable
- Specify the version of CountryFlag you're using

### Suggesting Enhancements

- Check if the enhancement has already been suggested in the [Issues](https://github.com/lendersmark/countryflag/issues)
- If not, create a new issue with a clear title and description
- Explain why this enhancement would be useful to most users
- Include any relevant examples or mockups

### Pull Requests

1. Fork the repository
2. Create a new branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run the tests (`pytest`)
5. Run the linters (`pre-commit run --all-files`)
6. Commit your changes (`git commit -m 'Add some amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## Development Environment

### Setup

1. Install Python 3.6 or newer
2. Clone the repository: `git clone https://github.com/lendersmark/countryflag.git`
3. Create a virtual environment: `python -m venv venv`
4. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Unix/macOS: `source venv/bin/activate`
5. Install development dependencies: `pip install -e ".[dev]"`
6. Install pre-commit hooks: `pre-commit install`

### Testing

- Run tests: `pytest`
- Run tests with coverage: `pytest --cov=countryflag`
- Run specific tests: `pytest tests/test_specific.py`
- Run property-based tests: `pytest tests/property`
- Run performance tests: `pytest tests/performance`

**Note**: Cache hit assertions in tests rely on the `MemoryCache.get_hits()` method to verify caching behavior.

### Documentation

- Build documentation: `sphinx-build -b html docs/source docs/build/html`
- View documentation: open `docs/build/html/index.html` in your browser

## Project Structure

```
countryflag/
├── src/
│   └── countryflag/        # Main package code
│       ├── core/           # Core functionality
│       ├── cli/            # Command-line interface
│       ├── plugins/        # Plugin system
│       └── cache/          # Caching system
├── tests/                  # Test suite
│   ├── unit/               # Unit tests
│   ├── integration/        # Integration tests
│   ├── performance/        # Performance benchmarks
│   └── property/           # Property-based tests
└── docs/                   # Documentation
```

## Style Guide

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) for code style
- Use [Google style](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings) for docstrings
- Use type hints for all function parameters and return values
- Write tests for all new functionality
- Keep lines under 88 characters
- Use descriptive variable names

## Commit Message Guidelines

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests after the first line

## Release Process

1. Update version number in `src/countryflag/__init__.py` and `pyproject.toml`
2. Update CHANGELOG.md with the new version and changes
3. Create a new release on GitHub with the version number as the tag

## Questions?

If you have any questions, feel free to create an issue or reach out to the maintainers.

Thank you for your contributions!
