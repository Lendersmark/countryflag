"""
Pytest configuration file with fixtures for countryflag tests.
"""
import os
import tempfile
from pathlib import Path
from typing import Dict, List, Generator, Any

import pytest
import pandas as pd
from country_converter import CountryConverter

from countryflag.core.models import CountryInfo
from countryflag.core.cache import Cache, MemoryCache


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
    
    class MockCountryConverter:
        def __init__(self, *args, **kwargs):
            self.data = mock_country_converter_data
    
    monkeypatch.setattr(CountryConverter, "__init__", MockCountryConverter.__init__)
