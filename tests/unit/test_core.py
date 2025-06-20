"""
Unit tests for the core module.
"""

import pytest
from unittest.mock import patch, MagicMock

from countryflag.core.models import CountryInfo
from countryflag.core.converters import CountryConverterSingleton
from countryflag.core.flag import CountryFlag
from countryflag.core.exceptions import (
    InvalidCountryError,
    ReverseConversionError,
    RegionError,
)


class TestCountryInfo:
    """Tests for the CountryInfo class."""
    
    def test_init(self):
        """Test that a CountryInfo can be initialized."""
        country_info = CountryInfo(
            name="United States",
            iso2="US",
            iso3="USA",
            official_name="United States of America",
        )
        assert country_info.name == "United States"
        assert country_info.iso2 == "US"
        assert country_info.iso3 == "USA"
        assert country_info.official_name == "United States of America"
        assert country_info.flag == "🇺🇸"
    
    def test_init_with_region(self):
        """Test that a CountryInfo can be initialized with region info."""
        country_info = CountryInfo(
            name="United States",
            iso2="US",
            iso3="USA",
            official_name="United States of America",
            region="Americas",
            subregion="Northern America",
        )
        assert country_info.region == "Americas"
        assert country_info.subregion == "Northern America"
    
    def test_init_with_flag(self):
        """Test that a CountryInfo can be initialized with a flag."""
        country_info = CountryInfo(
            name="United States",
            iso2="US",
            iso3="USA",
            official_name="United States of America",
            flag="🇺🇸",
        )
        assert country_info.flag == "🇺🇸"


class TestCountryConverterSingleton:
    """Tests for the CountryConverterSingleton class."""
    
    def test_singleton(self):
        """Test that CountryConverterSingleton is a singleton."""
        converter1 = CountryConverterSingleton()
        converter2 = CountryConverterSingleton()
        assert converter1 is converter2
    
    def test_convert(self, mock_country_converter):
        """Test that convert() converts country names to ISO2 codes."""
        converter = CountryConverterSingleton()
        assert converter.convert("United States") == "US"
    
    def test_get_iso2_to_country_mapping(self, mock_country_converter):
        """Test that get_iso2_to_country_mapping() returns a dictionary."""
        converter = CountryConverterSingleton()
        mapping = converter.get_iso2_to_country_mapping()
        assert isinstance(mapping, dict)
        assert "US" in mapping
        assert mapping["US"] == "United States"
    
    def test_get_supported_regions(self):
        """Test that get_supported_regions() returns a list of regions."""
        converter = CountryConverterSingleton()
        regions = converter.get_supported_regions()
        assert isinstance(regions, list)
        assert "Europe" in regions
    
    def test_get_countries_by_region(self, mock_country_converter):
        """Test that get_countries_by_region() returns countries in a region."""
        converter = CountryConverterSingleton()
        countries = converter.get_countries_by_region("Europe")
        assert isinstance(countries, list)
        assert any(country.name == "Germany" for country in countries)
    
    def test_get_countries_by_region_invalid(self):
        """Test that get_countries_by_region() raises RegionError for invalid regions."""
        converter = CountryConverterSingleton()
        with pytest.raises(RegionError):
            converter.get_countries_by_region("Invalid Region")
    
    def test_get_flag_to_country_mapping(self, mock_country_converter):
        """Test that get_flag_to_country_mapping() returns a dictionary."""
        converter = CountryConverterSingleton()
        mapping = converter.get_flag_to_country_mapping()
        assert isinstance(mapping, dict)
        assert "🇺🇸" in mapping
        assert mapping["🇺🇸"] == "United States"
    
    def test_find_close_matches(self, mock_country_converter):
        """Test that find_close_matches() returns similar country names."""
        converter = CountryConverterSingleton()
        matches = converter.find_close_matches("Germny")
        assert isinstance(matches, list)
        assert len(matches) > 0
        assert matches[0][0] == "Germany"


class TestCountryFlag:
    """Tests for the CountryFlag class."""
    
    def test_init(self):
        """Test that a CountryFlag can be initialized."""
        cf = CountryFlag()
        assert cf._language == "en"
        assert cf._cache is None
    
    def test_init_with_language(self):
        """Test that a CountryFlag can be initialized with a language."""
        cf = CountryFlag(language="fr")
        assert cf._language == "fr"
    
    def test_init_with_cache(self, memory_cache):
        """Test that a CountryFlag can be initialized with a cache."""
        cf = CountryFlag(cache=memory_cache)
        assert cf._cache is memory_cache
    
    def test_set_language(self):
        """Test that set_language() changes the language."""
        cf = CountryFlag()
        cf.set_language("fr")
        assert cf._language == "fr"
    
    def test_validate_country_name(self, mock_country_converter):
        """Test that validate_country_name() returns True for valid countries."""
        cf = CountryFlag()
        assert cf.validate_country_name("United States") is True
        assert cf.validate_country_name("Invalid Country") is False
    
    def test_get_supported_countries(self, mock_country_converter):
        """Test that get_supported_countries() returns a list of dictionaries."""
        cf = CountryFlag()
        countries = cf.get_supported_countries()
        assert isinstance(countries, list)
        assert all(isinstance(country, dict) for country in countries)
        assert all("name" in country for country in countries)
        assert all("iso2" in country for country in countries)
    
    def test_get_flags_by_region(self, mock_country_converter):
        """Test that get_flags_by_region() returns flags for a region."""
        cf = CountryFlag()
        flags, pairs = cf.get_flags_by_region("Europe")
        assert isinstance(flags, str)
        assert isinstance(pairs, list)
        assert len(pairs) > 0
    
    def test_get_flags_by_region_invalid(self):
        """Test that get_flags_by_region() raises RegionError for invalid regions."""
        cf = CountryFlag()
        with pytest.raises(RegionError):
            cf.get_flags_by_region("Invalid Region")
    
    def test_get_flag(self, mock_country_converter):
        """Test that get_flag() returns flags for country names."""
        cf = CountryFlag()
        flags, pairs = cf.get_flag(["United States", "Canada"])
        assert flags == "🇺🇸 🇨🇦"
        assert pairs == [("United States", "🇺🇸"), ("Canada", "🇨🇦")]
    
    def test_get_flag_with_separator(self, mock_country_converter):
        """Test that get_flag() respects the separator parameter."""
        cf = CountryFlag()
        flags, pairs = cf.get_flag(["United States", "Canada"], separator="|")
        assert flags == "🇺🇸|🇨🇦"
    
    def test_get_flag_with_fuzzy_matching(self, mock_country_converter):
        """Test that get_flag() uses fuzzy matching when enabled."""
        cf = CountryFlag()
        
        # Patch the find_close_matches method to return a specific result
        with patch.object(CountryConverterSingleton, "find_close_matches") as mock_find:
            mock_find.return_value = [("Germany", "DE")]
            
            flags, pairs = cf.get_flag(["Germny"], fuzzy_matching=True)
            assert flags == "🇩🇪"
            assert pairs == [("Germany", "🇩🇪")]
            
            # Check that find_close_matches was called
            mock_find.assert_called_once()
    
    def test_get_flag_invalid_country(self, mock_country_converter):
        """Test that get_flag() raises InvalidCountryError for invalid countries."""
        cf = CountryFlag()
        with pytest.raises(InvalidCountryError):
            cf.get_flag(["Invalid Country"])
    
    def test_reverse_lookup(self, mock_country_converter):
        """Test that reverse_lookup() returns country names for flags."""
        cf = CountryFlag()
        pairs = cf.reverse_lookup(["🇺🇸", "🇨🇦"])
        assert pairs == [("🇺🇸", "United States"), ("🇨🇦", "Canada")]
    
    def test_reverse_lookup_invalid_flag(self, mock_country_converter):
        """Test that reverse_lookup() raises ReverseConversionError for invalid flags."""
        cf = CountryFlag()
        with pytest.raises(ReverseConversionError):
            cf.reverse_lookup(["🏴"])
    
    def test_format_output_text(self, mock_country_converter):
        """Test that format_output() formats output as text."""
        cf = CountryFlag()
        pairs = [("United States", "🇺🇸"), ("Canada", "🇨🇦")]
        output = cf.format_output(pairs, output_format="text")
        assert output == "🇺🇸 🇨🇦"
    
    def test_format_output_json(self, mock_country_converter):
        """Test that format_output() formats output as JSON."""
        cf = CountryFlag()
        pairs = [("United States", "🇺🇸"), ("Canada", "🇨🇦")]
        output = cf.format_output(pairs, output_format="json")
        assert '"country": "United States"' in output
        assert '"flag": "🇺🇸"' in output
    
    def test_format_output_csv(self, mock_country_converter):
        """Test that format_output() formats output as CSV."""
        cf = CountryFlag()
        pairs = [("United States", "🇺🇸"), ("Canada", "🇨🇦")]
        output = cf.format_output(pairs, output_format="csv")
        assert "United States,🇺🇸" in output
        assert "Canada,🇨🇦" in output
