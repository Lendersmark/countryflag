"""
Core functionality for the countryflag package.

This package contains the core models, exceptions, and functionality for converting
country names to emoji flags and vice versa.
"""

from countryflag.core.converters import CountryConverterSingleton
from countryflag.core.exceptions import (
    CountryFlagError,
    InvalidCountryError,
    RegionError,
    ReverseConversionError,
)
from countryflag.core.flag import CountryFlag
from countryflag.core.models import CountryInfo

__all__ = [
    "CountryFlagError",
    "InvalidCountryError",
    "ReverseConversionError",
    "RegionError",
    "CountryInfo",
    "CountryConverterSingleton",
    "CountryFlag",
]
