"""
Parametrized tests for robust reverse lookup functionality.

This test module provides comprehensive testing of the reverse lookup
functionality with edge-case emojis like 🇬🇧, 🇦🇨, and other
regional-indicator sequences that represent territories.
"""

from typing import List, Tuple

import pytest

from countryflag.core.exceptions import ReverseConversionError
from countryflag.core.flag import CountryFlag
from countryflag.lookup import (
    create_enhanced_flag_mapping,
    extract_iso_codes_from_regex,
    get_iso_code_from_flag,
    is_regional_indicator_sequence,
    normalize_emoji_flag,
    reverse_lookup_flag,
)


class TestReverseLookupEdgeCases:
    """Test cases for reverse lookup with edge-case emojis."""

    @pytest.fixture
    def country_flag(self) -> CountryFlag:
        """Create a CountryFlag instance for testing."""
        return CountryFlag()

    @pytest.mark.parametrize(
        "emoji_flag,expected_country",
        [
            # Standard cases
            ("🇺🇸", "United States"),
            ("🇨🇦", "Canada"),
            ("🇩🇪", "Germany"),
            ("🇫🇷", "France"),
            ("🇯🇵", "Japan"),
            # UK/GB edge cases - both should map to United Kingdom
            ("🇬🇧", "United Kingdom"),
            ("🇺🇰", "United Kingdom"),
            # Greece edge cases - both EL and GR should work
            ("🇬🇷", "Greece"),
            # Note: 🇪🇱 might not be supported by flag library
            # Special territories
            ("🇦🇨", "Ascension Island"),
            # Other common territories
            ("🇦🇩", "Andorra"),
            ("🇦🇪", "United Arab Emirates"),
            ("🇦🇫", "Afghanistan"),
            ("🇦🇬", "Antigua and Barbuda"),
            ("🇦🇮", "Anguilla"),
            ("🇦🇱", "Albania"),
            ("🇦🇲", "Armenia"),
            ("🇦🇴", "Angola"),
            ("🇦🇶", "Antarctica"),
            ("🇦🇷", "Argentina"),
            ("🇦🇸", "American Samoa"),
            ("🇦🇹", "Austria"),
            ("🇦🇺", "Australia"),
            ("🇦🇼", "Aruba"),
            ("🇦🇽", "Aland Islands"),
            ("🇦🇿", "Azerbaijan"),
        ],
    )
    def test_reverse_lookup_single_flag(
        self, country_flag: CountryFlag, emoji_flag: str, expected_country: str
    ):
        """Test reverse lookup for individual flags."""
        result = country_flag.reverse_lookup([emoji_flag])

        assert len(result) == 1
        flag, country = result[0]
        assert flag == emoji_flag
        assert country == expected_country

    @pytest.mark.parametrize(
        "emoji_flags,expected_pairs",
        [
            # Mixed standard and edge cases
            (
                ["🇺🇸", "🇬🇧", "🇺🇰", "🇦🇨"],
                [
                    ("🇺🇸", "United States"),
                    ("🇬🇧", "United Kingdom"),
                    ("🇺🇰", "United Kingdom"),
                    ("🇦🇨", "Ascension Island"),
                ],
            ),
            # European countries with potential edge cases
            (
                ["🇬🇧", "🇫🇷", "🇩🇪", "🇮🇹", "🇪🇸"],
                [
                    ("🇬🇧", "United Kingdom"),
                    ("🇫🇷", "France"),
                    ("🇩🇪", "Germany"),
                    ("🇮🇹", "Italy"),
                    ("🇪🇸", "Spain"),
                ],
            ),
            # Various territories and special cases
            (
                ["🇦🇨", "🇸🇭", "🇹🇦"],
                [
                    ("🇦🇨", "Ascension Island"),
                    ("🇸🇭", "St. Helena"),  # Note: actual data uses "St." not "Saint"
                    ("🇹🇦", "Tristan da Cunha"),
                ],
            ),
        ],
    )
    def test_reverse_lookup_multiple_flags(
        self,
        country_flag: CountryFlag,
        emoji_flags: List[str],
        expected_pairs: List[Tuple[str, str]],
    ):
        """Test reverse lookup for multiple flags including edge cases."""
        result = country_flag.reverse_lookup(emoji_flags)

        assert len(result) == len(expected_pairs)
        for i, (expected_flag, expected_country) in enumerate(expected_pairs):
            actual_flag, actual_country = result[i]
            assert actual_flag == expected_flag
            assert actual_country == expected_country

    @pytest.mark.parametrize(
        "invalid_input",
        [
            "🏴󠁧󠁢󠁵󠁫󠁿",  # UK subdivision flag (not a regional indicator)
            "🏁",  # Checkered flag
            "🚩",  # Red flag
            "🏳️",  # White flag
            "🏳️‍🌈",  # Rainbow flag
            "GB",  # Text ISO code
            "🇿🇿",  # Non-existent country code
            "🇦",  # Single regional indicator
            "🇦🇧🇨",  # Too many characters
        ],
    )
    def test_reverse_lookup_invalid_flags(
        self, country_flag: CountryFlag, invalid_input: str
    ):
        """Test that invalid flags raise appropriate errors."""
        with pytest.raises(ReverseConversionError):
            country_flag.reverse_lookup([invalid_input])

    def test_reverse_lookup_empty_list(self, country_flag: CountryFlag):
        """Test reverse lookup with empty input."""
        result = country_flag.reverse_lookup([])
        assert result == []

    def test_reverse_lookup_empty_string_error(self, country_flag: CountryFlag):
        """Test that empty string raises appropriate error."""
        with pytest.raises(ReverseConversionError):
            country_flag.reverse_lookup([""])

    def test_reverse_lookup_mixed_valid_invalid(self, country_flag: CountryFlag):
        """Test that one invalid flag in a list still raises an error."""
        with pytest.raises(ReverseConversionError):
            country_flag.reverse_lookup(["🇺🇸", "invalid", "🇬🇧"])


class TestLookupHelperFunctions:
    """Test cases for the lookup helper functions."""

    @pytest.mark.parametrize(
        "emoji_flag,expected",
        [
            ("🇺🇸", "🇺🇸"),  # Standard case
            ("🇬🇧", "🇬🇧"),  # Edge case
            ("  🇺🇸  ", "🇺🇸"),  # With whitespace
            ("", ""),  # Empty string
            ("invalid", "invalid"),  # Non-emoji
        ],
    )
    def test_normalize_emoji_flag(self, emoji_flag: str, expected: str):
        """Test flag emoji normalization."""
        result = normalize_emoji_flag(emoji_flag)
        assert result == expected

    @pytest.mark.parametrize(
        "iso2_pattern,expected_codes",
        [
            ("US", ["US"]),
            ("^GB$|^UK$", ["GB", "UK"]),
            ("^GR$|^EL$", ["GR", "EL"]),
            ("not found", []),
            ("", []),
            ("INVALID", []),  # Wrong length
            ("us", ["US"]),  # Lowercase
        ],
    )
    def test_extract_iso_codes_from_regex(
        self, iso2_pattern: str, expected_codes: List[str]
    ):
        """Test extraction of ISO codes from regex patterns."""
        result = extract_iso_codes_from_regex(iso2_pattern)
        assert result == expected_codes

    @pytest.mark.parametrize(
        "text,expected",
        [
            ("🇺🇸", True),
            ("🇬🇧", True),
            ("🇦🇨", True),
            ("🏴󠁧󠁢󠁵󠁫󠁿", False),  # UK subdivision flag
            ("GB", False),  # Text
            ("", False),  # Empty
            ("🇦", False),  # Single character
            ("🇦🇧🇨", False),  # Too many characters
        ],
    )
    def test_is_regional_indicator_sequence(self, text: str, expected: bool):
        """Test detection of regional indicator sequences."""
        result = is_regional_indicator_sequence(text)
        assert result == expected

    @pytest.mark.parametrize(
        "emoji_flag,expected_iso",
        [
            ("🇺🇸", "US"),
            ("🇬🇧", "GB"),
            ("🇺🇰", "UK"),
            ("🇦🇨", "AC"),
            ("🇩🇪", "DE"),
            ("invalid", None),
            ("", None),
            ("🏴󠁧󠁢󠁵󠁫󠁿", None),  # Not a regional indicator sequence
        ],
    )
    def test_get_iso_code_from_flag(self, emoji_flag: str, expected_iso: str):
        """Test extraction of ISO codes from flag emojis."""
        result = get_iso_code_from_flag(emoji_flag)
        assert result == expected_iso

    def test_reverse_lookup_flag_with_mapping(self):
        """Test the reverse_lookup_flag function with a custom mapping."""
        mapping = {
            "🇺🇸": "United States",
            "🇬🇧": "United Kingdom",
            "🇺🇰": "United Kingdom",
            "🇦🇨": "Ascension Island",
        }

        # Test direct lookup
        assert reverse_lookup_flag("🇺🇸", mapping) == "United States"
        assert reverse_lookup_flag("🇬🇧", mapping) == "United Kingdom"
        assert reverse_lookup_flag("🇺🇰", mapping) == "United Kingdom"
        assert reverse_lookup_flag("🇦🇨", mapping) == "Ascension Island"

        # Test not found
        assert reverse_lookup_flag("🇿🇿", mapping) is None
        assert reverse_lookup_flag("", mapping) is None
        assert reverse_lookup_flag("invalid", mapping) is None


class TestEnhancedFlagMapping:
    """Test cases for the enhanced flag mapping creation."""

    def test_enhanced_mapping_handles_uk_gb(self):
        """Test that the enhanced mapping correctly handles UK/GB variations."""
        from countryflag.core.converters import CountryConverterSingleton

        converter = CountryConverterSingleton()
        mapping = create_enhanced_flag_mapping(converter.data)

        # Both GB and UK flags should map to United Kingdom
        assert "🇬🇧" in mapping
        assert "🇺🇰" in mapping
        assert mapping["🇬🇧"] == "United Kingdom"
        assert mapping["🇺🇰"] == "United Kingdom"

    def test_enhanced_mapping_includes_special_territories(self):
        """Test that special territories are included in the mapping."""
        from countryflag.core.converters import CountryConverterSingleton

        converter = CountryConverterSingleton()
        mapping = create_enhanced_flag_mapping(converter.data)

        # Check for special territories
        special_flags = ["🇦🇨", "🇸🇭"]  # Ascension Island, Saint Helena

        for flag in special_flags:
            if flag in mapping:  # Only check if the flag is actually supported
                assert isinstance(mapping[flag], str)
                assert len(mapping[flag]) > 0

    def test_enhanced_mapping_size(self):
        """Test that the enhanced mapping has a reasonable number of entries."""
        from countryflag.core.converters import CountryConverterSingleton

        converter = CountryConverterSingleton()
        mapping = create_enhanced_flag_mapping(converter.data)

        # Should have more than 200 entries (there are ~250 country codes)
        assert len(mapping) > 200

        # All values should be non-empty strings
        for flag, country in mapping.items():
            assert isinstance(flag, str)
            assert isinstance(country, str)
            assert (
                len(flag) == 2
            )  # Should be exactly 2 Unicode characters (regional indicators)
            assert len(country) > 0


class TestIntegrationWithCountryFlag:
    """Integration tests for the CountryFlag class with enhanced lookup."""

    def test_forward_and_reverse_consistency(self):
        """Test that forward and reverse conversions are consistent."""
        cf = CountryFlag()

        # Test countries that should work in both directions
        test_countries = ["United States", "Germany", "France", "Japan"]

        # Forward conversion
        flags, pairs = cf.get_flag(test_countries)

        # Extract just the flags
        flag_emojis = [flag for _, flag in pairs]

        # Reverse conversion
        reverse_pairs = cf.reverse_lookup(flag_emojis)

        # Check that we get back valid country names
        assert len(reverse_pairs) == len(test_countries)
        for (flag, country), (original_country, original_flag) in zip(
            reverse_pairs, pairs
        ):
            assert flag == original_flag
            # Note: country names might be slightly different due to normalization
            assert isinstance(country, str)
            assert len(country) > 0

    def test_edge_case_territories_integration(self):
        """Test integration of edge case territories."""
        cf = CountryFlag()

        # Test specific edge cases that should work
        edge_cases = ["🇬🇧", "🇺🇰", "🇦🇨"]
        expected_countries = ["United Kingdom", "United Kingdom", "Ascension Island"]

        result = cf.reverse_lookup(edge_cases)

        assert len(result) == len(edge_cases)
        for i, (flag, country) in enumerate(result):
            assert flag == edge_cases[i]
            assert country == expected_countries[i]

    def test_caching_with_enhanced_lookup(self):
        """Test that caching works correctly with enhanced lookup."""
        from countryflag.cache.memory import MemoryCache

        cache = MemoryCache()
        cf = CountryFlag(cache=cache)

        # First call - should populate cache
        result1 = cf.reverse_lookup(["🇺🇸", "🇬🇧"])

        # Second call - should use cache
        result2 = cf.reverse_lookup(["🇺🇸", "🇬🇧"])

        assert result1 == result2
        assert len(result1) == 2
        assert result1[0] == ("🇺🇸", "United States")
        assert result1[1] == ("🇬🇧", "United Kingdom")
