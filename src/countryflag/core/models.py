"""
Data models for the countryflag package.

This module contains data classes and models used throughout the countryflag package.
"""

from dataclasses import dataclass
from typing import ClassVar, List

import flag


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
        if not self.flag:
            object.__setattr__(self, "flag", flag.flag(self.iso2))


class RegionDefinitions:
    """
    Class containing definitions of regions/continents.

    This class provides standard region names and groupings.
    """

    # Define the supported regions
    REGIONS: ClassVar[List[str]] = ["Africa", "Americas", "Asia", "Europe", "Oceania"]
