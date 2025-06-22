"""
Base plugin interface for the countryflag package.

This module contains the BasePlugin interface that all plugins must implement.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from countryflag.core.models import CountryInfo


class BasePlugin(ABC):
    """
    Abstract base class for plugins.

    This class defines the interface that all plugins must adhere to.
    """

    @abstractmethod
    def get_country_info(self, name: str) -> Optional[CountryInfo]:
        """
        Get country information for a given country name.

        Args:
            name: The country name to look up.

        Returns:
            CountryInfo: The country information, or None if the country is not found.
        """
        pass

    @abstractmethod
    def get_supported_countries(self) -> List[CountryInfo]:
        """
        Get a list of supported countries.

        Returns:
            List[CountryInfo]: A list of country information objects.
        """
        pass

    @abstractmethod
    def get_supported_regions(self) -> List[str]:
        """
        Get a list of supported regions/continents.

        Returns:
            List[str]: A list of supported regions/continents.
        """
        pass

    @abstractmethod
    def get_countries_by_region(self, region: str) -> List[CountryInfo]:
        """
        Get countries in a specific region/continent.

        Args:
            region: The region/continent name.

        Returns:
            List[CountryInfo]: A list of countries in the specified region.
        """
        pass

    @abstractmethod
    def convert_country_name(self, name: str, to_format: str) -> str:
        """
        Convert a country name to the specified format.

        Args:
            name: The country name to convert.
            to_format: The format to convert to (e.g., "ISO2", "ISO3").

        Returns:
            str: The converted country code, or "not found" if the country is not found.
        """
        pass

    @abstractmethod
    def get_flag(self, country_name: str) -> Optional[str]:
        """
        Get the flag emoji for a country name.

        Args:
            country_name: The country name to get the flag for.

        Returns:
            str: The flag emoji, or None if the country is not found.
        """
        pass

    @abstractmethod
    def reverse_lookup(self, flag_emoji: str) -> Optional[str]:
        """
        Get the country name for a flag emoji.

        Args:
            flag_emoji: The flag emoji to look up.

        Returns:
            str: The country name, or None if the flag is not found.
        """
        pass
