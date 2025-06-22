"""
Country flag functionality for the countryflag package.

This module contains the CountryFlag class that provides methods for converting
country names to emoji flags and vice versa.
"""

import csv
import json
import logging
from io import StringIO
from typing import Any, Dict, List, Literal, Optional, Tuple, cast

import flag

from countryflag.cache.base import Cache
from countryflag.core.converters import CountryConverterSingleton
from countryflag.core.exceptions import (
    InvalidCountryError,
    RegionError,
    ReverseConversionError,
)
from countryflag.core.models import CountryInfo

# Configure logging
logger = logging.getLogger("countryflag.flag")

# Type definitions
RegionType = Literal["Africa", "Americas", "Asia", "Europe", "Oceania"]
OutputFormatType = Literal["text", "json", "csv"]


class CountryFlag:
    """
    Class to handle country flag operations.

    This class provides methods for converting country names to emoji flags,
    reverse lookup (flag to country name), and region-based operations.

    Attributes:
        _converter: The CountryConverterSingleton instance.
        _language: The language code for output.
        _cache: The cache instance to use (optional).

    Example:
        >>> cf = CountryFlag()
        >>> flags, _ = cf.get_flag(["United States", "Canada", "Mexico"])
        >>> flags
        '🇺🇸 🇨🇦 🇲🇽'
    """

    __slots__ = ("_converter", "_language", "_cache")

    def __init__(self, language: str = "en", cache: Optional[Cache] = None) -> None:
        """
        Initialize the CountryFlag class.

        Args:
            language: The language code for output (default: 'en').
            cache: The cache instance to use (optional).
        """
        self._converter = CountryConverterSingleton()
        self._language = language
        self._cache = cache

    def set_language(self, language: str) -> None:
        """
        Set the language for country names.

        Args:
            language: The ISO 639-1 language code.
        """
        self._language = language

    def validate_country_name(self, country_name: str) -> bool:
        """
        Validate if a country name can be converted to an ISO2 code.

        Args:
            country_name: The country name to validate.

        Returns:
            bool: True if the country name is valid, False otherwise.

        Example:
            >>> cf = CountryFlag()
            >>> cf.validate_country_name("United States")
            True
            >>> cf.validate_country_name("Not a Country")
            False
        """
        if not country_name or not isinstance(country_name, str):
            return False

        try:
            # Check cache first if available
            if self._cache:
                cache_key = f"validate_{country_name}"
                cached_result = self._cache.get(cache_key)
                if cached_result is not None:
                    return cached_result

            code = self._converter.convert(country_name)
            result = code != "not found"

            # Cache the result if cache is available
            if self._cache:
                self._cache.set(cache_key, result)

            return result
        except Exception:
            return False

    def get_supported_countries(self) -> List[Dict[str, str]]:
        """
        Get a list of supported country names and their ISO2 codes.

        Returns:
            List[Dict[str, str]]: A list of dictionaries containing country information.

        Example:
            >>> cf = CountryFlag()
            >>> countries = cf.get_supported_countries()
            >>> len(countries) > 0
            True
        """
        # Check cache first if available
        if self._cache:
            cache_key = "supported_countries"
            cached_result = self._cache.get(cache_key)
            if cached_result is not None:
                return cached_result

        # Create a list of dictionaries with country information
        countries = []
        for _, row in self._converter.data.iterrows():
            if row["ISO2"] != "not found":
                countries.append(
                    {
                        "name": row["name_short"],
                        "iso2": row["ISO2"],
                        "iso3": row["ISO3"],
                        "official_name": row["name_official"],
                    }
                )

        # Cache the result if cache is available
        if self._cache:
            self._cache.set(cache_key, countries)

        return countries

    def get_flags_by_region(
        self, region: RegionType, separator: str = " "
    ) -> Tuple[str, List[Tuple[str, str]]]:
        """
        Get flags for all countries in a specific region/continent.

        Args:
            region: The region/continent name (e.g., "Europe", "Asia").
            separator: The separator to use between flags (default: space).

        Returns:
            Tuple[str, List[Tuple[str, str]]]: A tuple containing the flags string and
                a list of (country_name, flag) pairs.

        Raises:
            RegionError: If the region is not supported.

        Example:
            >>> cf = CountryFlag()
            >>> flags, pairs = cf.get_flags_by_region("Europe")
            >>> len(pairs) > 0
            True
        """
        # Check cache first if available
        if self._cache:
            cache_key = f"flags_by_region_{region}_{separator}"
            cached_result = self._cache.get(cache_key)
            if cached_result is not None:
                return cached_result

        try:
            countries = self._converter.get_countries_by_region(region)
            country_names = [country.name for country in countries]
            result = self.get_flag(country_names, separator)

            # Cache the result if cache is available
            if self._cache:
                self._cache.set(cache_key, result)

            return result
        except RegionError as re:
            logger.error(f"Error getting flags for region '{region}': {re}")
            raise

    def get_flag(
        self,
        country_names: List[str],
        separator: str = " ",
        fuzzy_matching: bool = False,
        fuzzy_threshold: float = 0.6,
    ) -> Tuple[str, List[Tuple[str, str]]]:
        """
        Convert country names to emoji flags.

        Args:
            country_names: A list of country names to convert to flags.
            separator: The separator to use between flags (default: space).
            fuzzy_matching: Whether to use fuzzy matching for country names.
            fuzzy_threshold: The similarity threshold for fuzzy matching (0-1).

        Returns:
            Tuple[str, List[Tuple[str, str]]]: A tuple containing the flags string and
                a list of (country_name, flag) pairs.

        Raises:
            InvalidCountryError: If a country name cannot be converted to a flag.

        Example:
            >>> cf = CountryFlag()
            >>> flags, pairs = cf.get_flag(["United States", "Canada"])
            >>> flags
            '🇺🇸 🇨🇦'
            >>> pairs
            [('United States', '🇺🇸'), ('Canada', '🇨🇦')]
        """
        if not country_names:
            logger.warning("Empty list of country names provided")
            return "", []

        # Check cache first if available and not using fuzzy matching
        if self._cache and not fuzzy_matching:
            cache_key = f"get_flag_{','.join(country_names)}_{separator}"
            cached_result = self._cache.get(cache_key)
            if cached_result is not None:
                return cached_result

        # Use a list for better performance when concatenating strings
        flags_list = []
        country_flag_pairs = []

        for i, country_name in enumerate(country_names):
            logger.debug(f"Processing country: {country_name}")

            if not country_name or not isinstance(country_name, str):
                logger.warning(f"Invalid input at position {i}: {country_name}")
                continue

            try:
                # Try direct conversion first
                country_code = self._converter.convert(country_name)

                # If not found and fuzzy matching is enabled, try to find close matches
                if country_code == "not found" and fuzzy_matching:
                    matches = self._converter.find_close_matches(
                        country_name, fuzzy_threshold
                    )
                    if matches:
                        # Use the best match
                        best_match, country_code = matches[0]
                        logger.info(
                            f"Using fuzzy match '{best_match}' for '{country_name}'"
                        )
                        country_name = best_match

                if country_code == "not found":
                    raise InvalidCountryError(
                        f"Country not found: {country_name}", country_name
                    )

                # Convert ISO2 code into flag
                emoji_flag = flag.flag(country_code)
                flags_list.append(emoji_flag)
                country_flag_pairs.append((country_name, emoji_flag))

            except ValueError as ve:
                logger.error(f"Error converting country '{country_name}': {ve}")
                raise InvalidCountryError(
                    f"Invalid country name: {country_name}", country_name
                ) from ve

        # Join the flags with the specified separator
        result = (separator.join(flags_list), country_flag_pairs)

        # Cache the result if cache is available and not using fuzzy matching
        if self._cache and not fuzzy_matching:
            self._cache.set(cache_key, result)

        return result

    def reverse_lookup(self, emoji_flags: List[str]) -> List[Tuple[str, str]]:
        """
        Convert emoji flags to country names with robust handling of edge cases.

        This method provides enhanced reverse lookup that handles:
        - Standard regional indicator flags (🇺🇸 → United States)
        - Alternative ISO codes (🇬🇧 and 🇺🇰 → United Kingdom)
        - Special territories (🇦🇨 → Ascension Island)
        - Regional indicator normalization

        Args:
            emoji_flags: A list of emoji flags to convert to country names.

        Returns:
            List[Tuple[str, str]]: A list of tuples containing (flag, country_name).

        Raises:
            ReverseConversionError: If a flag emoji cannot be converted to a country name.

        Example:
            >>> cf = CountryFlag()
            >>> pairs = cf.reverse_lookup(["🇺🇸", "🇬🇧", "🇺🇰", "🇦🇨"])
            >>> pairs
            [('🇺🇸', 'United States'), ('🇬🇧', 'United Kingdom'), ('🇺🇰', 'United Kingdom'), ('🇦🇨', 'Ascension Island')]
        """
        if not emoji_flags:
            logger.warning("Empty list of emoji flags provided")
            return []

        # Check cache first if available
        if self._cache:
            cache_key = f"reverse_lookup_{','.join(emoji_flags)}"
            cached_result = self._cache.get(cache_key)
            if cached_result is not None:
                return cached_result

        flag_to_country = self._converter.get_flag_to_country_mapping()
        result = []

        for i, emoji_flag in enumerate(emoji_flags):
            logger.debug(f"Processing flag: {emoji_flag}")

            if not isinstance(emoji_flag, str):
                logger.warning(f"Invalid input at position {i}: {emoji_flag}")
                continue

            if not emoji_flag:  # Empty string should raise an error
                error_msg = f"Cannot convert flag emoji to country name: {emoji_flag}"
                logger.error(error_msg)
                raise ReverseConversionError(error_msg, emoji_flag)

            # Use the enhanced reverse lookup from the lookup module
            from countryflag.lookup import reverse_lookup_flag

            country_name = reverse_lookup_flag(emoji_flag, flag_to_country)

            if country_name:
                # Normalize the flag for consistent output
                from countryflag.lookup import normalize_emoji_flag

                normalized_flag = normalize_emoji_flag(emoji_flag)
                result.append((normalized_flag, country_name))
            else:
                error_msg = f"Cannot convert flag emoji to country name: {emoji_flag}"
                logger.error(error_msg)
                raise ReverseConversionError(error_msg, emoji_flag)

        # Cache the result if cache is available
        if self._cache:
            self._cache.set(cache_key, result)

        return result

    def format_output(
        self,
        country_flag_pairs: List[Tuple[str, str]],
        output_format: OutputFormatType = "text",
        separator: str = " ",
    ) -> str:
        """
        Format the output according to the specified format.

        Args:
            country_flag_pairs: A list of (country, flag) pairs.
            output_format: The output format (text, json, csv).
            separator: The separator used between flags in text format.

        Returns:
            str: The formatted output.

        Example:
            >>> cf = CountryFlag()
            >>> flags, pairs = cf.get_flag(["United States", "Canada"])
            >>> cf.format_output(pairs, "json")
            '[{"country": "United States", "flag": "🇺🇸"}, {"country": "Canada", "flag": "🇨🇦"}]'
        """
        if output_format == "json":
            result = [
                {"country": country, "flag": flag}
                for country, flag in country_flag_pairs
            ]
            return json.dumps(result, ensure_ascii=False)

        elif output_format == "csv":
            output = StringIO()
            writer = csv.writer(output)
            writer.writerow(["Country", "Flag"])
            for country, flag in country_flag_pairs:
                writer.writerow([country, flag])
            return output.getvalue()

        else:  # text format
            return separator.join(flag for _, flag in country_flag_pairs)
