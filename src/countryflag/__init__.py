"""
CountryFlag - A Python package for converting country names into emoji flags.

This package provides functionality to convert country names to emoji flags and vice versa,
with support for various formats, fuzzy matching, and region/continent grouping.

Features:
- Convert country names to emoji flags
- Reverse lookup (flag to country name)
- Region/continent grouping
- Multiple output formats (text, JSON, CSV)
- Fuzzy matching for country names
- Interactive CLI mode with autocompletion
- Asynchronous and parallel processing
- Memory and disk caching for improved performance

Example:
    >>> import countryflag
    >>> countryflag.getflag(['Germany', 'BE', 'United States', 'Japan'])
    '🇩🇪 🇧🇪 🇺🇸 🇯🇵'

For more advanced usage, use the core classes directly:
    >>> from countryflag.core import CountryFlag
    >>> cf = CountryFlag()
    >>> flags, pairs = cf.get_flag(['Germany', 'France', 'Italy'])
    >>> flags
    '🇩🇪 🇫🇷 🇮🇹'

For more information, see the documentation at:
https://countryflag.readthedocs.io/
"""

import logging
import os
import platform
import sys
from typing import Any, Dict, List, Optional, Tuple, Union

from countryflag.core.exceptions import (
    CacheError,
    CountryFlagError,
    InvalidCountryError,
    PluginError,
    RegionError,
    ReverseConversionError,
)

# Import core functionality
from countryflag.core.flag import CountryFlag

# Package metadata
__version__ = "1.1.1"
__author__ = "Lendersmark"
__license__ = "MIT"
__copyright__ = "Copyright 2025 Lendersmark"
__email__ = "author@example.com"
__status__ = "Production"


# Define platform-specific optimizations
def _setup_platform_optimizations() -> None:
    """Set up platform-specific optimizations."""
    # Check if we're running on PyPy
    if platform.python_implementation() == "PyPy":
        # PyPy-specific optimizations (if any)
        pass

    # Windows-specific optimizations
    if sys.platform.startswith("win"):
        # Windows doesn't render emoji flags correctly in many terminals
        # We could add a Windows-specific renderer or warning here
        pass

    # macOS-specific optimizations
    elif sys.platform == "darwin":
        # macOS has good emoji support, no special handling needed
        pass

    # Linux-specific optimizations
    elif sys.platform.startswith("linux"):
        # Check terminal capabilities for emoji support
        pass


# Run platform-specific optimizations on import
_setup_platform_optimizations()


def getflag(
    countries: Union[str, List[str]], separator: str = " "
) -> Union[str, Tuple[str, List[Tuple[str, str]]]]:
    """
    Convert country names to emoji flags.

    This is a convenience function that creates a CountryFlag instance and calls
    get_flag() on it. For backward compatibility, it returns just the string of
    flags by default, but can optionally return the full tuple with pairs.

    Args:
        countries: A single country name or list of country names to convert to flags.
        separator: The separator to use between flags (default: space).

    Returns:
        str: A string containing emoji flags separated by the specified separator.

    Raises:
        TypeError: If countries argument is not a string or list of strings.
        InvalidCountryError: If a country name cannot be converted to a flag.

    Example:
        >>> getflag(['Germany', 'BE', 'United States of America', 'Japan'])
        '🇩🇪 🇧🇪 🇺🇸 🇯🇵'
    """
    # Type checking for defensive programming
    if countries is None:
        raise TypeError(
            "countries argument cannot be None. Expected a string or list of strings."
        )

    if not isinstance(countries, (str, list)):
        raise TypeError(
            f"countries argument must be a string or list of strings, got {type(countries).__name__}"
        )

    # Convert single string to list for compatibility with core implementation
    if isinstance(countries, str):
        countries = [countries]

    cf = CountryFlag()
    flags, pairs = cf.get_flag(countries, separator)

    # Check if we're being called from a module that imports from v0.2.0
    # If so, return the full result (flags, pairs)
    frame = sys._getframe(1)
    if (
        frame
        and "self" in frame.f_locals
        and hasattr(frame.f_locals["self"], "__module__")
    ):
        module = frame.f_locals["self"].__module__
        if module.startswith("countryflag.") and not module == "countryflag.cli.main":
            return flags, pairs

    # Otherwise, maintain backward compatibility by returning just the flags string
    return flags


def get_ascii_flag(country_name: str) -> str:
    """
    Get ASCII art flag for a country, with fallback to Unicode emoji.

    This is a convenience function that creates a CountryFlag instance and calls
    get_ascii_flag() on it. It attempts to load ASCII art from embedded resources,
    falling back to Unicode emoji flags when resources are missing.

    Args:
        country_name: The country name or ISO code.

    Returns:
        str: ASCII art flag if available, otherwise Unicode emoji flag.

    Raises:
        TypeError: If country_name is not a string.
        InvalidCountryError: If the country name cannot be converted.

    Example:
        >>> result = get_ascii_flag("DE")
        >>> isinstance(result, str)
        True
    """
    # Type checking for defensive programming
    if country_name is None:
        raise TypeError("country_name argument cannot be None. Expected a string.")

    if not isinstance(country_name, str):
        raise TypeError(
            f"country_name argument must be a string, got {type(country_name).__name__}"
        )

    cf = CountryFlag()
    return cf.get_ascii_flag(country_name)


__all__ = [
    "getflag",
    "get_ascii_flag",
    "CountryFlag",
    "CountryFlagError",
    "InvalidCountryError",
    "ReverseConversionError",
    "RegionError",
    "CacheError",
    "PluginError",
]
