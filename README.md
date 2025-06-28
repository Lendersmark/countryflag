# CountryFlag

[![PyPI version](https://img.shields.io/pypi/v/countryflag.svg)](https://pypi.org/project/countryflag/)
[![Python versions](https://img.shields.io/pypi/pyversions/countryflag.svg)](https://pypi.org/project/countryflag/)
[![Documentation Status](https://readthedocs.org/projects/countryflag/badge/?version=latest)](https://countryflag.readthedocs.io/en/latest/?badge=latest)
[![License](https://img.shields.io/github/license/Lendersmark/countryflag)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Build Status](https://github.com/Lendersmark/countryflag/actions/workflows/ci.yml/badge.svg)](https://github.com/Lendersmark/countryflag/actions)
[![Coverage](https://codecov.io/gh/Lendersmark/countryflag/branch/main/graph/badge.svg)](https://codecov.io/gh/Lendersmark/countryflag)

CountryFlag is a Python package for converting country names into emoji flags.

## Features

* Convert country names to emoji flags 🏁
* Support for reverse lookup (flag to country name)
* Support for region/continent grouping
* Multiple output formats (text, JSON, CSV)
* Fuzzy matching for country names
* Interactive CLI mode with autocompletion
* Asynchronous and parallel processing
* Comprehensive caching system

## Installation

```bash
pip install countryflag
```

## Quick Start

### Python API

```python
import countryflag

# Convert country names to flags
countries = ['Germany', 'BE', 'United States of America', 'Japan']
flags = countryflag.getflag(countries)
print(flags)  # 🇩🇪 🇧🇪 🇺🇸 🇯🇵

# Using the core class
from countryflag.core import CountryFlag

cf = CountryFlag()
flags, pairs = cf.get_flag(["United States", "Canada", "Mexico"])
print(flags)  # 🇺🇸 🇨🇦 🇲🇽
```

### Command Line Interface

```bash
# Basic usage
countryflag --countries Germany BE Spain 'United States of America'

# Custom separator
countryflag --separator "|" --countries Germany France Italy

# Fuzzy matching
countryflag --fuzzy --countries Germny Frnace Itly

# Get European flags
countryflag --region Europe

# Interactive mode
countryflag --interactive

# Output formats
countryflag --format json --countries Germany France
countryflag --format csv --countries Germany France

# List all supported countries
countryflag --list-countries

# List all supported regions
countryflag --list-regions

# Validate a country name
countryflag --validate "Germany"

# Reverse lookup (flag to country)
countryflag --reverse 🇩🇪 🇫🇷 🇺🇸

# Process files
countryflag --file countries.txt
countryflag --files file1.txt file2.txt
```

## CLI Reference

### Available Options

| Option | Short | Description |
|--------|-------|-------------|
| `--countries` | | Country names to convert (space-separated) |
| `--file` | `-i` | Process a file with country names (one per line) |
| `--files` | | Process multiple files in parallel |
| `--reverse` | `-r` | Convert flag emojis to country names |
| `--region` | | Get flags for all countries in a region |
| `--interactive` | `-I` | Run in interactive mode with autocompletion |
| `--format` | `-f` | Output format: `text`, `json`, or `csv` |
| `--separator` | `-s` | Character to separate flags (default: space) |
| `--fuzzy` | `-z` | Enable fuzzy matching for country names |
| `--threshold` | `-t` | Similarity threshold for fuzzy matching (0-1) |
| `--language` | `-l` | Language for country names (ISO 639-1 code) |
| `--verbose` | `-v` | Enable verbose logging |
| `--list-countries` | | List all supported countries |
| `--list-regions` | | List all supported regions |
| `--validate` | | Validate a country name |
| `--cache` | `-c` | Enable caching |
| `--cache-dir` | | Directory for cache files |
| `--async` | `-a` | Use asynchronous file processing |
| `--workers` | `-w` | Number of worker threads for parallel processing |

### Supported Regions

- Africa
- Americas  
- Asia
- Europe
- Oceania

## Troubleshooting

### Common Issues

**1. "More than one regular expression match" warnings**

These warnings indicate that the country matching algorithm found multiple potential matches. The tool will still work correctly and output the correct flags, but you may see warning messages. This is a known issue that doesn't affect functionality.

**2. Country not found**

Try using the `--fuzzy` flag for fuzzy matching:
```bash
countryflag --fuzzy --countries "Untied States"  # Will match "United States"
```

**3. Multi-word country names**

Always quote multi-word country names:
```bash
countryflag --countries "United States of America" "United Kingdom"
```

**4. Check available countries**

To see all supported country names:
```bash
countryflag --list-countries
```

## Advanced Features

### Caching

CountryFlag includes automatic cache sharing for improved performance:

```python
from countryflag.core import CountryFlag
from countryflag.cache import MemoryCache, DiskCache

# Automatic cache sharing (new in v1.0.1, enhanced in v1.1.0)
cf1 = CountryFlag()  # Uses global shared cache
cf2 = CountryFlag()  # Shares same cache as cf1

# First call (cache miss)
flags1, _ = cf1.get_flag(["Germany"])

# Second call from different instance (cache hit!)
flags2, _ = cf2.get_flag(["Germany"])  # Much faster

# Custom cache (if needed)
cache = MemoryCache()
cf = CountryFlag(cache=cache)  # Uses independent cache

# Clear global cache (useful for testing)
CountryFlag.clear_global_cache()
```

### Region-Based Lookup

```python
# Get all European flags
flags, pairs = cf.get_flags_by_region("Europe")
print(f"Found {len(pairs)} European countries")
```

### Reverse Lookup

```python
# Convert flags back to country names
flags = ["🇺🇸", "🇯🇵", "🇩🇪"]
pairs = cf.reverse_lookup(flags)
for flag, country in pairs:
    print(f"{flag} is {country}")
```

### Asynchronous Processing

```python
import asyncio
from countryflag.utils.io import process_file_input_async

async def process_large_file():
    countries = await process_file_input_async("countries.txt")
    cf = CountryFlag()
    flags, pairs = cf.get_flag(countries)
    print(flags)

asyncio.run(process_large_file())
```

## Documentation

For complete documentation, visit [countryflag.readthedocs.io](https://countryflag.readthedocs.io/).

## Contributing

Contributions are welcome! Please read our [Contributing Guide](docs/CONTRIBUTING.md) for details on how to submit pull requests, report issues, and contribute to the project.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

This package depends on:
* [Country Converter (coco)](https://pypi.org/project/country-converter/) by [Konstantin Stadler](https://pypi.org/user/konstantinstadler/)
* [Emoji-country-flag](https://pypi.org/project/emoji-country-flag/) by [cuzi](https://pypi.org/user/cuzi/)
