"""
Country converter functionality for the countryflag package.

This module contains the CountryConverterSingleton class that provides
caching and conversion of country names to various formats.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple, cast

import flag
import country_converter as coco
import pandas as pd
from difflib import get_close_matches
from functools import lru_cache

from countryflag.core.models import CountryInfo, RegionDefinitions
from countryflag.core.exceptions import RegionError

# Configure logging
logger = logging.getLogger("countryflag.converters")


class CountryConverterSingleton:
    """
    Singleton class for caching country converter operations.
    
    This class implements caching for country converter operations and provides
    methods for converting country names to various formats.
    
    Attributes:
        _converter: The country_converter.CountryConverter instance.
        _cache: Dictionary for caching conversion results.
        _fuzzy_cache: Dictionary for caching fuzzy matching results.
        _reverse_cache: Dictionary for caching reverse lookup results.
        _region_cache: Dictionary for caching region-based lookup results.
    """
    __instance: Optional['CountryConverterSingleton'] = None
    
    def __new__(cls) -> 'CountryConverterSingleton':
        """
        Create a new instance of the class if one doesn't exist.
        
        Returns:
            CountryConverterSingleton: The singleton instance.
        """
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
    def data(self) -> pd.DataFrame:
        """
        Return the data frame from the converter.
        
        Returns:
            pandas.DataFrame: The data frame containing country information.
        """
        return self._converter.data
    
    @property
    def region_data(self) -> pd.DataFrame:
        """
        Return the region data frame.
        
        Returns:
            pandas.DataFrame: The data frame containing country region information.
        """
        return self._region_data
    
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
        return RegionDefinitions.REGIONS
        
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
        if region not in RegionDefinitions.REGIONS:
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
            
        Example:
            >>> converter = CountryConverterSingleton()
            >>> mapping = converter.get_flag_to_country_mapping()
            >>> mapping['🇺🇸']
            'United States'
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
            
        Example:
            >>> converter = CountryConverterSingleton()
            >>> matches = converter.find_close_matches("Germny")
            >>> matches[0][0]
            'Germany'
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
