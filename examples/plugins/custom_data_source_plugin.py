#!/usr/bin/env python3
"""
Example of a custom data source plugin for countryflag.

This plugin uses a custom data source (a JSON file) for country information
instead of the default country_converter library.
"""

import json
import os
from typing import List, Dict, Optional, Any

from countryflag.core.models import CountryInfo
from countryflag.plugins.base import BasePlugin


class CustomDataSourcePlugin(BasePlugin):
    """
    Custom data source plugin for countryflag.
    
    This plugin uses a JSON file as the data source for country information.
    
    Attributes:
        data_file: Path to the JSON file containing country data.
        _countries: Dictionary mapping country names to country information.
        _iso2_map: Dictionary mapping ISO2 codes to country information.
        _flag_map: Dictionary mapping flag emojis to country information.
    """
    
    def __init__(self, data_file: str):
        """
        Initialize the plugin with a custom data file.
        
        Args:
            data_file: Path to the JSON file containing country data.
        """
        self.data_file = data_file
        self._countries = {}
        self._iso2_map = {}
        self._flag_map = {}
        self._regions = {}
        
        # Load data from the file
        self._load_data()
    
    def _load_data(self) -> None:
        """Load country data from the JSON file."""
        if not os.path.exists(self.data_file):
            raise FileNotFoundError(f"Data file not found: {self.data_file}")
        
        with open(self.data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Process the data
        for item in data:
            country_info = CountryInfo(
                name=item['name'],
                iso2=item['iso2'],
                iso3=item.get('iso3', ''),
                official_name=item.get('official_name', item['name']),
                region=item.get('region', ''),
                subregion=item.get('subregion', ''),
            )
            
            # Add to the dictionaries
            self._countries[country_info.name.lower()] = country_info
            self._iso2_map[country_info.iso2.lower()] = country_info
            self._flag_map[country_info.flag] = country_info
            
            # Add to regions
            if country_info.region:
                if country_info.region not in self._regions:
                    self._regions[country_info.region] = []
                self._regions[country_info.region].append(country_info)
    
    def get_country_info(self, name: str) -> Optional[CountryInfo]:
        """
        Get country information for a given country name.
        
        Args:
            name: The country name to look up.
            
        Returns:
            CountryInfo: The country information, or None if the country is not found.
        """
        # Try direct lookup
        if name.lower() in self._countries:
            return self._countries[name.lower()]
        
        # Try ISO2 lookup
        if len(name) == 2 and name.lower() in self._iso2_map:
            return self._iso2_map[name.lower()]
        
        # Not found
        return None
    
    def get_supported_countries(self) -> List[CountryInfo]:
        """
        Get a list of supported countries.
        
        Returns:
            List[CountryInfo]: A list of country information objects.
        """
        return list(self._countries.values())
    
    def get_supported_regions(self) -> List[str]:
        """
        Get a list of supported regions/continents.
        
        Returns:
            List[str]: A list of supported regions/continents.
        """
        return list(self._regions.keys())
    
    def get_countries_by_region(self, region: str) -> List[CountryInfo]:
        """
        Get countries in a specific region/continent.
        
        Args:
            region: The region/continent name.
            
        Returns:
            List[CountryInfo]: A list of countries in the specified region.
        """
        return self._regions.get(region, [])
    
    def convert_country_name(self, name: str, to_format: str) -> str:
        """
        Convert a country name to the specified format.
        
        Args:
            name: The country name to convert.
            to_format: The format to convert to (e.g., "ISO2", "ISO3").
            
        Returns:
            str: The converted country code, or "not found" if the country is not found.
        """
        country_info = self.get_country_info(name)
        if not country_info:
            return "not found"
        
        if to_format == "ISO2":
            return country_info.iso2
        elif to_format == "ISO3":
            return country_info.iso3
        else:
            return "not found"
    
    def get_flag(self, country_name: str) -> Optional[str]:
        """
        Get the flag emoji for a country name.
        
        Args:
            country_name: The country name to get the flag for.
            
        Returns:
            str: The flag emoji, or None if the country is not found.
        """
        country_info = self.get_country_info(country_name)
        return country_info.flag if country_info else None
    
    def reverse_lookup(self, flag_emoji: str) -> Optional[str]:
        """
        Get the country name for a flag emoji.
        
        Args:
            flag_emoji: The flag emoji to look up.
            
        Returns:
            str: The country name, or None if the flag is not found.
        """
        if flag_emoji in self._flag_map:
            return self._flag_map[flag_emoji].name
        return None


# Example data file (sample_countries.json)
SAMPLE_DATA = [
    {
        "name": "United States",
        "iso2": "US",
        "iso3": "USA",
        "official_name": "United States of America",
        "region": "Americas",
        "subregion": "Northern America"
    },
    {
        "name": "Canada",
        "iso2": "CA",
        "iso3": "CAN",
        "official_name": "Canada",
        "region": "Americas",
        "subregion": "Northern America"
    },
    {
        "name": "Germany",
        "iso2": "DE",
        "iso3": "DEU",
        "official_name": "Federal Republic of Germany",
        "region": "Europe",
        "subregion": "Western Europe"
    },
    {
        "name": "France",
        "iso2": "FR",
        "iso3": "FRA",
        "official_name": "French Republic",
        "region": "Europe",
        "subregion": "Western Europe"
    }
]


def create_sample_data_file(output_file: str = "sample_countries.json") -> str:
    """
    Create a sample data file for the custom data source plugin.
    
    Args:
        output_file: Path to the output file.
        
    Returns:
        str: Path to the created file.
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(SAMPLE_DATA, f, indent=2)
    return output_file


def example_usage():
    """Example usage of the custom data source plugin."""
    # Create a sample data file
    data_file = create_sample_data_file()
    
    # Create the plugin
    plugin = CustomDataSourcePlugin(data_file)
    
    # Register the plugin with countryflag
    from countryflag.plugins import register_plugin
    register_plugin("custom_data", plugin)
    
    # Use the plugin with CountryFlag
    from countryflag.core import CountryFlag
    cf = CountryFlag()
    
    # Get a flag
    flags, pairs = cf.get_flag(["United States", "Germany"])
    print("Flags:", flags)
    print("Pairs:", pairs)
    
    # Get countries by region
    flags, pairs = cf.get_flags_by_region("Europe")
    print("European flags:", flags)
    print("European pairs:", pairs)
    
    # Clean up
    import os
    os.remove(data_file)


if __name__ == "__main__":
    example_usage()
