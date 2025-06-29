"""
Property-based tests for the countryflag package.

This module contains property-based tests that use hypothesis to test
the properties of the countryflag package.
"""

import concurrent.futures
import threading

import pytest
from hypothesis import assume, example, given, settings
from hypothesis import strategies as st
from hypothesis.stateful import Bundle, RuleBasedStateMachine, initialize, rule
from hypothesis.strategies import composite

from countryflag.cache.disk import DiskCache
from countryflag.cache.memory import MemoryCache
from countryflag.core.converters import CountryConverterSingleton
from countryflag.core.exceptions import InvalidCountryError
from countryflag.core.flag import CountryFlag
from countryflag.core.models import CountryInfo

# Define common strategies
country_names_strategy = st.sampled_from(
    [
        "United States",
        "Canada",
        "Germany",
        "Japan",
        "Brazil",
        "France",
        "Italy",
        "Spain",
        "United Kingdom",
        "Australia",
        "China",
        "India",
        "Russia",
        "Mexico",
        "South Korea",
    ]
)

# Strategy for valid country lists
valid_country_lists = st.lists(country_names_strategy, min_size=1)

# Strategy for separators
separator_strategy = st.text(min_size=1, max_size=5)

# Strategy for output formats
output_format_strategy = st.sampled_from(["text", "json", "csv"])


# Composite strategies that include mock setup
@composite
def country_list_with_mock(draw):
    """Generate a country list and set up mock."""
    from unittest.mock import patch

    import pandas as pd

    countries = draw(valid_country_lists)

    # Create expanded mock data to include all countries used in tests
    mock_data = {
        "name_short": [
            "United States",
            "Canada",
            "Germany",
            "Japan",
            "Brazil",
            "France",
            "Italy",
            "Spain",
            "United Kingdom",
            "Australia",
            "China",
            "India",
            "Russia",
            "Mexico",
            "South Korea",
        ],
        "ISO2": [
            "US",
            "CA",
            "DE",
            "JP",
            "BR",
            "FR",
            "IT",
            "ES",
            "GB",
            "AU",
            "CN",
            "IN",
            "RU",
            "MX",
            "KR",
        ],
        "ISO3": [
            "USA",
            "CAN",
            "DEU",
            "JPN",
            "BRA",
            "FRA",
            "ITA",
            "ESP",
            "GBR",
            "AUS",
            "CHN",
            "IND",
            "RUS",
            "MEX",
            "KOR",
        ],
        "name_official": [
            "United States of America",
            "Canada",
            "Federal Republic of Germany",
            "Japan",
            "Federative Republic of Brazil",
            "French Republic",
            "Italian Republic",
            "Kingdom of Spain",
            "United Kingdom of Great Britain and Northern Ireland",
            "Commonwealth of Australia",
            "People's Republic of China",
            "Republic of India",
            "Russian Federation",
            "United Mexican States",
            "Republic of Korea",
        ],
        "region": [
            "Americas",
            "Americas",
            "Europe",
            "Asia",
            "Americas",
            "Europe",
            "Europe",
            "Europe",
            "Europe",
            "Oceania",
            "Asia",
            "Asia",
            "Europe",
            "Americas",
            "Asia",
        ],
        "sub_region": [
            "Northern America",
            "Northern America",
            "Western Europe",
            "Eastern Asia",
            "South America",
            "Western Europe",
            "Southern Europe",
            "Southern Europe",
            "Northern Europe",
            "Australia and New Zealand",
            "Eastern Asia",
            "Southern Asia",
            "Eastern Europe",
            "Central America",
            "Eastern Asia",
        ],
    }

    return countries, pd.DataFrame(mock_data)


@composite
def country_list_and_separator_with_mock(draw):
    """Generate a country list, separator and set up mock."""
    import pandas as pd

    countries = draw(valid_country_lists)
    separator = draw(separator_strategy)

    # Use the same expanded mock data as the other functions
    mock_data = {
        "name_short": [
            "United States",
            "Canada",
            "Germany",
            "Japan",
            "Brazil",
            "France",
            "Italy",
            "Spain",
            "United Kingdom",
            "Australia",
            "China",
            "India",
            "Russia",
            "Mexico",
            "South Korea",
        ],
        "ISO2": [
            "US",
            "CA",
            "DE",
            "JP",
            "BR",
            "FR",
            "IT",
            "ES",
            "GB",
            "AU",
            "CN",
            "IN",
            "RU",
            "MX",
            "KR",
        ],
        "ISO3": [
            "USA",
            "CAN",
            "DEU",
            "JPN",
            "BRA",
            "FRA",
            "ITA",
            "ESP",
            "GBR",
            "AUS",
            "CHN",
            "IND",
            "RUS",
            "MEX",
            "KOR",
        ],
        "name_official": [
            "United States of America",
            "Canada",
            "Federal Republic of Germany",
            "Japan",
            "Federative Republic of Brazil",
            "French Republic",
            "Italian Republic",
            "Kingdom of Spain",
            "United Kingdom of Great Britain and Northern Ireland",
            "Commonwealth of Australia",
            "People's Republic of China",
            "Republic of India",
            "Russian Federation",
            "United Mexican States",
            "Republic of Korea",
        ],
        "region": [
            "Americas",
            "Americas",
            "Europe",
            "Asia",
            "Americas",
            "Europe",
            "Europe",
            "Europe",
            "Europe",
            "Oceania",
            "Asia",
            "Asia",
            "Europe",
            "Americas",
            "Asia",
        ],
        "sub_region": [
            "Northern America",
            "Northern America",
            "Western Europe",
            "Eastern Asia",
            "South America",
            "Western Europe",
            "Southern Europe",
            "Southern Europe",
            "Northern Europe",
            "Australia and New Zealand",
            "Eastern Asia",
            "Southern Asia",
            "Eastern Europe",
            "Central America",
            "Eastern Asia",
        ],
    }

    return countries, separator, pd.DataFrame(mock_data)


@composite
def country_list_and_format_with_mock(draw):
    """Generate a country list, output format and set up mock."""
    import pandas as pd

    countries = draw(valid_country_lists)
    output_format = draw(output_format_strategy)

    # Use the same expanded mock data as the other functions
    mock_data = {
        "name_short": [
            "United States",
            "Canada",
            "Germany",
            "Japan",
            "Brazil",
            "France",
            "Italy",
            "Spain",
            "United Kingdom",
            "Australia",
            "China",
            "India",
            "Russia",
            "Mexico",
            "South Korea",
        ],
        "ISO2": [
            "US",
            "CA",
            "DE",
            "JP",
            "BR",
            "FR",
            "IT",
            "ES",
            "GB",
            "AU",
            "CN",
            "IN",
            "RU",
            "MX",
            "KR",
        ],
        "ISO3": [
            "USA",
            "CAN",
            "DEU",
            "JPN",
            "BRA",
            "FRA",
            "ITA",
            "ESP",
            "GBR",
            "AUS",
            "CHN",
            "IND",
            "RUS",
            "MEX",
            "KOR",
        ],
        "name_official": [
            "United States of America",
            "Canada",
            "Federal Republic of Germany",
            "Japan",
            "Federative Republic of Brazil",
            "French Republic",
            "Italian Republic",
            "Kingdom of Spain",
            "United Kingdom of Great Britain and Northern Ireland",
            "Commonwealth of Australia",
            "People's Republic of China",
            "Republic of India",
            "Russian Federation",
            "United Mexican States",
            "Republic of Korea",
        ],
        "region": [
            "Americas",
            "Americas",
            "Europe",
            "Asia",
            "Americas",
            "Europe",
            "Europe",
            "Europe",
            "Europe",
            "Oceania",
            "Asia",
            "Asia",
            "Europe",
            "Americas",
            "Asia",
        ],
        "sub_region": [
            "Northern America",
            "Northern America",
            "Western Europe",
            "Eastern Asia",
            "South America",
            "Western Europe",
            "Southern Europe",
            "Southern Europe",
            "Northern Europe",
            "Australia and New Zealand",
            "Eastern Asia",
            "Southern Asia",
            "Eastern Europe",
            "Central America",
            "Eastern Asia",
        ],
    }

    return countries, output_format, pd.DataFrame(mock_data)


@given(country_list_with_mock())
def test_getflag_length(data):
    """Test that the number of flags returned matches the number of country names."""
    country_names, mock_data = data

    from unittest.mock import patch

    from countryflag.core.converters import CountryConverterSingleton

    # Patch the singleton instance
    with patch.object(CountryConverterSingleton, "__new__") as mock_singleton:
        # Create a proper mock converter with the convert method
        class MockConverter:
            def __init__(self):
                self.data = mock_data

            def convert(self, name, to="ISO2"):
                """Mock convert method."""
                name = name.strip().lower()
                for _, row in mock_data.iterrows():
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

        mock_instance = type(
            "MockInstance",
            (),
            {
                "data": mock_data,
                "_converter": MockConverter(),
                "convert": lambda self, name, to="ISO2": MockConverter().convert(
                    name, to
                ),
            },
        )()
        mock_singleton.return_value = mock_instance
        cf = CountryFlag()
        flags, pairs = cf.get_flag(country_names)

        # Split the flags by the separator (space)
        flag_list = flags.split(" ")

        # Check that we have the same number of flags as country names
        assert len(flag_list) == len(country_names)
        assert len(pairs) == len(country_names)


@given(country_list_and_separator_with_mock())
def test_getflag_separator(data):
    """Test that the separator is used correctly."""
    country_names, separator, mock_data = data

    from unittest.mock import patch

    from countryflag.core.converters import CountryConverterSingleton

    # Patch the singleton instance
    with patch.object(CountryConverterSingleton, "__new__") as mock_singleton:
        # Create a proper mock converter with the convert method
        class MockConverter:
            def __init__(self):
                self.data = mock_data

            def convert(self, name, to="ISO2"):
                """Mock convert method."""
                name = name.strip().lower()
                for _, row in mock_data.iterrows():
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

        mock_instance = type(
            "MockInstance",
            (),
            {
                "data": mock_data,
                "_converter": MockConverter(),
                "convert": lambda self, name, to="ISO2": MockConverter().convert(
                    name, to
                ),
            },
        )()
        mock_singleton.return_value = mock_instance
        cf = CountryFlag()
        flags, pairs = cf.get_flag(country_names, separator=separator)

        # Split the flags by the separator
        flag_list = flags.split(separator)

        # Check that we have the same number of flags as country names
        assert len(flag_list) == len(country_names)


@given(country_list_with_mock())
def test_reverse_lookup_round_trip(data):
    """Test that converting from country names to flags and back returns the original country names."""
    country_names, mock_data = data

    from unittest.mock import patch

    from countryflag.core.converters import CountryConverterSingleton

    class MockCountryConverter:
        def __init__(self, *args, **kwargs):
            self.data = mock_data

    # Patch the singleton instance
    with patch.object(CountryConverterSingleton, "__new__") as mock_singleton:
        # Create a proper mock converter with the convert method
        class MockConverter:
            def __init__(self):
                self.data = mock_data

            def convert(self, name, to="ISO2"):
                """Mock convert method."""
                name = name.strip().lower()
                for _, row in mock_data.iterrows():
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

        mock_instance = type(
            "MockInstance",
            (),
            {
                "data": mock_data,
                "_converter": MockConverter(),
                "convert": lambda self, name, to="ISO2": MockConverter().convert(
                    name, to
                ),
                "get_flag_to_country_mapping": lambda self: {
                    "🇺🇸": "United States",
                    "🇨🇦": "Canada",
                    "🇩🇪": "Germany",
                    "🇯🇵": "Japan",
                    "🇧🇷": "Brazil",
                    "🇫🇷": "France",
                    "🇮🇹": "Italy",
                    "🇪🇸": "Spain",
                    "🇬🇧": "United Kingdom",
                    "🇦🇺": "Australia",
                    "🇨🇳": "China",
                    "🇮🇳": "India",
                    "🇷🇺": "Russia",
                    "🇲🇽": "Mexico",
                    "🇰🇷": "South Korea",
                },
            },
        )()
        mock_singleton.return_value = mock_instance
        cf = CountryFlag()
        flags, pairs = cf.get_flag(country_names)

        # Extract the flags
        flag_list = [flag for _, flag in pairs]

        # Convert the flags back to country names
        reverse_pairs = cf.reverse_lookup(flag_list)
        reverse_country_names = [country for _, country in reverse_pairs]

        # Check that we get the original country names back
        assert len(reverse_country_names) == len(country_names)
        for i, country in enumerate(country_names):
            assert reverse_country_names[i] == country


@given(st.sampled_from(["Africa", "Americas", "Asia", "Europe", "Oceania"]))
def test_get_flags_by_region(region):
    """Test that get_flags_by_region returns flags for countries in the region."""
    from unittest.mock import patch

    import pandas as pd

    from countryflag.core.converters import CountryConverterSingleton

    # Create mock data for the specific region
    mock_data = {
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
        "region": [region] * 5,  # All countries in the specified region
        "sub_region": [
            "Northern America",
            "Northern America",
            "Western Europe",
            "Eastern Asia",
            "South America",
        ],
    }

    class MockCountryConverter:
        def __init__(self, *args, **kwargs):
            self.data = pd.DataFrame(mock_data)

    # Patch the singleton instance
    with patch.object(CountryConverterSingleton, "__new__") as mock_singleton:
        # Create a proper mock converter with the convert method
        class MockConverter:
            def __init__(self):
                self.data = pd.DataFrame(mock_data)

            def convert(self, name, to="ISO2"):
                """Mock convert method."""
                name = name.strip().lower()
                for _, row in self.data.iterrows():
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

        mock_instance = type(
            "MockInstance",
            (),
            {
                "data": pd.DataFrame(mock_data),
                "_converter": MockConverter(),
                "convert": lambda self, name, to="ISO2": MockConverter().convert(
                    name, to
                ),
                "get_countries_by_region": lambda self, region: MockConverter().get_countries_by_region(
                    region
                ),
            },
        )()
        mock_singleton.return_value = mock_instance
        cf = CountryFlag()
        flags, pairs = cf.get_flags_by_region(region)

        # Check that we got some flags
        assert len(pairs) > 0

        # Check that all countries are in the specified region
        converter = CountryConverterSingleton()
        countries = converter.get_countries_by_region(region)
        country_names = [country.name for country in countries]

        for country, _ in pairs:
            assert country in country_names


@given(country_list_and_format_with_mock())
def test_format_output(data):
    """Test that format_output returns output in the specified format."""
    country_names, output_format, mock_data = data

    from unittest.mock import patch

    from countryflag.core.converters import CountryConverterSingleton

    # Patch the singleton instance
    with patch.object(CountryConverterSingleton, "__new__") as mock_singleton:
        # Create a proper mock converter with the convert method
        class MockConverter:
            def __init__(self):
                self.data = mock_data

            def convert(self, name, to="ISO2"):
                """Mock convert method."""
                name = name.strip().lower()
                for _, row in mock_data.iterrows():
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

        mock_instance = type(
            "MockInstance",
            (),
            {
                "data": mock_data,
                "_converter": MockConverter(),
                "convert": lambda self, name, to="ISO2": MockConverter().convert(
                    name, to
                ),
            },
        )()
        mock_singleton.return_value = mock_instance
        cf = CountryFlag()
        flags, pairs = cf.get_flag(country_names)
        output = cf.format_output(pairs, output_format=output_format)

        # Check that we got some output
        assert len(output) > 0

        # Check the format
        if output_format == "text":
            # Text format should contain the flags
            for _, flag in pairs:
                assert flag in output
        elif output_format == "json":
            # JSON format should contain the country names and flags
            for country, flag in pairs:
                assert f'"country": "{country}"' in output
                assert f'"flag": "{flag}"' in output
        elif output_format == "csv":
            # CSV format should contain the country names and flags
            for country, flag in pairs:
                assert (
                    f"{country},{flag}" in output or f'"{country}","{flag}"' in output
                )


# Unicode Edge Cases Tests
@given(
    st.lists(
        st.sampled_from(
            [
                "España",
                "日本",
                "Россия",
                "भारत",
                "中国",
                "مصر",
                "ישראל",
                "한국",
                "Ελλάδα",
                "Việt Nam",
            ]
        ),
        min_size=1,
    )
)
def test_unicode_country_names(country_names):
    """Test that country names with Unicode characters are handled correctly."""
    # Mock the converter to handle these Unicode names
    from unittest.mock import patch

    cf = CountryFlag()

    # We need to patch the convert method to handle our Unicode names
    with patch.object(CountryConverterSingleton, "convert") as mock_convert:
        # Map each Unicode name to a valid ISO2 code
        mock_convert.side_effect = lambda name, to="ISO2": {
            "España": "ES",
            "日本": "JP",
            "Россия": "RU",
            "भारत": "IN",
            "中国": "CN",
            "مصر": "EG",
            "ישראל": "IL",
            "한국": "KR",
            "Ελλάδα": "GR",
            "Việt Nam": "VN",
        }.get(name, "not found")

        flags, pairs = cf.get_flag(country_names)

        # Check that we got the expected number of flags
        assert len(pairs) == len(country_names)

        # Check that each input name is in the output
        for name in country_names:
            assert any(name == pair[0] for pair in pairs)


@given(st.lists(st.text(min_size=1, max_size=50), min_size=1))
def test_input_validation(random_strings):
    """Test that invalid country names are handled gracefully."""
    from unittest.mock import patch

    from countryflag.core.exceptions import InvalidCountryError

    cf = CountryFlag()

    # Patch convert to return "not found" for most inputs
    with patch.object(CountryConverterSingleton, "convert") as mock_convert:
        mock_convert.return_value = "not found"

        # Try to convert the random strings
        try:
            flags, pairs = cf.get_flag(random_strings, fuzzy_matching=True)
            # If we get here, fuzzy matching must have worked for some strings
            # Just check that we got some results
            assert len(pairs) <= len(random_strings)
        except InvalidCountryError:
            # This is also acceptable - it means no matches were found
            pass


@given(country_list_with_mock())
def test_case_insensitivity(data):
    """Test that country name lookup is case-insensitive."""
    country_names, mock_data = data

    from unittest.mock import patch

    from countryflag.core.converters import CountryConverterSingleton

    # Patch the singleton instance
    with patch.object(CountryConverterSingleton, "__new__") as mock_singleton:
        # Create a proper mock converter with the convert method
        class MockConverter:
            def __init__(self):
                self.data = mock_data

            def convert(self, name, to="ISO2"):
                """Mock convert method."""
                name = name.strip().lower()
                for _, row in mock_data.iterrows():
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

        mock_instance = type(
            "MockInstance",
            (),
            {
                "data": mock_data,
                "_converter": MockConverter(),
                "convert": lambda self, name, to="ISO2": MockConverter().convert(
                    name, to
                ),
            },
        )()
        mock_singleton.return_value = mock_instance
        cf = CountryFlag()

        # Convert country names to random case
        mixed_case_names = []
        for name in country_names:
            if len(name) > 0:
                # Randomize the case of the first character
                mixed_case = name[0].swapcase() + name[1:]
                mixed_case_names.append(mixed_case)
            else:
                mixed_case_names.append(name)

        # Get flags for original and mixed case names
        flags_original, pairs_original = cf.get_flag(country_names)
        flags_mixed, pairs_mixed = cf.get_flag(mixed_case_names)

        # The flags should be the same
        assert flags_original == flags_mixed


# Boundary Conditions Tests
@given(st.lists(country_names_strategy, min_size=0, max_size=0))
def test_empty_input_list(empty_list):
    """Test that an empty input list returns an empty result."""
    cf = CountryFlag()
    flags, pairs = cf.get_flag(empty_list)

    assert flags == ""
    assert pairs == []


@given(st.lists(country_names_strategy, min_size=1).map(lambda x: x + [None, "", 123]))
@settings(deadline=None)  # Disable deadline for this test due to variable performance
def test_invalid_items_in_list(country_list_with_invalid_items):
    """Test that invalid items in the list are handled gracefully."""
    cf = CountryFlag()

    # Count valid items (exclude None, numbers, empty strings, and whitespace-only strings)
    valid_items = [
        x
        for x in country_list_with_invalid_items
        if isinstance(x, str) and x.strip() and x != ""
    ]

    # Convert the list - should handle invalid items gracefully
    # Empty strings and other invalid items should be skipped
    flags, pairs = cf.get_flag(country_list_with_invalid_items)
    # Check that we got flags for valid items only
    assert len(pairs) == len(valid_items)


@given(valid_country_lists, st.text(min_size=0, max_size=0))
def test_empty_separator(country_names, empty_separator):
    """Test behavior with an empty separator."""
    cf = CountryFlag()

    # Use an empty separator
    flags, pairs = cf.get_flag(country_names, separator=empty_separator)

    # The flags should be concatenated without separation
    assert len(flags) == sum(len(flag) for _, flag in pairs)


# Cache Consistency Tests
class TestCacheConsistency(RuleBasedStateMachine):
    """
    Test that the cache remains consistent across multiple operations.

    This stateful test simulates a sequence of operations on a cached CountryFlag
    instance and checks that the cache remains consistent.
    """

    countries = Bundle("countries")

    @initialize()
    def setup_cache(self):
        """Initialize test state."""
        self.memory_cache = MemoryCache()
        self.cf = CountryFlag(cache=self.memory_cache)

    @rule(target=countries, country=country_names_strategy)
    def add_country(self, country):
        """Add a country to the bundle."""
        return country

    @rule(countries=st.lists(countries, min_size=1, unique=True))
    def check_cache_consistency(self, countries):
        """Check that cached results are consistent."""
        # Capture cache hits before the calls
        hits_before = self.memory_cache.get_hits()

        # First call (should be a cache miss for new countries)
        flags1, pairs1 = self.cf.get_flag(countries)

        # Second call (should be a cache hit)
        flags2, pairs2 = self.cf.get_flag(countries)

        # Capture cache hits after the calls
        hits_after = self.memory_cache.get_hits()

        # Results should be identical
        assert flags1 == flags2
        assert len(pairs1) == len(pairs2)

        # Verify that the cache hit count increased
        # Since get_hits() returns an int (global count), we verify the count increased
        assert (
            hits_after > hits_before
        ), f"Cache hits should have increased: {hits_before} -> {hits_after}"

    @rule(countries=st.lists(countries, min_size=1, unique=True))
    def check_cache_hit_counts(self, countries):
        """Check that cache hit counts are properly tracked."""
        # Perform operations that should result in cache hits
        self.cf.get_flag(countries)
        self.cf.get_flag(countries)  # Second call should be cache hits

        # Replace previous manual assertion with one that queries the real cache
        assert self.memory_cache.get_hits() > 0


TestCacheStateMachine = TestCacheConsistency.TestCase


# Concurrency Properties Tests
@pytest.mark.parametrize("num_threads", [2, 5, 10])
def test_thread_safety(num_threads):
    """Test that the CountryFlag class is thread-safe."""
    # Create a shared CountryFlag instance
    cf = CountryFlag()

    # Sample country names
    countries = ["United States", "Canada", "Germany", "Japan", "Brazil"]

    # Function to be executed in threads
    def convert_countries():
        flags, pairs = cf.get_flag(countries)
        return len(pairs)

    # Create and start threads
    threads = []
    results = []

    for _ in range(num_threads):
        thread = threading.Thread(target=lambda: results.append(convert_countries()))
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # All threads should have converted the same number of countries
    assert all(result == len(countries) for result in results)


def test_concurrent_cache_access(tmp_path):
    """Test that multiple threads can safely access the cache."""
    # Create a shared cache
    memory_cache = MemoryCache()

    # Function to be executed in threads
    def use_cache(country_list):
        cf = CountryFlag(cache=memory_cache)
        flags, pairs = cf.get_flag(country_list)
        return len(pairs)

    # Create different country lists
    country_lists = [
        ["United States", "Canada", "Germany"],
        ["Japan", "Brazil", "France"],
        ["Italy", "Spain", "United Kingdom"],
        ["Australia", "China", "India"],
    ]

    # Use a thread pool
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        # Submit tasks
        future_to_list = {
            executor.submit(use_cache, country_list): country_list
            for country_list in country_lists
        }

        # Get results
        results = {}
        for future in concurrent.futures.as_completed(future_to_list):
            country_list = future_to_list[future]
            try:
                results[tuple(country_list)] = future.result()
            except Exception as e:
                results[tuple(country_list)] = e

    # Check that all operations succeeded
    for country_list in country_lists:
        assert results[tuple(country_list)] == len(country_list)

    # Check that cache has entries for all countries
    cf = CountryFlag(cache=memory_cache)
    for country_list in country_lists:
        cache_key = f"get_flag_{cf._make_key(country_list, ' ')}"
        assert memory_cache.contains(cache_key)
