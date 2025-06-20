"""
Property-based tests for the countryflag package.

This module contains property-based tests that use hypothesis to test
the properties of the countryflag package.
"""

import pytest
import threading
import concurrent.futures
from hypothesis import given, strategies as st, settings, assume, example
from hypothesis.stateful import RuleBasedStateMachine, Bundle, rule

from countryflag.core.flag import CountryFlag
from countryflag.core.converters import CountryConverterSingleton
from countryflag.core.models import CountryInfo
from countryflag.cache.memory import MemoryCache
from countryflag.cache.disk import DiskCache


# Define common strategies
country_names_strategy = st.sampled_from([
    "United States", "Canada", "Germany", "Japan", "Brazil",
    "France", "Italy", "Spain", "United Kingdom", "Australia",
    "China", "India", "Russia", "Mexico", "South Korea"
])

# Strategy for valid country lists
valid_country_lists = st.lists(country_names_strategy, min_size=1)

# Strategy for separators
separator_strategy = st.text(min_size=1, max_size=5)

# Strategy for output formats
output_format_strategy = st.sampled_from(["text", "json", "csv"])


@given(valid_country_lists)
def test_getflag_length(country_names, mock_country_converter):
    """Test that the number of flags returned matches the number of country names."""
    cf = CountryFlag()
    flags, pairs = cf.get_flag(country_names)
    
    # Split the flags by the separator (space)
    flag_list = flags.split(" ")
    
    # Check that we have the same number of flags as country names
    assert len(flag_list) == len(country_names)
    assert len(pairs) == len(country_names)


@given(valid_country_lists, separator_strategy)
def test_getflag_separator(country_names, separator, mock_country_converter):
    """Test that the separator is used correctly."""
    cf = CountryFlag()
    flags, pairs = cf.get_flag(country_names, separator=separator)
    
    # Split the flags by the separator
    flag_list = flags.split(separator)
    
    # Check that we have the same number of flags as country names
    assert len(flag_list) == len(country_names)


@given(valid_country_lists)
def test_reverse_lookup_round_trip(country_names, mock_country_converter):
    """Test that converting from country names to flags and back returns the original country names."""
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
def test_get_flags_by_region(region, mock_country_converter):
    """Test that get_flags_by_region returns flags for countries in the region."""
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


@given(valid_country_lists, output_format_strategy)
def test_format_output(country_names, output_format, mock_country_converter):
    """Test that format_output returns output in the specified format."""
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
            assert f"{country},{flag}" in output or f'"{country}","{flag}"' in output


# Unicode Edge Cases Tests
@given(st.lists(
    st.sampled_from([
        "España", "日本", "Россия", "भारत", "中国",
        "مصر", "ישראל", "한국", "Ελλάδα", "Việt Nam"
    ]),
    min_size=1
))
def test_unicode_country_names(country_names, mock_country_converter):
    """Test that country names with Unicode characters are handled correctly."""
    # Mock the converter to handle these Unicode names
    from unittest.mock import patch
    
    cf = CountryFlag()
    
    # We need to patch the convert method to handle our Unicode names
    with patch.object(CountryConverterSingleton, 'convert') as mock_convert:
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
            "Việt Nam": "VN"
        }.get(name, "not found")
        
        flags, pairs = cf.get_flag(country_names)
        
        # Check that we got the expected number of flags
        assert len(pairs) == len(country_names)
        
        # Check that each input name is in the output
        for name in country_names:
            assert any(name == pair[0] for pair in pairs)


@given(st.lists(
    st.text(min_size=1, max_size=50),
    min_size=1
))
def test_input_validation(random_strings, mock_country_converter):
    """Test that invalid country names are handled gracefully."""
    from unittest.mock import patch
    from countryflag.core.exceptions import InvalidCountryError
    
    cf = CountryFlag()
    
    # Patch convert to return "not found" for most inputs
    with patch.object(CountryConverterSingleton, 'convert') as mock_convert:
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


@given(valid_country_lists)
def test_case_insensitivity(country_names, mock_country_converter):
    """Test that country name lookup is case-insensitive."""
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
def test_empty_input_list(empty_list, mock_country_converter):
    """Test that an empty input list returns an empty result."""
    cf = CountryFlag()
    flags, pairs = cf.get_flag(empty_list)
    
    assert flags == ""
    assert pairs == []


@given(st.lists(country_names_strategy, min_size=1).map(lambda x: x + [None, "", 123]))
def test_invalid_items_in_list(country_list_with_invalid_items, mock_country_converter):
    """Test that invalid items in the list are handled gracefully."""
    cf = CountryFlag()
    
    # Count valid items
    valid_items = [x for x in country_list_with_invalid_items if isinstance(x, str) and x]
    
    # Convert the list
    flags, pairs = cf.get_flag(country_list_with_invalid_items)
    
    # Check that we got flags for valid items only
    assert len(pairs) == len(valid_items)


@given(valid_country_lists, st.text(min_size=0, max_size=0))
def test_empty_separator(country_names, empty_separator, mock_country_converter):
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
    
    def __init__(self):
        super().__init__()
        self.memory_cache = MemoryCache()
        self.cf = CountryFlag(cache=self.memory_cache)
        self.cache_hits = {}
    
    @rule(target=countries, country=country_names_strategy)
    def add_country(self, country):
        """Add a country to the bundle."""
        return country
    
    @rule(countries=st.lists(countries, min_size=1, unique=True))
    def check_cache_consistency(self, countries):
        """Check that cached results are consistent."""
        # First call (should be a cache miss for new countries)
        flags1, pairs1 = self.cf.get_flag(countries)
        
        # Record cache hits
        for country in countries:
            if country not in self.cache_hits:
                self.cache_hits[country] = 0
        
        # Second call (should be a cache hit)
        flags2, pairs2 = self.cf.get_flag(countries)
        
        # Results should be identical
        assert flags1 == flags2
        assert len(pairs1) == len(pairs2)
        
        # Update cache hit count
        for country in countries:
            self.cache_hits[country] += 1
    
    @rule()
    def check_cache_hit_counts(self):
        """Check that cache hits are being recorded."""
        # After several operations, some countries should have multiple cache hits
        assert any(count > 0 for count in self.cache_hits.values())


TestCacheStateMachine = TestCacheConsistency.TestCase


# Concurrency Properties Tests
@pytest.mark.parametrize("num_threads", [2, 5, 10])
def test_thread_safety(num_threads, mock_country_converter):
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


def test_concurrent_cache_access(mock_country_converter, tmp_path):
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
        future_to_list = {executor.submit(use_cache, country_list): country_list 
                        for country_list in country_lists}
        
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
    for country_list in country_lists:
        cache_key = f"get_flag_{','.join(country_list)}_{' '}"
        assert memory_cache.contains(cache_key)
