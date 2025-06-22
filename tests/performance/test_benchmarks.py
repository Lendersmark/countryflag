"""
Performance benchmarks for the countryflag package.

This module contains benchmarks for measuring the performance of
various operations in the countryflag package.
"""

import random
import string
import time
from typing import Any, Dict, List, Tuple

import pytest

from countryflag.cache.disk import DiskCache
from countryflag.cache.memory import MemoryCache
from countryflag.core.converters import CountryConverterSingleton
from countryflag.core.flag import CountryFlag
from countryflag.utils.io import process_file_input, process_multiple_files

# Sample data for benchmarks
SAMPLE_COUNTRIES_SMALL = ["United States", "Canada", "Germany", "Japan", "Brazil"]
SAMPLE_COUNTRIES_MEDIUM = [
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
    "Netherlands",
    "Belgium",
    "Sweden",
    "Norway",
    "Denmark",
    "Finland",
    "Poland",
    "Switzerland",
    "Austria",
    "Greece",
]

# Generate a large list of country names by repeating the medium list
SAMPLE_COUNTRIES_LARGE = SAMPLE_COUNTRIES_MEDIUM * 10  # 250 countries


def generate_random_string(length: int) -> str:
    """Generate a random string of fixed length."""
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for _ in range(length))


def create_temp_file_with_countries(tmp_path, countries: List[str]) -> str:
    """Create a temporary file with country names, one per line."""
    temp_file = tmp_path / "countries.txt"
    with open(temp_file, "w") as f:
        for country in countries:
            f.write(f"{country}\n")
    return str(temp_file)


class TestConversionBenchmarks:
    """Benchmarks for country name to flag conversion."""

    @pytest.mark.benchmark(group="conversion")
    def test_convert_small_list(self, benchmark):
        """Benchmark conversion of a small list of country names to flags."""
        cf = CountryFlag()

        def convert():
            flags, _ = cf.get_flag(SAMPLE_COUNTRIES_SMALL)
            return flags

        result = benchmark(convert)
        assert len(result.split(" ")) == len(SAMPLE_COUNTRIES_SMALL)

    @pytest.mark.benchmark(group="conversion")
    def test_convert_medium_list(self, benchmark):
        """Benchmark conversion of a medium list of country names to flags."""
        cf = CountryFlag()

        def convert():
            flags, _ = cf.get_flag(SAMPLE_COUNTRIES_MEDIUM)
            return flags

        result = benchmark(convert)
        assert len(result.split(" ")) == len(SAMPLE_COUNTRIES_MEDIUM)

    @pytest.mark.benchmark(group="conversion")
    def test_convert_large_list(self, benchmark):
        """Benchmark conversion of a large list of country names to flags."""
        cf = CountryFlag()

        def convert():
            flags, _ = cf.get_flag(SAMPLE_COUNTRIES_LARGE)
            return flags

        result = benchmark(convert)
        assert len(result.split(" ")) == len(SAMPLE_COUNTRIES_LARGE)


class TestReverseLookupBenchmarks:
    """Benchmarks for emoji flag to country name reverse lookup."""

    @pytest.fixture
    def sample_flags(self) -> Tuple[List[str], List[str], List[str]]:
        """Generate sample flag lists for benchmarking."""
        cf = CountryFlag()
        small_flags, _ = cf.get_flag(SAMPLE_COUNTRIES_SMALL)
        medium_flags, _ = cf.get_flag(SAMPLE_COUNTRIES_MEDIUM)
        large_flags, _ = cf.get_flag(SAMPLE_COUNTRIES_LARGE)
        return (small_flags.split(" "), medium_flags.split(" "), large_flags.split(" "))

    @pytest.mark.benchmark(group="reverse_lookup")
    def test_reverse_lookup_small(self, benchmark, sample_flags):
        """Benchmark reverse lookup for a small list of flags."""
        cf = CountryFlag()
        small_flags, _, _ = sample_flags

        def reverse_lookup():
            return cf.reverse_lookup(small_flags)

        result = benchmark(reverse_lookup)
        assert len(result) == len(small_flags)

    @pytest.mark.benchmark(group="reverse_lookup")
    def test_reverse_lookup_medium(self, benchmark, sample_flags):
        """Benchmark reverse lookup for a medium list of flags."""
        cf = CountryFlag()
        _, medium_flags, _ = sample_flags

        def reverse_lookup():
            return cf.reverse_lookup(medium_flags)

        result = benchmark(reverse_lookup)
        assert len(result) == len(medium_flags)

    @pytest.mark.benchmark(group="reverse_lookup")
    def test_reverse_lookup_large(self, benchmark, sample_flags):
        """Benchmark reverse lookup for a large list of flags."""
        cf = CountryFlag()
        _, _, large_flags = sample_flags

        def reverse_lookup():
            return cf.reverse_lookup(large_flags)

        result = benchmark(reverse_lookup)
        assert len(result) == len(large_flags)


class TestCacheBenchmarks:
    """Benchmarks for caching performance."""

    @pytest.mark.benchmark(group="cache")
    def test_no_cache_performance(self, benchmark):
        """Benchmark conversion without caching."""
        cf = CountryFlag()  # No cache

        def convert():
            flags, _ = cf.get_flag(SAMPLE_COUNTRIES_MEDIUM)
            return flags

        result = benchmark(convert)
        assert len(result.split(" ")) == len(SAMPLE_COUNTRIES_MEDIUM)

    @pytest.mark.benchmark(group="cache")
    def test_memory_cache_performance(self, benchmark):
        """Benchmark conversion with memory caching."""
        memory_cache = MemoryCache()
        cf = CountryFlag(cache=memory_cache)

        # Warm up the cache
        cf.get_flag(SAMPLE_COUNTRIES_MEDIUM)

        def convert():
            flags, _ = cf.get_flag(SAMPLE_COUNTRIES_MEDIUM)
            return flags

        result = benchmark(convert)
        assert len(result.split(" ")) == len(SAMPLE_COUNTRIES_MEDIUM)

    @pytest.mark.benchmark(group="cache")
    def test_disk_cache_performance(self, benchmark, tmp_path):
        """Benchmark conversion with disk caching."""
        disk_cache = DiskCache(str(tmp_path / "cache"))
        cf = CountryFlag(cache=disk_cache)

        # Warm up the cache
        cf.get_flag(SAMPLE_COUNTRIES_MEDIUM)

        def convert():
            flags, _ = cf.get_flag(SAMPLE_COUNTRIES_MEDIUM)
            return flags

        result = benchmark(convert)
        assert len(result.split(" ")) == len(SAMPLE_COUNTRIES_MEDIUM)


class TestBatchProcessingBenchmarks:
    """Benchmarks for batch processing."""

    @pytest.mark.benchmark(group="batch_processing")
    def test_single_file_processing(self, benchmark, tmp_path):
        """Benchmark processing of a single file."""
        file_path = create_temp_file_with_countries(tmp_path, SAMPLE_COUNTRIES_MEDIUM)

        def process_file():
            return process_file_input(file_path)

        result = benchmark(process_file)
        assert len(result) == len(SAMPLE_COUNTRIES_MEDIUM)

    @pytest.mark.benchmark(group="batch_processing")
    def test_multiple_files_processing(self, benchmark, tmp_path):
        """Benchmark processing of multiple files."""
        # Create 5 files with the same content
        file_paths = []
        for i in range(5):
            file_path = create_temp_file_with_countries(
                tmp_path, SAMPLE_COUNTRIES_SMALL
            )
            file_paths.append(file_path)

        def process_files():
            return process_multiple_files(file_paths)

        result = benchmark(process_files)
        assert len(result) == len(SAMPLE_COUNTRIES_SMALL) * 5

    @pytest.mark.benchmark(group="batch_processing")
    def test_multiple_files_parallel_processing(self, benchmark, tmp_path):
        """Benchmark parallel processing of multiple files."""
        # Create 10 files with the same content
        file_paths = []
        for i in range(10):
            file_path = create_temp_file_with_countries(
                tmp_path, SAMPLE_COUNTRIES_SMALL
            )
            file_paths.append(file_path)

        def process_files_parallel():
            return process_multiple_files(file_paths, max_workers=4)

        result = benchmark(process_files_parallel)
        assert len(result) == len(SAMPLE_COUNTRIES_SMALL) * 10


class TestFormatOutputBenchmarks:
    """Benchmarks for output formatting."""

    @pytest.fixture
    def sample_pairs(self) -> List[Tuple[str, str]]:
        """Generate sample country-flag pairs for benchmarking."""
        cf = CountryFlag()
        _, pairs = cf.get_flag(SAMPLE_COUNTRIES_MEDIUM)
        return pairs

    @pytest.mark.benchmark(group="format_output")
    def test_format_text_output(self, benchmark, sample_pairs):
        """Benchmark text output formatting."""
        cf = CountryFlag()

        def format_text():
            return cf.format_output(sample_pairs, output_format="text")

        result = benchmark(format_text)
        assert len(result.split(" ")) == len(sample_pairs)

    @pytest.mark.benchmark(group="format_output")
    def test_format_json_output(self, benchmark, sample_pairs):
        """Benchmark JSON output formatting."""
        cf = CountryFlag()

        def format_json():
            return cf.format_output(sample_pairs, output_format="json")

        result = benchmark(format_json)
        assert "country" in result
        assert "flag" in result

    @pytest.mark.benchmark(group="format_output")
    def test_format_csv_output(self, benchmark, sample_pairs):
        """Benchmark CSV output formatting."""
        cf = CountryFlag()

        def format_csv():
            return cf.format_output(sample_pairs, output_format="csv")

        result = benchmark(format_csv)
        assert "Country,Flag" in result


class TestFuzzyMatchingBenchmarks:
    """Benchmarks for fuzzy matching."""

    @pytest.mark.benchmark(group="fuzzy_matching")
    def test_find_close_matches_performance(self, benchmark):
        """Benchmark finding close matches for country names."""
        converter = CountryConverterSingleton()

        def find_matches():
            return converter.find_close_matches("Germny")

        result = benchmark(find_matches)
        assert len(result) > 0
        assert "Germany" in [match[0] for match in result]

    @pytest.mark.benchmark(group="fuzzy_matching")
    def test_get_flag_with_fuzzy_matching(self, benchmark):
        """Benchmark conversion with fuzzy matching enabled."""
        cf = CountryFlag()
        misspelled_countries = ["Germny", "Unted States", "Japen", "Brazl", "Canade"]

        def convert_with_fuzzy():
            flags, _ = cf.get_flag(misspelled_countries, fuzzy_matching=True)
            return flags

        result = benchmark(convert_with_fuzzy)
        assert len(result.split(" ")) == len(misspelled_countries)
