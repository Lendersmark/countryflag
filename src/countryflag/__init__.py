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

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

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
__version__ = "1.0.1"
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
    country_names: List[str], separator: str = " "
) -> Union[str, Tuple[str, List[Tuple[str, str]]]]:
    """
    Convert country names to emoji flags.

    This is a convenience function that creates a CountryFlag instance and calls
    get_flag() on it. For backward compatibility, it returns just the string of
    flags by default, but can optionally return the full tuple with pairs.

    Args:
        country_names: A list of country names to convert to flags.
        separator: The separator to use between flags (default: space).

    Returns:
        str: A string containing emoji flags separated by the specified separator.

    Raises:
        InvalidCountryError: If a country name cannot be converted to a flag.

    Example:
        >>> getflag(['Germany', 'BE', 'United States of America', 'Japan'])
        '🇩🇪 🇧🇪 🇺🇸 🇯🇵'
    """
    cf = CountryFlag()
    flags, pairs = cf.get_flag(country_names, separator)

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


__all__ = [
    "getflag",
    "CountryFlag",
    "CountryFlagError",
    "InvalidCountryError",
    "ReverseConversionError",
    "RegionError",
    "CacheError",
    "PluginError",
]
