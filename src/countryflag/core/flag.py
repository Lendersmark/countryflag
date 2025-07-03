"""
Country flag functionality for the countryflag package.

This module contains the CountryFlag class that provides methods for converting
country names to emoji flags and vice versa.
"""

import csv
import json
import logging
from io import StringIO
from typing import Dict, List, Literal, Optional, Tuple

import flag

# Import resource loading modules
try:
    import importlib.resources as importlib_resources  # type: ignore
except ImportError:
    importlib_resources = None  # type: ignore

try:
    import pkg_resources  # type: ignore
except ImportError:
    pkg_resources = None  # type: ignore

from countryflag.cache.base import Cache
from countryflag.cache.memory import MemoryCache
from countryflag.core.converters import CountryConverterSingleton
from countryflag.core.exceptions import (
    InvalidCountryError,
    RegionError,
    ReverseConversionError,
)
from countryflag.utils.suppress import silence_coco_warnings
from countryflag.utils.text import norm_newlines

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

    # Class-level shared cache instance (lazy-initialized)
    _global_cache: Optional[MemoryCache] = None

    __slots__ = ("_converter", "_language", "_cache")

    def __init__(self, language: str = "en", cache: Optional[Cache] = None) -> None:
        """
        Initialize the CountryFlag class.

        Args:
            language: The language code for output (default: 'en').
            cache: The cache instance to use (optional).
                If None, uses the shared global cache.
        """
        self._converter = CountryConverterSingleton()
        self._language = language
        # Use the global cache if no cache is provided
        self._cache = cache if cache is not None else self._get_global_cache()

    @classmethod
    def _get_global_cache(cls) -> MemoryCache:
        """
        Get or create the global cache instance (lazy initialization).

        This method ensures thread-safe lazy initialization of the global cache
        to prevent deadlocks in multiprocessing scenarios.

        Returns:
            MemoryCache: The global cache instance.
        """
        if cls._global_cache is None:
            cls._global_cache = MemoryCache()
        return cls._global_cache

    @classmethod
    def clear_global_cache(cls) -> None:
        """
        Clear the global cache. Useful for testing or resetting cache state.

        This method clears the shared cache instance used by all CountryFlag
        instances that don't have a custom cache provided.

        Example:
            >>> CountryFlag.clear_global_cache()
        """
        if cls._global_cache is not None:
            cls._global_cache.clear()
            cls._global_cache.reset_hits()

    def set_language(self, language: str) -> None:
        """
        Set the language for country names.

        Args:
            language: The ISO 639-1 language code.
        """
        self._language = language

    def _make_key(self, country_names: List[str], separator: str) -> str:
        """
        Create a deterministic cache key by sorting country names.

        This ensures that the same logical country list in different orders
        maps to the same cache entry. Only valid string entries are used for the key.

        Args:
            country_names: List of country names.
            separator: The separator used between flags.

        Returns:
            str: A deterministic cache key.
        """
        # Filter to only valid string entries for the cache key
        valid_names = [
            name for name in country_names if isinstance(name, str) and name.strip()
        ]
        return ",".join(sorted(valid_names)) + f"_{separator}"

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

            # Convert to all possible codes and validate the length
            valid_result = False
            iso_codes = [code.strip() for code in country_name.split()]

            if len(iso_codes) > 1:  # Handle cases with multi-word countries
                with silence_coco_warnings():
                    valid_result = all(
                        self._converter.convert(name) != "not found"
                        for name in iso_codes
                    )
            else:
                # Single country validation
                with silence_coco_warnings():
                    code = self._converter.convert(country_name)
                    valid_result = (
                        isinstance(code, str) and code != "not found" and len(code) <= 3
                    )

            # Cache the result if cache is available
            if self._cache:
                self._cache.set(cache_key, valid_result)

            return valid_result
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
            cache_key = f"get_flag_{self._make_key(country_names, separator)}"
            cached_result = self._cache.get(cache_key)
            if cached_result is not None:
                # Cached result exists, but we need to reorder it to match current input order
                cached_flags, cached_pairs = cached_result
                # Create a mapping from country name to flag
                # from cached result
                country_to_flag = dict(cached_pairs)

                # Reconstruct result in current input order
                reordered_pairs = []
                reordered_flags = []
                for country_name in country_names:
                    if (
                        isinstance(country_name, str)
                        and country_name.strip()
                        and country_name in country_to_flag
                    ):
                        emoji_flag = country_to_flag[country_name]
                        reordered_pairs.append((country_name, emoji_flag))
                        reordered_flags.append(emoji_flag)

                return (separator.join(reordered_flags), reordered_pairs)

        # Use a list for better performance when concatenating strings
        flags_list = []
        country_flag_pairs = []

        for i, country_name in enumerate(country_names):
            logger.debug(f"Processing country: {country_name}")

            # Skip invalid items (non-strings, None)
            if not isinstance(country_name, str):
                logger.debug(
                    f"Skipping invalid input type at position {i}: "
                    f"expected string, got {type(country_name).__name__}"
                )
                continue

            # Skip empty strings and whitespace-only strings
            if not country_name.strip():
                logger.debug(
                    f"Empty or whitespace-only string detected at position {i}, skipping"
                )
                continue

            try:
                # Suppress noise during conversion attempts
                with silence_coco_warnings():
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
                                f"Using fuzzy match '{best_match}' for "
                                f"'{country_name}'"
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
            >>> pairs = cf.reverse_lookup(["🇺🇸", "🇬🇧", "🇺🇰"])
            >>> pairs
            [('🇺🇸', 'United States'), ('🇬🇧', 'United Kingdom')]
        """
        if not emoji_flags:
            logger.warning("Empty list of emoji flags provided")
            return []

        # Check cache first if available
        if self._cache:
            cache_key = f"reverse_lookup_{self._make_key(emoji_flags, '')}"
            cached_result = self._cache.get(cache_key)
            if cached_result is not None:
                # Cached result exists, but we need to reorder it to match current input order
                # Create a mapping from flag to country from cached result
                flag_to_country = dict(cached_result)

                # Reconstruct result in current input order
                reordered_result = []
                for emoji_flag in emoji_flags:
                    if isinstance(emoji_flag, str) and emoji_flag in flag_to_country:
                        country_name = flag_to_country[emoji_flag]
                        reordered_result.append((emoji_flag, country_name))

                return reordered_result

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
            '[{"country": "US", "flag": "🇺🇸"}]'
        """
        if output_format == "json":
            result = [
                {"country": country, "flag": flag}
                for country, flag in country_flag_pairs
            ]
            return norm_newlines(json.dumps(result, ensure_ascii=False))

        elif output_format == "csv":
            output = StringIO()
            writer = csv.writer(output)
            writer.writerow(["Country", "Flag"])
            for country, emoji_flag in country_flag_pairs:
                writer.writerow([country, emoji_flag])
            return norm_newlines(output.getvalue())

        else:  # text format
            return norm_newlines(separator.join(flag for _, flag in country_flag_pairs))

    def get_ascii_flag(self, country_name: str) -> str:
        """
        Get ASCII art flag for a country, with fallback to Unicode emoji.

        This method attempts to load ASCII art from embedded resources.
        If the resource is missing or cannot be loaded, it falls back to
        returning the Unicode emoji flag instead of raising an error.

        Args:
            country_name: The country name or ISO code.

        Returns:
            str: ASCII art flag if available, otherwise Unicode emoji flag.

        Example:
            >>> cf = CountryFlag()
            >>> result = cf.get_ascii_flag("DE")
            >>> isinstance(result, str)
            True
        """
        # First convert country name to ISO code
        try:
            with silence_coco_warnings():
                iso_code = self._converter.convert(country_name)

            if iso_code == "not found":
                raise InvalidCountryError(
                    f"Country not found: {country_name}", country_name
                )

        except Exception:
            raise InvalidCountryError(
                f"Invalid country name: {country_name}", country_name
            )

        # Try to load ASCII art from embedded resources
        try:
            # Try different resource loading approaches
            ascii_art = None

            # Method 1: importlib.resources (Python 3.9+)
            if importlib_resources and hasattr(importlib_resources, "open_binary"):
                try:
                    # This will raise FileNotFoundError if resource is missing
                    with importlib_resources.open_binary(
                        "countryflag.assets", f"{iso_code.lower()}.txt"
                    ) as f:
                        ascii_art = f.read().decode("utf-8")
                except FileNotFoundError:
                    logger.debug(
                        f"ASCII art resource not found for {iso_code} (importlib.resources)"
                    )
                    ascii_art = None

            # Method 2: pkg_resources (legacy)
            elif pkg_resources and hasattr(pkg_resources, "resource_stream"):
                try:
                    # This will raise FileNotFoundError if resource is missing
                    with pkg_resources.resource_stream(
                        "countryflag.assets", f"{iso_code.lower()}.txt"
                    ) as f:
                        ascii_art = f.read().decode("utf-8")
                except FileNotFoundError:
                    logger.debug(
                        f"ASCII art resource not found for {iso_code} (pkg_resources)"
                    )
                    ascii_art = None

            # If ASCII art was successfully loaded, return it
            if ascii_art:
                logger.debug(f"Loaded ASCII art for {iso_code}")
                return ascii_art

        except Exception as e:
            # Log the error but don't crash
            logger.debug(f"Error loading ASCII art for {iso_code}: {e}")

        # Fallback: return Unicode emoji flag
        logger.debug(f"Falling back to Unicode emoji for {iso_code}")
        try:
            emoji_flag = flag.flag(iso_code)
            return emoji_flag
        except Exception as e:
            logger.error(f"Error generating emoji flag for {iso_code}: {e}")
            raise InvalidCountryError(
                f"Could not generate flag for country: {country_name}", country_name
            ) from e
