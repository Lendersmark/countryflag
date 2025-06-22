"""
Exceptions for the countryflag package.

This module contains custom exceptions raised by the countryflag package.
"""

from typing import Optional


class CountryFlagError(Exception):
    """
    Base exception for countryflag errors.

    This is the base class for all exceptions raised by the countryflag package.

    Attributes:
        message: The error message.
    """

    __slots__ = ("message",)

    def __init__(self, message: str) -> None:
        """
        Initialize the exception.

        Args:
            message: The error message.
        """
        self.message = message
        super().__init__(message)


class InvalidCountryError(CountryFlagError):
    """
    Exception raised when an invalid country name is provided.

    This exception is raised when a country name cannot be converted to an ISO2 code.

    Attributes:
        message: The error message.
        country: The invalid country name.
    """

    __slots__ = ("country",)

    def __init__(self, message: str, country: str) -> None:
        """
        Initialize the exception.

        Args:
            message: The error message.
            country: The invalid country name.
        """
        self.country = country
        super().__init__(message)


class ReverseConversionError(CountryFlagError):
    """
    Exception raised when a flag emoji cannot be converted to a country name.

    This exception is raised when a flag emoji cannot be mapped to a country name.

    Attributes:
        message: The error message.
        flag: The flag emoji that could not be converted.
    """

    __slots__ = ("flag",)

    def __init__(self, message: str, flag: str) -> None:
        """
        Initialize the exception.

        Args:
            message: The error message.
            flag: The flag emoji that could not be converted.
        """
        self.flag = flag
        super().__init__(message)


class RegionError(CountryFlagError):
    """
    Exception raised when an invalid region is provided.

    This exception is raised when a region name is not recognized.

    Attributes:
        message: The error message.
        region: The invalid region name.
    """

    __slots__ = ("region",)

    def __init__(self, message: str, region: str) -> None:
        """
        Initialize the exception.

        Args:
            message: The error message.
            region: The invalid region name.
        """
        self.region = region
        super().__init__(message)


class CacheError(CountryFlagError):
    """
    Exception raised when there is an error with the cache.

    This exception is raised when there is an error reading from or writing to the cache.

    Attributes:
        message: The error message.
        key: The cache key that caused the error (optional).
    """

    __slots__ = ("key",)

    def __init__(self, message: str, key: Optional[str] = None) -> None:
        """
        Initialize the exception.

        Args:
            message: The error message.
            key: The cache key that caused the error (optional).
        """
        self.key = key
        super().__init__(message)


class PluginError(CountryFlagError):
    """
    Exception raised when there is an error with a plugin.

    This exception is raised when there is an error loading or using a plugin.

    Attributes:
        message: The error message.
        plugin_name: The name of the plugin that caused the error (optional).
    """

    __slots__ = ("plugin_name",)

    def __init__(self, message: str, plugin_name: Optional[str] = None) -> None:
        """
        Initialize the exception.

        Args:
            message: The error message.
            plugin_name: The name of the plugin that caused the error (optional).
        """
        self.plugin_name = plugin_name
        super().__init__(message)
