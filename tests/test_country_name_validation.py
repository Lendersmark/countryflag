"""Validation of whole country names and legacy lists of country codes."""

import subprocess
import sys

import pytest

from countryflag import CountryFlag
from countryflag.cache.memory import MemoryCache


@pytest.mark.parametrize(
    "name",
    [
        "United States",
        "United Kingdom",
        "New Zealand",
        "South Africa",
        "Costa Rica",
        "US Virgin Islands",
        "UK Virgin Islands",
        "St Vincent and the Grenadines",
        "Lao PDR",
    ],
)
def test_validate_multiword_country_name(name: str) -> None:
    """Validate names accepted by flag conversion, including a cache hit."""
    country_flag = CountryFlag(cache=MemoryCache())
    assert country_flag.get_flag([name])[0]
    assert country_flag.validate_country_name(name)
    assert country_flag.validate_country_name(name)


@pytest.mark.parametrize("name", ["France", "US", "GB", "US GB"])
def test_validate_existing_names_and_code_lists(name: str) -> None:
    """Keep support for single countries and space-separated codes."""
    assert CountryFlag(cache=MemoryCache()).validate_country_name(name)


@pytest.mark.parametrize(
    "name",
    [
        "",
        " ",
        "Not a Country",
        "US InvalidCode",
    ],
)
def test_validate_invalid_country_name(name: str) -> None:
    """Reject inputs that cannot be resolved as countries or code lists."""
    assert not CountryFlag(cache=MemoryCache()).validate_country_name(name)


def test_cli_validate_multiword_country_name() -> None:
    """Report multi-word names as valid through the public CLI."""
    result = subprocess.run(
        [sys.executable, "-m", "countryflag", "--validate", "United States"],
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
    )
    assert result.returncode == 0
    assert "'United States' is a valid country name" in result.stdout
