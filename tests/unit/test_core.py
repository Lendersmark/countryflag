"""Unit tests for the core functionality."""

import pytest
from countryflag.core import CountryFlag
from countryflag.core.exceptions import InvalidCountryError


def test_basic_flag_conversion():
    """Test basic conversion of country names to flags."""
    cf = CountryFlag()
    flags, pairs = cf.get_flag(["Germany", "France", "Italy"])
    assert len(pairs) == 3
    assert all(flag for _, flag in pairs)


def test_iso_code_conversion():
    """Test conversion using ISO codes."""
    cf = CountryFlag()
    flags, pairs = cf.get_flag(["DE", "FR", "IT"])
    assert len(pairs) == 3
    assert all(flag for _, flag in pairs)


def test_invalid_country():
    """Test handling of invalid country names."""
    cf = CountryFlag()
    with pytest.raises(InvalidCountryError):
        cf.get_flag(["InvalidCountry"])


def test_empty_input():
    """Test handling of empty input."""
    cf = CountryFlag()
    flags, pairs = cf.get_flag([])
    assert flags == ""
    assert pairs == []


def test_mixed_formats():
    """Test handling of mixed format inputs."""
    cf = CountryFlag()
    flags, pairs = cf.get_flag(["Germany", "FR", "Italy"])
    assert len(pairs) == 3
    assert all(flag for _, flag in pairs)


def test_fuzzy_matching():
    """Test fuzzy matching functionality."""
    cf = CountryFlag()
    flags, pairs = cf.get_flag(["Germny", "Frnce"], fuzzy_matching=True)
    assert len(pairs) == 2
    assert all(flag for _, flag in pairs)


def test_custom_separator():
    """Test custom separator in output."""
    cf = CountryFlag()
    flags, _ = cf.get_flag(["Germany", "France"], separator="|")
    assert "|" in flags


def test_format_output_json():
    """Test JSON output format."""
    cf = CountryFlag()
    _, pairs = cf.get_flag(["Germany", "France"])
    output = cf.format_output(pairs, output_format="json")
    assert '"country"' in output
    assert '"flag"' in output


def test_format_output_csv():
    """Test CSV output format."""
    cf = CountryFlag()
    _, pairs = cf.get_flag(["Germany", "France"])
    output = cf.format_output(pairs, output_format="csv")
    assert "Country,Flag" in output


def test_reverse_lookup():
    """Test reverse lookup from flag to country name."""
    cf = CountryFlag()
    _, pairs = cf.get_flag(["Germany", "France"])
    flags = [flag for _, flag in pairs]
    result = cf.reverse_lookup(flags)
    assert len(result) == 2
    assert all(country for _, country in result)
