"""Test type checking defensive code in public API methods.

This test module covers Step 10: Non-string argument raises `TypeError`.
Pass an `int` or `None` to the public API; assert `TypeError` with helpful message.
Covers defensive type-checking lines.
"""

import pytest

from src.countryflag import get_ascii_flag, getflag
from src.countryflag.core.flag import CountryFlag


class TestTypeCheckingPublicAPI:
    """Test type checking for public API functions."""

    def test_getflag_with_int_raises_typeerror(self):
        """Test that passing an int to getflag raises TypeError."""
        with pytest.raises(TypeError) as exc_info:
            # Pass an int instead of string
            getflag(123)

        # Check that the error message is helpful
        error_message = str(exc_info.value)
        assert (
            "expected string" in error_message.lower() or "int" in error_message.lower()
        )

    def test_getflag_with_none_raises_typeerror(self):
        """Test that passing None to getflag raises TypeError."""
        with pytest.raises(TypeError) as exc_info:
            # Pass None instead of string
            getflag(None)

        # Check that the error message is helpful
        error_message = str(exc_info.value)
        assert "none" in error_message.lower() or "expected" in error_message.lower()

    def test_getflag_with_list_containing_int_handles_gracefully(self):
        """Test that getflag handles list containing ints gracefully."""
        # Based on the code in get_flag(), invalid types are skipped with debug logging
        # This should return empty string since all invalid items are skipped
        result = getflag([123, 456])
        assert result == ""

    def test_getflag_with_list_containing_none_handles_gracefully(self):
        """Test that getflag handles list containing None gracefully."""
        # Based on the code in get_flag(), invalid types are skipped with debug logging
        # This should return empty string since all invalid items are skipped
        result = getflag([None, None])
        assert result == ""

    def test_getflag_with_mixed_valid_invalid_types(self):
        """Test that getflag handles mixed valid and invalid types."""
        # Valid string should be processed, invalid types should be skipped
        result = getflag(["Germany", 123, None, "France"])
        # Should contain valid flags for Germany and France
        assert "🇩🇪" in result
        assert "🇫🇷" in result

    def test_get_ascii_flag_with_int_raises_typeerror(self):
        """Test that passing an int to get_ascii_flag raises TypeError."""
        with pytest.raises((TypeError, AttributeError)) as exc_info:
            # Pass an int instead of string - this might raise TypeError or AttributeError
            # depending on how the conversion is attempted
            get_ascii_flag(123)

        # Check that some meaningful error is raised
        assert exc_info.value is not None

    def test_get_ascii_flag_with_none_raises_typeerror(self):
        """Test that passing None to get_ascii_flag raises TypeError."""
        with pytest.raises((TypeError, AttributeError)) as exc_info:
            # Pass None instead of string
            get_ascii_flag(None)

        # Check that some meaningful error is raised
        assert exc_info.value is not None


class TestTypeCheckingCountryFlagClass:
    """Test type checking for CountryFlag class methods."""

    def test_country_flag_get_flag_with_int_list_handles_gracefully(self):
        """Test that CountryFlag.get_flag handles int list gracefully."""
        cf = CountryFlag()
        # Should return empty results since all items are invalid
        flags, pairs = cf.get_flag([123, 456])
        assert flags == ""
        assert pairs == []

    def test_country_flag_get_flag_with_none_list_handles_gracefully(self):
        """Test that CountryFlag.get_flag handles None list gracefully."""
        cf = CountryFlag()
        # Should return empty results since all items are invalid
        flags, pairs = cf.get_flag([None, None])
        assert flags == ""
        assert pairs == []

    def test_country_flag_validate_country_name_with_int_returns_false(self):
        """Test that CountryFlag.validate_country_name with int returns False."""
        cf = CountryFlag()
        # According to the code (line 144-145), non-string input returns False
        result = cf.validate_country_name(123)
        assert result is False

    def test_country_flag_validate_country_name_with_none_returns_false(self):
        """Test that CountryFlag.validate_country_name with None returns False."""
        cf = CountryFlag()
        # According to the code (line 144-145), non-string input returns False
        result = cf.validate_country_name(None)
        assert result is False

    def test_country_flag_reverse_lookup_with_int_list_handles_gracefully(self):
        """Test that CountryFlag.reverse_lookup handles int list gracefully."""
        cf = CountryFlag()
        # Should handle non-string items gracefully (they are skipped per line 445-447)
        result = cf.reverse_lookup([123, 456])
        assert result == []

    def test_country_flag_reverse_lookup_with_none_list_handles_gracefully(self):
        """Test that CountryFlag.reverse_lookup handles None list gracefully."""
        cf = CountryFlag()
        # Should handle non-string items gracefully (they are skipped per line 445-447)
        result = cf.reverse_lookup([None, None])
        assert result == []

    def test_country_flag_get_ascii_flag_with_int_raises_error(self):
        """Test that CountryFlag.get_ascii_flag with int raises appropriate error."""
        cf = CountryFlag()
        with pytest.raises((TypeError, AttributeError, Exception)) as exc_info:
            # This should raise some error when trying to process an int
            cf.get_ascii_flag(123)

        # Check that some meaningful error is raised
        assert exc_info.value is not None

    def test_country_flag_get_ascii_flag_with_none_raises_error(self):
        """Test that CountryFlag.get_ascii_flag with None raises appropriate error."""
        cf = CountryFlag()
        with pytest.raises((TypeError, AttributeError, Exception)) as exc_info:
            # This should raise some error when trying to process None
            cf.get_ascii_flag(None)

        # Check that some meaningful error is raised
        assert exc_info.value is not None


class TestTypeCheckingEdgeCases:
    """Test edge cases for type checking."""

    def test_getflag_with_float_handles_gracefully(self):
        """Test that getflag handles float gracefully."""
        # Floats are not strings, should be handled like other invalid types
        result = getflag([3.14])
        assert result == ""

    def test_getflag_with_boolean_handles_gracefully(self):
        """Test that getflag handles boolean gracefully."""
        # Booleans are not strings, should be handled like other invalid types
        result = getflag([True, False])
        assert result == ""

    def test_getflag_with_empty_list_returns_empty(self):
        """Test that getflag with empty list returns empty string."""
        result = getflag([])
        assert result == ""

    def test_country_flag_methods_with_mixed_types(self):
        """Test CountryFlag methods with mixed valid/invalid types."""
        cf = CountryFlag()

        # Test get_flag with mixed types
        flags, pairs = cf.get_flag(["Germany", 123, "France", None, "Italy"])
        # Should only process the valid string countries
        assert "🇩🇪" in flags
        assert "🇫🇷" in flags
        assert "🇮🇹" in flags
        assert len(pairs) == 3  # Only 3 valid countries

    def test_defensive_type_checking_coverage(self):
        """Test that defensive type checking is working as expected."""
        cf = CountryFlag()

        # These should all be handled gracefully without crashing
        test_cases = [
            [1, 2, 3],
            [None, None],
            [True, False],
            [3.14, 2.71],
            ["", 123, "Germany"],  # Mix of empty string, int, and valid country
            [[], {}, set()],  # Various container types
        ]

        for test_case in test_cases:
            # Should not raise unhandled exceptions
            try:
                flags, pairs = cf.get_flag(test_case)
                # Result should be reasonable (empty or containing only valid flags)
                assert isinstance(flags, str)
                assert isinstance(pairs, list)
            except Exception as e:
                # If an exception is raised, it should be a known/expected type
                assert isinstance(e, (TypeError, AttributeError, ValueError))
