"""
Pytest configuration file with fixtures for countryflag tests.
"""

import os
import tempfile
from pathlib import Path
from typing import Any, Dict, Generator, List

import pandas as pd
import pytest
from country_converter import CountryConverter

from countryflag.cache import Cache, MemoryCache
from countryflag.core.models import CountryInfo


@pytest.fixture
def sample_country_names() -> List[str]:
    """Return a list of sample country names for testing."""
    return ["United States", "Canada", "Germany", "Japan", "Brazil"]


@pytest.fixture
def sample_iso2_codes() -> List[str]:
    """Return a list of sample ISO2 codes for testing."""
    return ["US", "CA", "DE", "JP", "BR"]


@pytest.fixture
def sample_emoji_flags() -> List[str]:
    """Return a list of sample emoji flags for testing."""
    return ["🇺🇸", "🇨🇦", "🇩🇪", "🇯🇵", "🇧🇷"]


@pytest.fixture
def sample_country_infos(sample_country_names, sample_iso2_codes) -> List[CountryInfo]:
    """Return a list of sample CountryInfo objects for testing."""
    country_infos = []
    for i, (name, iso2) in enumerate(zip(sample_country_names, sample_iso2_codes)):
        country_infos.append(
            CountryInfo(
                name=name,
                iso2=iso2,
                iso3=f"{iso2}X",
                official_name=f"Official name of {name}",
                region="Region" if i % 2 == 0 else "Other Region",
                subregion="Subregion" if i % 3 == 0 else "Other Subregion",
            )
        )
    return country_infos


@pytest.fixture
def temp_countries_file() -> Generator[str, None, None]:
    """Create a temporary file with country names for testing file input."""
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as temp_file:
        temp_file.write("United States\nCanada\nGermany\nJapan\nBrazil\n")
        temp_file_path = temp_file.name

    yield temp_file_path

    # Clean up
    os.unlink(temp_file_path)


@pytest.fixture
def temp_cache_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for cache testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def memory_cache() -> Cache:
    """Return a memory cache instance for testing."""
    return MemoryCache()


@pytest.fixture
def mock_country_converter_data() -> pd.DataFrame:
    """Create mock data for the CountryConverter."""
    data = {
        "name_short": ["United States", "Canada", "Germany", "Japan", "Brazil"],
        "ISO2": ["US", "CA", "DE", "JP", "BR"],
        "ISO3": ["USA", "CAN", "DEU", "JPN", "BRA"],
        "name_official": [
            "United States of America",
            "Canada",
            "Federal Republic of Germany",
            "Japan",
            "Federative Republic of Brazil",
        ],
        "region": ["Americas", "Americas", "Europe", "Asia", "Americas"],
        "sub_region": [
            "Northern America",
            "Northern America",
            "Western Europe",
            "Eastern Asia",
            "South America",
        ],
    }
    return pd.DataFrame(data)


@pytest.fixture
def mock_country_converter(monkeypatch, mock_country_converter_data) -> None:
    """Patch the CountryConverter to use mock data."""

    def mock_coco_convert(names, to="ISO3"):
        """Mock country_converter.convert function."""
        # Handle single string input
        if isinstance(names, str):
            name = names.strip().lower()
            # Look up in the mock data
            for _, row in mock_country_converter_data.iterrows():
                if (
                    row["name_short"].lower() == name
                    or row["ISO2"].lower() == name
                    or row["ISO3"].lower() == name
                ):
                    if to == "ISO2":
                        return row["ISO2"]
                    elif to == "ISO3":
                        return row["ISO3"]
                    else:
                        return row["name_short"]
            return "not found"

        # Handle list input (return list)
        if isinstance(names, list):
            return [mock_coco_convert(name, to) for name in names]

        return "not found"

    class MockCountryConverter:
        def __init__(self, *args, **kwargs):
            self.data = mock_country_converter_data

        def convert(self, names, to="ISO2"):
            """Mock convert method that handles country name to ISO code conversion."""
            return mock_coco_convert(names, to)

        def get_countries_by_region(self, region):
            """Mock method to get countries by region."""
            import flag

            from countryflag.core.models import CountryInfo

            countries = []
            for _, row in self.data.iterrows():
                if row["region"].lower() == region.lower():
                    try:
                        country_info = CountryInfo(
                            name=row["name_short"],
                            iso2=row["ISO2"],
                            iso3=row["ISO3"],
                            official_name=row["name_official"],
                            region=row["region"],
                            subregion=row["sub_region"],
                            flag=flag.flag(row["ISO2"]),
                        )
                        countries.append(country_info)
                    except Exception:
                        # Skip if flag generation fails
                        pass
            return countries

    # Patch the coco.convert function that's used directly
    import country_converter as coco

    monkeypatch.setattr(coco, "convert", mock_coco_convert)

    # Patch the CountryConverter class methods
    monkeypatch.setattr(CountryConverter, "__init__", MockCountryConverter.__init__)
    monkeypatch.setattr(CountryConverter, "convert", MockCountryConverter.convert)
    monkeypatch.setattr(
        CountryConverter,
        "get_countries_by_region",
        MockCountryConverter.get_countries_by_region,
    )

    # Reset the singleton to ensure clean state for tests
    from countryflag.core.converters import CountryConverterSingleton

    CountryConverterSingleton._CountryConverterSingleton__instance = None
