"""Unit tests for memory cache functionality."""

from countryflag.core import CountryFlag


def test_cache_hits_regression():
    """Test that cache hits are properly incremented for deterministic cache behavior.

    This is a regression test that ensures cache hits work correctly when the same
    set of countries is requested in different orders. This guards against future
    regressions without relying on Hypothesis state machines.
    """
    cf = CountryFlag()
    countries = ["Canada", "Brazil"]
    cf.get_flag(countries)
    before = cf._cache.hits
    cf.get_flag(list(reversed(countries)))
    assert cf._cache.hits == before + 1
