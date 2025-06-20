#!/usr/bin/env python3
# countryflag - Converts country names to emoji flags

"""
CountryFlag - A Python package for converting country names into emoji flags.

This module provides functionality to convert country names to emoji flags
and vice versa, with support for various formats, fuzzy matching, and
region/continent grouping.

For more information, see the documentation at:
https://github.com/Lendersmark/countryflag

.. include:: ../README.md
"""

import sys
import json
import csv
import logging
import os
import re
import functools
import unicodedata
import asyncio
import concurrent.futures
from pathlib import Path
from typing import (
    List, Dict, Union, Optional, Any, Tuple, Set, Callable, TypeVar, 
    Generator, Iterable, cast, Protocol, runtime_checkable, 
    NamedTuple, TypedDict, Literal, ClassVar, Final, Generic, overload
)
from io import StringIO
from dataclasses import dataclass, field
import flag
import argparse
import country_converter as coco
from functools import lru_cache, wraps
from difflib import get_close_matches
import readline
import prompt_toolkit
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.shortcuts import prompt
import aioconsole
import typeguard


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("countryflag")


# Type variable for generic functions
T = TypeVar('T')


# Type definitions
RegionType = Literal["Africa", "Americas", "Asia", "Europe", "Oceania"]
OutputFormatType = Literal["text", "json", "csv"]
T = TypeVar('T')
U = TypeVar('U')


# Design by contract decorators
def require(predicate: Callable[..., bool], message: str = "Precondition failed"):
    """
    Decorator to enforce preconditions using design by contract.
    
    Args:
        predicate: A function that takes the same arguments as the decorated function
                  and returns True if the precondition is satisfied.
        message: The error message to raise if the precondition fails.
    
    Returns:
        The decorated function.
    
    Raises:
        ValueError: If the precondition is not satisfied.
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            if not predicate(*args, **kwargs):
                raise ValueError(f"{message} in {func.__name__}")
            return func(*args, **kwargs)
        return wrapper
    return decorator


def ensure(predicate: Callable[[T], bool], message: str = "Postcondition failed"):
    """
    Decorator to enforce postconditions using design by contract.
    
    Args:
        predicate: A function that takes the return value of the decorated function
                  and returns True if the postcondition is satisfied.
        message: The error message to raise if the postcondition fails.
    
    Returns:
        The decorated function with postcondition checking.
    
    Raises:
        ValueError: If the postcondition is not satisfied.
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            result = func(*args, **kwargs)
            if not predicate(result):
                raise ValueError(f"{message} in {func.__name__}")
            return result
        return wrapper
    return decorator


def runtime_typechecked(func: Callable[..., T]) -> Callable[..., T]:
    """
    Decorator to add runtime type checking to a function.
    
    Args:
        func: The function to decorate.
    
    Returns:
        The decorated function with runtime type checking.
    
    Raises:
        TypeError: If the arguments or return value do not match the type annotations.
    """
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        return typeguard.typechecked(func)(*args, **kwargs)
    return wrapper


# Exception classes
class CountryFlagError(Exception):
    """Custom exception for countryflag errors."""
    __slots__ = ('message',)
    
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class InvalidCountryError(CountryFlagError):
    """Exception raised when an invalid country name is provided."""
    __slots__ = ('country',)
    
    def __init__(self, message: str, country: str) -> None:
        self.country = country
        super().__init__(message)


class ReverseConversionError(CountryFlagError):
    """Exception raised when a flag emoji cannot be converted to a country name."""
    __slots__ = ('flag',)
    
    def __init__(self, message: str, flag: str) -> None:
        self.flag = flag
        super().__init__(message)


class RegionError(CountryFlagError):
    """Exception raised when an invalid region is provided."""
    __slots__ = ('region',)
    
    def __init__(self, message: str, region: str) -> None:
        self.region = region
        super().__init__(message)


# Data classes
@dataclass(frozen=True)
class CountryInfo:
    """
    Data class representing country information.
    
    Attributes:
        name: The short name of the country.
        iso2: The ISO 3166-1 alpha-2 code for the country.
        iso3: The ISO 3166-1 alpha-3 code for the country.
        official_name: The official name of the country.
        region: The region/continent the country belongs to.
        subregion: The subregion within the continent.
        flag: The emoji flag for the country.
    """
    name: str
    iso2: str
    iso3: str
    official_name: str
    region: str = ""
    subregion: str = ""
    flag: str = ""
    
    def __post_init__(self) -> None:
        """Generate the flag emoji if not provided."""
        object.__setattr__(self, "flag", flag.flag(self.iso2) if not self.flag else self.flag)


@runtime_checkable
class CountryLookup(Protocol):
    """Protocol defining the interface for country lookup operations."""
    
    def convert(self, name: str, to: str = "ISO2") -> str:
        """Convert a country name to the specified format."""
        ...
    
    def get_countries_by_region(self, region: str) -> List[CountryInfo]:
        """Get countries in a specific region/continent."""
        ...
    
    def get_supported_regions(self) -> List[str]:
        """Get a list of supported regions/continents."""
        ...


class CountryConverterSingleton:
    """
    Singleton class for caching country converter operations.
    
    This class implements the CountryLookup protocol and provides
    caching for country converter operations.
    """
    __instance: Optional['CountryConverterSingleton'] = None
    
    # Define the supported regions
    REGIONS: ClassVar[List[str]] = [
        "Africa", "Americas", "Asia", "Europe", "Oceania"
    ]
    
    def __new__(cls) -> 'CountryConverterSingleton':
        if cls.__instance is None:
            cls.__instance = super(CountryConverterSingleton, cls).__new__(cls)
            cls.__instance._converter = coco.CountryConverter()
            cls.__instance._cache: Dict[str, Any] = {}
            cls.__instance._fuzzy_cache: Dict[str, List[Tuple[str, str]]] = {}
            cls.__instance._reverse_cache: Dict[str, str] = {}
            cls.__instance._region_cache: Dict[str, List[CountryInfo]] = {}
            
            # Add UN region data if available
            try:
                cls.__instance._region_data = cls.__instance._converter.data[['ISO2', 'ISO3', 'name_short', 'name_official', 'region', 'sub_region']]
            except KeyError:
                # If region data is not available, create empty columns
                cls.__instance._region_data = cls.__instance._converter.data[['ISO2', 'ISO3', 'name_short', 'name_official']].copy()
                cls.__instance._region_data['region'] = ""
                cls.__instance._region_data['sub_region'] = ""
        
        return cls.__instance
    
    @property
    def data(self) -> Any:
        """
        Return the data frame from the converter.
        
        Returns:
            pandas.DataFrame: The data frame containing country information.
        """
        return self._converter.data
    
    @property
    def region_data(self) -> Any:
        """
        Return the region data frame.
        
        Returns:
            pandas.DataFrame: The data frame containing country region information.
        """
        return self._region_data
    
    @runtime_typechecked
    @lru_cache(maxsize=1024)
    def convert(self, name: str, to: str = "ISO2") -> str:
        """
        Convert a country name to the specified format with caching.
        
        Args:
            name: The country name to convert.
            to: The format to convert to (default: ISO2).
            
        Returns:
            str: The converted country code.
            
        Example:
            >>> converter = CountryConverterSingleton()
            >>> converter.convert("United States", "ISO2")
            'US'
            >>> converter.convert("United States", "ISO3")
            'USA'
        """
        try:
            result = coco.convert(names=name, to=to)
            return result
        except Exception as e:
            logger.debug(f"Error converting {name} to {to}: {e}")
            return "not found"
    
    @runtime_typechecked
    def get_iso2_to_country_mapping(self) -> Dict[str, str]:
        """
        Get a mapping of ISO2 codes to country names.
        
        Returns:
            Dict[str, str]: A dictionary mapping ISO2 codes to country names.
            
        Example:
            >>> converter = CountryConverterSingleton()
            >>> mapping = converter.get_iso2_to_country_mapping()
            >>> mapping['US']
            'United States'
        """
        if 'iso2_mapping' not in self._cache:
            result = {}
            for _, row in self.data.iterrows():
                if row['ISO2'] != "not found":
                    result[row['ISO2']] = row['name_short']
            self._cache['iso2_mapping'] = result
            
        return self._cache['iso2_mapping']
        
    @runtime_typechecked
    def get_supported_regions(self) -> List[str]:
        """
        Get a list of supported regions/continents.
        
        Returns:
            List[str]: A list of supported regions/continents.
            
        Example:
            >>> converter = CountryConverterSingleton()
            >>> converter.get_supported_regions()
            ['Africa', 'Americas', 'Asia', 'Europe', 'Oceania']
        """
        return self.REGIONS
        
    @runtime_typechecked
    def get_countries_by_region(self, region: str) -> List[CountryInfo]:
        """
        Get countries in a specific region/continent.
        
        Args:
            region: The region/continent name (e.g., "Europe", "Asia").
            
        Returns:
            List[CountryInfo]: A list of countries in the specified region.
            
        Raises:
            RegionError: If the region is not supported.
            
        Example:
            >>> converter = CountryConverterSingleton()
            >>> countries = converter.get_countries_by_region("Europe")
            >>> len(countries) > 0
            True
        """
        if region not in self.REGIONS:
            raise RegionError(f"Unsupported region: {region}", region)
            
        if region not in self._region_cache:
            countries = []
            
            # Filter countries by region
            for _, row in self.region_data.iterrows():
                if (row['ISO2'] != "not found" and 
                    isinstance(row['region'], str) and 
                    row['region'].lower() == region.lower()):
                    
                    country_info = CountryInfo(
                        name=row['name_short'],
                        iso2=row['ISO2'],
                        iso3=row['ISO3'],
                        official_name=row['name_official'],
                        region=row['region'],
                        subregion=row['sub_region'] if 'sub_region' in row else "",
                        flag=flag.flag(row['ISO2'])
                    )
                    countries.append(country_info)
                    
            self._region_cache[region] = countries
            
        return self._region_cache[region]
    
    def get_flag_to_country_mapping(self) -> Dict[str, str]:
        """
        Get a mapping of flag emojis to country names.
        
        Returns:
            Dict[str, str]: A dictionary mapping flag emojis to country names.
        """
        if not self._reverse_cache:
            iso2_mapping = self.get_iso2_to_country_mapping()
            for iso2, country in iso2_mapping.items():
                emoji_flag = flag.flag(iso2)
                self._reverse_cache[emoji_flag] = country
        return self._reverse_cache
    
    def find_close_matches(self, name: str, cutoff: float = 0.6) -> List[Tuple[str, str]]:
        """
        Find country names that closely match the given input.
        
        Args:
            name: The country name to find matches for.
            cutoff: The similarity threshold (0-1).
            
        Returns:
            List[Tuple[str, str]]: A list of tuples containing (country_name, iso2_code).
        """
        cache_key = f"{name}_{cutoff}"
        if cache_key in self._fuzzy_cache:
            return self._fuzzy_cache[cache_key]
            
        # Get all country names
        country_names = []
        for _, row in self.data.iterrows():
            if row['ISO2'] != "not found":
                country_names.append((row['name_short'], row['ISO2']))
                
        # Get all country names as a list
        names_only = [n[0] for n in country_names]
        
        # Find close matches
        matches = get_close_matches(name, names_only, n=5, cutoff=cutoff)
        
        # Create result list with (name, iso2) tuples
        result = [(match, next(code for n, code in country_names if n == match)) for match in matches]
        
        # Cache the result
        self._fuzzy_cache[cache_key] = result
        
        return result


class CountryFlag:
    """
    Class to handle country flag operations.
    
    This class provides methods for converting country names to emoji flags,
    reverse lookup (flag to country name), and region-based operations.
    
    Attributes:
        _converter: The CountryConverterSingleton instance.
        _language: The language code for output.
        
    Example:
        >>> cf = CountryFlag()
        >>> flags, _ = cf.get_flag(["United States", "Canada", "Mexico"])
        >>> flags
        '🇺🇸 🇨🇦 🇲🇽'
    """
    __slots__ = ('_converter', '_language')
    
    def __init__(self, language: str = 'en') -> None:
        """
        Initialize the CountryFlag class.
        
        Args:
            language: The language code for output (default: 'en').
        """
        self._converter = CountryConverterSingleton()
        self._language = language
    
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
        """
        if not country_name or not isinstance(country_name, str):
            return False
            
        try:
            code = self._converter.convert(country_name)
            return code != "not found"
        except Exception:
            return False
    
    def get_supported_countries(self) -> List[Dict[str, str]]:
        """
        Get a list of supported country names and their ISO2 codes.
        
        Returns:
            List[Dict[str, str]]: A list of dictionaries containing country information.
        """
        # Create a list of dictionaries with country information
        countries = []
        for _, row in self._converter.data.iterrows():
            if row['ISO2'] != "not found":
                countries.append({
                    'name': row['name_short'],
                    'iso2': row['ISO2'],
                    'iso3': row['ISO3'],
                    'official_name': row['name_official']
                })
        
        return countries
    
    @runtime_typechecked
    def get_flags_by_region(
        self, 
        region: RegionType,
        separator: str = " "
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
        try:
            countries = self._converter.get_countries_by_region(region)
            country_names = [country.name for country in countries]
            return self.get_flag(country_names, separator)
        except RegionError as re:
            logger.error(f"Error getting flags for region '{region}': {re}")
            raise
    
    @runtime_typechecked
    @require(lambda country_names, *args, **kwargs: isinstance(country_names, list), 
             "country_names must be a list")
    @ensure(lambda result: isinstance(result, tuple) and len(result) == 2, 
            "Result must be a tuple of (str, list)")
    def get_flag(
        self, 
        country_names: List[str], 
        separator: str = " ",
        fuzzy_matching: bool = False,
        fuzzy_threshold: float = 0.6
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
                    matches = self._converter.find_close_matches(country_name, fuzzy_threshold)
                    if matches:
                        # Use the best match
                        best_match, country_code = matches[0]
                        logger.info(f"Using fuzzy match '{best_match}' for '{country_name}'")
                        country_name = best_match
                
                if country_code == "not found":
                    raise InvalidCountryError(f"Country not found: {country_name}", country_name)
                    
                # Convert ISO2 code into flag
                emoji_flag = flag.flag(country_code)
                flags_list.append(emoji_flag)
                country_flag_pairs.append((country_name, emoji_flag))
                
            except ValueError as ve:
                logger.error(f"Error converting country '{country_name}': {ve}")
                raise InvalidCountryError(f"Invalid country name: {country_name}", country_name) from ve
                
        # Join the flags with the specified separator
        return separator.join(flags_list), country_flag_pairs
    
    def reverse_lookup(self, emoji_flags: List[str]) -> List[Tuple[str, str]]:
        """
        Convert emoji flags to country names.
        
        Args:
            emoji_flags: A list of emoji flags to convert to country names.
            
        Returns:
            List[Tuple[str, str]]: A list of tuples containing (flag, country_name).
            
        Raises:
            ReverseConversionError: If a flag emoji cannot be converted to a country name.
        """
        if not emoji_flags:
            logger.warning("Empty list of emoji flags provided")
            return []
            
        flag_to_country = self._converter.get_flag_to_country_mapping()
        result = []
        
        for i, emoji_flag in enumerate(emoji_flags):
            logger.debug(f"Processing flag: {emoji_flag}")
            
            if not emoji_flag or not isinstance(emoji_flag, str):
                logger.warning(f"Invalid input at position {i}: {emoji_flag}")
                continue
                
            # Clean the input flag
            clean_flag = emoji_flag.strip()
            
            if clean_flag in flag_to_country:
                country_name = flag_to_country[clean_flag]
                result.append((clean_flag, country_name))
            else:
                error_msg = f"Cannot convert flag emoji to country name: {clean_flag}"
                logger.error(error_msg)
                raise ReverseConversionError(error_msg, clean_flag)
                
        return result
    
    def format_output(
        self,
        country_flag_pairs: List[Tuple[str, str]],
        output_format: str = "text",
        separator: str = " "
    ) -> str:
        """
        Format the output according to the specified format.
        
        Args:
            country_flag_pairs: A list of (country, flag) pairs.
            output_format: The output format (text, json, csv).
            separator: The separator used between flags in text format.
            
        Returns:
            str: The formatted output.
        """
        if output_format == "json":
            result = [{"country": country, "flag": flag} for country, flag in country_flag_pairs]
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


@runtime_typechecked
def process_file_input(file_path: str) -> List[str]:
    """
    Process a file containing country names, one per line.
    
    Args:
        file_path: The path to the file.
        
    Returns:
        List[str]: A list of country names.
        
    Raises:
        IOError: If the file cannot be read.
        
    Example:
        >>> process_file_input("countries.txt")  # File contains "USA\\nCanada"
        ['USA', 'Canada']
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            # Read lines and strip whitespace
            return [line.strip() for line in f if line.strip()]
    except IOError as e:
        logger.error(f"Error reading file {file_path}: {e}")
        raise


@runtime_typechecked
async def process_file_input_async(file_path: str) -> List[str]:
    """
    Process a file containing country names asynchronously.
    
    Args:
        file_path: The path to the file.
        
    Returns:
        List[str]: A list of country names.
        
    Raises:
        IOError: If the file cannot be read.
    """
    try:
        # For very large files, this will be more efficient
        loop = asyncio.get_event_loop()
        
        # Use ThreadPoolExecutor for file I/O operations
        with concurrent.futures.ThreadPoolExecutor() as pool:
            contents = await loop.run_in_executor(
                pool, lambda: Path(file_path).read_text(encoding='utf-8')
            )
            
            # Process the file contents
            return [line.strip() for line in contents.splitlines() if line.strip()]
    except IOError as e:
        logger.error(f"Error reading file {file_path}: {e}")
        raise


@runtime_typechecked
def process_multiple_files(file_paths: List[str], max_workers: int = 4) -> List[str]:
    """
    Process multiple files containing country names in parallel.
    
    Args:
        file_paths: A list of paths to files.
        max_workers: The maximum number of worker threads.
        
    Returns:
        List[str]: A combined list of country names from all files.
        
    Raises:
        IOError: If any file cannot be read.
    """
    results: List[str] = []
    
    # Use ThreadPoolExecutor for parallel file processing
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_file = {
            executor.submit(process_file_input, file_path): file_path
            for file_path in file_paths
        }
        
        for future in concurrent.futures.as_completed(future_to_file):
            file_path = future_to_file[future]
            try:
                # Add the results from this file to our combined results
                results.extend(future.result())
            except Exception as e:
                logger.error(f"Error processing file {file_path}: {e}")
                # Re-raise the exception
                raise
                
    return results


def run_interactive_mode(country_flag: CountryFlag) -> None:
    """
    Run the interactive CLI mode with autocomplete.
    
    Args:
        country_flag: The CountryFlag instance to use.
    """
    # Get all country names for autocompletion
    countries = country_flag.get_supported_countries()
    country_names = [country['name'] for country in countries]
    
    print("CountryFlag Interactive Mode")
    print("Type country names to get their flags. Type 'exit' or 'quit' to exit.")
    print("Press Tab for autocompletion.")
    
    # Create a completer with country names
    country_completer = WordCompleter(country_names, ignore_case=True)
    
    while True:
        try:
            # Get input with autocompletion
            user_input = prompt('> ', completer=country_completer)
            
            if user_input.lower() in ('exit', 'quit'):
                break
                
            # Split input by commas or spaces
            country_list = [c.strip() for c in re.split(r'[,\s]+', user_input) if c.strip()]
            
            if country_list:
                flags, pairs = country_flag.get_flag(country_list, fuzzy_matching=True)
                
                # Display results
                for name, emoji in pairs:
                    print(f"{name}: {emoji}")
                    
                print("\nCombined: " + flags)
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {str(e)}")
    
    print("Exiting interactive mode.")


async def run_async_main(args: argparse.Namespace) -> None:
    """
    Asynchronous version of the main function.
    
    Args:
        args: The parsed command-line arguments.
    """
    # Set logging level based on verbose flag
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # Initialize the CountryFlag class
    country_flag = CountryFlag(language=args.language)
    
    try:
        # Process input
        country_names = []
        if args.file:
            # Use async file processing for larger files
            country_names = await process_file_input_async(args.file)
        elif args.files:
            # Use parallel processing for multiple files
            country_names = process_multiple_files(args.files, max_workers=args.workers)
        elif args.countries:
            country_names = args.countries
            
        # Handle region-based lookup
        if args.region:
            flags, country_flag_pairs = country_flag.get_flags_by_region(args.region, args.separator)
            output = country_flag.format_output(country_flag_pairs, args.format, args.separator)
            print(output)
            return
            
        # Handle flag to country conversion (reverse lookup)
        if args.reverse:
            flag_country_pairs = country_flag.reverse_lookup(args.reverse)
            
            if args.format == "json":
                result = [{"flag": flag, "country": country} for flag, country in flag_country_pairs]
                print(json.dumps(result, ensure_ascii=False))
            elif args.format == "csv":
                output = StringIO()
                writer = csv.writer(output)
                writer.writerow(["Flag", "Country"])
                for flag, country in flag_country_pairs:
                    writer.writerow([flag, country])
                print(output.getvalue())
            else:
                for flag, country in flag_country_pairs:
                    print(f"{flag} -> {country}")
                    
        # Handle country to flag conversion
        elif country_names:
            flags, country_flag_pairs = country_flag.get_flag(
                country_names, 
                args.separator, 
                args.fuzzy, 
                args.threshold
            )
            output = country_flag.format_output(country_flag_pairs, args.format, args.separator)
            print(output)
            
    except InvalidCountryError as ice:
        logger.error(str(ice))
        print(f"Error: {str(ice)}")
        
        # If fuzzy matching is enabled, suggest alternatives
        if args.fuzzy:
            converter = CountryConverterSingleton()
            matches = converter.find_close_matches(ice.country, args.threshold)
            if matches:
                print("\nDid you mean one of these?")
                for name, code in matches:
                    print(f"  - {name} ({code})")
                    
        print("\nUse --list-countries to see all supported country names")
        sys.exit(1)
        
    except RegionError as re:
        logger.error(str(re))
        print(f"Error: {str(re)}")
        print(f"\nSupported regions: {', '.join(CountryConverterSingleton.REGIONS)}")
        sys.exit(1)
        
    except ReverseConversionError as rce:
        logger.error(str(rce))
        print(f"Error: {str(rce)}")
        sys.exit(1)
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        print(f"Error: {str(e)}")
        sys.exit(1)


def main() -> None:
    """
    Entry point to the script.
    
    Parses command line arguments and executes the main functionality.
    """
    # Parse arguments
    parser = argparse.ArgumentParser(
        description="Countryflag: a Python package for converting country names into emoji flags."
    )
    
    # Input group
    input_group = parser.add_mutually_exclusive_group(required=False)
    input_group.add_argument(
        "countries",
        metavar="COUNTRY",
        nargs="*",
        help="Country names to be converted into emojis, separated by spaces",
    )
    input_group.add_argument(
        "--file", "-i",
        metavar="FILE",
        help="File containing country names, one per line",
    )
    input_group.add_argument(
        "--files", 
        nargs="+",
        metavar="FILES",
        help="Multiple files containing country names, processed in parallel",
    )
    input_group.add_argument(
        "--reverse", "-r",
        nargs="+",
        metavar="FLAG",
        help="Convert flag emojis to country names",
    )
    input_group.add_argument(
        "--region",
        choices=CountryConverterSingleton.REGIONS,
        help="Get flags for all countries in a specific region/continent",
    )
    input_group.add_argument(
        "--interactive", "-I",
        action="store_true",
        help="Run in interactive mode with autocompletion",
    )
    
    # Output options
    parser.add_argument(
        "--format", "-f",
        choices=["text", "json", "csv"],
        default="text",
        help="Output format (text, json, or csv)"
    )
    parser.add_argument(
        "--separator", "-s",
        default=" ",
        help="Separator character between flags (default: space)"
    )
    
    # Utility options
    parser.add_argument(
        "--fuzzy", "-z",
        action="store_true",
        help="Enable fuzzy matching for country names"
    )
    parser.add_argument(
        "--threshold", "-t",
        type=float,
        default=0.6,
        help="Similarity threshold for fuzzy matching (0-1, default: 0.6)"
    )
    parser.add_argument(
        "--language", "-l",
        default="en",
        help="Language for country names (ISO 639-1 code, default: en)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    parser.add_argument(
        "--list-countries",
        action="store_true",
        help="List all supported countries and exit"
    )
    parser.add_argument(
        "--list-regions",
        action="store_true",
        help="List all supported regions/continents and exit"
    )
    parser.add_argument(
        "--validate",
        metavar="COUNTRY",
        help="Validate a country name and exit"
    )
    parser.add_argument(
        "--workers", "-w",
        type=int,
        default=4,
        help="Number of worker threads for parallel processing (default: 4)"
    )
    parser.add_argument(
        "--async", "-a",
        action="store_true",
        dest="use_async",
        help="Use asynchronous file processing (faster for large files)"
    )
    
    args = parser.parse_args()
    
    # Set logging level based on verbose flag
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # Initialize the CountryFlag class
    country_flag = CountryFlag(language=args.language)
    
    # Handle special commands
    if args.list_countries:
        countries = country_flag.get_supported_countries()
        if args.format == "json":
            print(json.dumps(countries, ensure_ascii=False))
        elif args.format == "csv":
            output = StringIO()
            writer = csv.writer(output)
            writer.writerow(["Name", "ISO2", "ISO3", "Official Name", "Region"])
            for country in countries:
                writer.writerow([
                    country["name"],
                    country["iso2"],
                    country["iso3"],
                    country["official_name"],
                    country.get("region", "")
                ])
            print(output.getvalue())
        else:
            for country in countries:
                region = f" ({country.get('region', '')})" if country.get('region') else ""
                print(f"{country['name']} ({country['iso2']}){region}")
        sys.exit(0)
        
    if args.list_regions:
        regions = CountryConverterSingleton().get_supported_regions()
        if args.format == "json":
            print(json.dumps(regions, ensure_ascii=False))
        elif args.format == "csv":
            output = StringIO()
            writer = csv.writer(output)
            writer.writerow(["Region"])
            for region in regions:
                writer.writerow([region])
            print(output.getvalue())
        else:
            print("Supported regions/continents:")
            for region in regions:
                print(f"  - {region}")
        sys.exit(0)
        
    if args.validate:
        is_valid = country_flag.validate_country_name(args.validate)
        if is_valid:
            print(f"'{args.validate}' is a valid country name")
        else:
            print(f"'{args.validate}' is NOT a valid country name")
            
            # If fuzzy matching is enabled, suggest alternatives
            if args.fuzzy:
                converter = CountryConverterSingleton()
                matches = converter.find_close_matches(args.validate, args.threshold)
                if matches:
                    print("\nDid you mean one of these?")
                    for name, code in matches:
                        print(f"  - {name} ({code})")
                
        sys.exit(0 if is_valid else 1)
        
    # Run interactive mode
    if args.interactive:
        run_interactive_mode(country_flag)
        sys.exit(0)
    
    # Use async main if requested
    if args.use_async or args.file or args.files:
        try:
            # Run the async version
            asyncio.run(run_async_main(args))
        except KeyboardInterrupt:
            print("\nOperation cancelled by user.")
            sys.exit(1)
        return
    
    # Regular synchronous execution
    try:
        # Process input
        country_names = []
        if args.file:
            country_names = process_file_input(args.file)
        elif args.files:
            country_names = process_multiple_files(args.files, max_workers=args.workers)
        elif args.countries:
            country_names = args.countries
            
        # Handle region-based lookup
        if args.region:
            flags, country_flag_pairs = country_flag.get_flags_by_region(args.region, args.separator)
            output = country_flag.format_output(country_flag_pairs, args.format, args.separator)
            print(output)
            return
            
        # Handle flag to country conversion (reverse lookup)
        if args.reverse:
            flag_country_pairs = country_flag.reverse_lookup(args.reverse)
            
            if args.format == "json":
                result = [{"flag": flag, "country": country} for flag, country in flag_country_pairs]
                print(json.dumps(result, ensure_ascii=False))
            elif args.format == "csv":
                output = StringIO()
                writer = csv.writer(output)
                writer.writerow(["Flag", "Country"])
                for flag, country in flag_country_pairs:
                    writer.writerow([flag, country])
                print(output.getvalue())
            else:
                for flag, country in flag_country_pairs:
                    print(f"{flag} -> {country}")
                    
        # Handle country to flag conversion
        elif country_names:
            flags, country_flag_pairs = country_flag.get_flag(
                country_names, 
                args.separator, 
                args.fuzzy, 
                args.threshold
            )
            output = country_flag.format_output(country_flag_pairs, args.format, args.separator)
            print(output)
            
    except InvalidCountryError as ice:
        logger.error(str(ice))
        print(f"Error: {str(ice)}")
        
        # If fuzzy matching is enabled, suggest alternatives
        if args.fuzzy:
            converter = CountryConverterSingleton()
            matches = converter.find_close_matches(ice.country, args.threshold)
            if matches:
                print("\nDid you mean one of these?")
                for name, code in matches:
                    print(f"  - {name} ({code})")
                    
        print("\nUse --list-countries to see all supported country names")
        sys.exit(1)
        
    except RegionError as re:
        logger.error(str(re))
        print(f"Error: {str(re)}")
        print(f"\nSupported regions: {', '.join(CountryConverterSingleton.REGIONS)}")
        sys.exit(1)
        
    except ReverseConversionError as rce:
        logger.error(str(rce))
        print(f"Error: {str(rce)}")
        sys.exit(1)
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        print(f"Error: {str(e)}")
        sys.exit(1)


# If this module is the main program, run the main function
if __name__ == "__main__":
    main()
