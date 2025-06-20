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
countryflag Germany BE Spain 'United States of America'

# Custom separator
countryflag --separator "|" Germany France Italy

# Fuzzy matching
countryflag --fuzzy Germny Frnace Itly

# Get European flags
countryflag --region Europe

# Interactive mode
countryflag --interactive
```

## Advanced Features

### Caching

```python
from countryflag.core import CountryFlag
from countryflag.cache import MemoryCache, DiskCache

# Memory cache
cache = MemoryCache()
cf = CountryFlag(cache=cache)

# Disk cache
cache = DiskCache("/path/to/cache")
cf = CountryFlag(cache=cache)
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

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details on how to submit pull requests, report issues, and contribute to the project.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

This package depends on:
* [Country Converter (coco)](https://pypi.org/project/country-converter/) by [Konstantin Stadler](https://pypi.org/user/konstantinstadler/)
* [Emoji-country-flag](https://pypi.org/project/emoji-country-flag/) by [cuzi](https://pypi.org/user/cuzi/)
