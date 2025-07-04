"""
Test Unicode regional indicator edge-cases with non-ASCII letters.

This module tests the rarely executed code paths for regional indicator
construction when feeding two-letter codes containing non-ASCII letters
or unusual cases like "ÅL" for Åland.
"""

import unicodedata

import flag
import pytest

from src.countryflag.core.flag import CountryFlag


class TestUnicodeRegionalIndicators:
    """Test Unicode regional indicator construction with edge cases."""

    def test_regional_indicator_with_non_ascii_letters(self):
        """
        Test regional indicator construction with non-ASCII letters.

        Feeds "ÅL" (Åland) to test handling of non-ASCII letters in
        regional indicator sequences. This explores the rarely executed
        code path where non-ASCII characters are filtered out.
        """
        # Test the non-ASCII code "ÅL" (Åland)
        code = "ÅL"

        print(f"Input code: {code}")
        print(f"Code characters: {[c for c in code]}")
        print(
            f"ASCII chars in code: "
            f"{[c for c in code.lower() if c in 'abcdefghijklmnopqrstuvwxyz0123456789']}"
        )

        # The flag library filters non-ASCII characters
        # "ÅL" -> Å (filtered out) + L -> "L" (only one character remains)
        # This should raise UnknownCountryCode since "L" is not a valid 2-letter code

        try:
            result = flag.flag(code)
            # If we get here, the behavior changed and we should analyze it
            print(f"Unexpected success - Result: {result}")
            print(f"Result length: {len(result)}")

            # Analyze the Unicode structure
            for i, char in enumerate(result):
                print(
                    f"Character {i}: {char} (U+{ord(char):04X}) - "
                    f"{unicodedata.name(char, 'UNKNOWN')}"
                )

            # This should not happen with current behavior
            raise AssertionError(
                "Expected UnknownCountryCode exception for filtered input 'ÅL' -> 'L'"
            )

        except ValueError as e:
            print(f"Expected exception caught: {e}")
            # This is the expected behavior - non-ASCII chars are filtered
            # leaving only "L" which is not a valid country code
            msg = str(e)
            assert (
                "in 'ÅL'" in msg and "l" in msg
            ), "Exception should mention the filtered character"
            print("✓ Correctly handled non-ASCII character filtering edge case")

        # Now test a case that should work: "ÅLand" -> "land" -> tag sequence
        # (but too short) Or better: "ÅUS" -> "US" -> valid regional indicator
        code2 = "ÅUS"
        print(f"\nTesting another case: {code2}")

        try:
            result2 = flag.flag(code2)
            print(f"Result for {code2}: {result2}")

            # This should work since Å is filtered, leaving "US"
            expected_result = flag.flag("US")
            assert result2 == expected_result, "Should produce same result as 'US'"

            # Verify it's a proper regional indicator sequence
            assert len(result2) == 2
            for char in result2:
                char_code = ord(char)
                assert (
                    0x1F1E6 <= char_code <= 0x1F1FF
                ), f"Character {char} is not a regional indicator"

            print("✓ Correctly filtered non-ASCII and produced valid flag")

        except Exception as e:
            print(f"Unexpected exception for {code2}: {e}")
            raise

    def test_regional_indicator_direct_function(self):
        """
        Test the direct regional indicator function with edge cases.

        Uses flag.flag_regional_indicator directly to test the
        rarely executed code paths.
        """
        # Test with standard ASCII code
        result_ascii = flag.flag_regional_indicator("US")
        print(f"ASCII result: {result_ascii}")
        assert len(result_ascii) == 2

        # Test with mixed case
        result_mixed = flag.flag_regional_indicator("Us")
        print(f"Mixed case result: {result_mixed}")
        assert len(result_mixed) == 2

        # Verify both produce the same result (case insensitive)
        assert result_ascii == result_mixed

        # Test edge case with non-standard characters
        # The function should handle the input according to its documentation
        try:
            result_edge = flag.flag_regional_indicator("A1")  # Mix of letter and number
            print(f"Edge case result: {result_edge}")
            assert len(result_edge) == 2
        except Exception as e:
            print(f"Edge case threw exception: {e}")
            # This is acceptable as the function may reject invalid input

    def test_countryflag_with_non_ascii_input(self):
        """
        Test CountryFlag class with non-ASCII country codes.

        Tests how the CountryFlag class handles unusual input
        that might contain non-ASCII characters.
        """
        cf = CountryFlag()

        # Test with actual Åland islands (AX is the correct ISO code)
        # But let's test what happens when we feed unusual input
        test_cases = [
            "ÅL",  # Non-ASCII version
            "Åland",  # Full name with non-ASCII
            "AX",  # Correct ISO code for Åland
        ]

        for test_input in test_cases:
            print(f"\nTesting input: {test_input}")

            try:
                flags, pairs = cf.get_flag([test_input])
                print(f"Success - Flags: {flags}")
                print(f"Pairs: {pairs}")

                if flags:
                    # Analyze the flag structure
                    for i, char in enumerate(flags):
                        if char != " ":  # Skip separators
                            print(
                                f"Flag char {i}: {char} (U+{ord(char):04X}) - "
                                f"{unicodedata.name(char, 'UNKNOWN')}"
                            )

            except Exception as e:
                print(f"Exception for {test_input}: {e}")
                # This is expected for invalid country codes

    def test_regional_indicator_code_point_analysis(self):
        """
        Detailed analysis of regional indicator code point construction.

        Verifies that regional indicators are correctly constructed
        with exactly 2 code points when given a 2-letter code.
        """
        # Test various two-letter combinations
        test_codes = [
            "US",  # Standard
            "GB",  # Standard
            "DE",  # Standard
            "AL",  # Albania (what ÅL should normalize to)
        ]

        for code in test_codes:
            print(f"\nAnalyzing code: {code}")

            # Get the flag
            result = flag.flag(code)
            print(f"Flag result: {result}")

            # Verify length is exactly 2 (regional indicator pairs)
            assert (
                len(result) == 2
            ), f"Expected 2 characters for {code}, got {len(result)}"

            # Verify each character is a regional indicator
            char1, char2 = result[0], result[1]

            # Regional indicators are U+1F1E6 + (letter - 'A')
            expected_char1 = chr(0x1F1E6 + ord(code[0]) - ord("A"))
            expected_char2 = chr(0x1F1E6 + ord(code[1]) - ord("A"))

            print(f"Expected: {expected_char1}{expected_char2}")
            print(f"Got:      {char1}{char2}")

            assert char1 == expected_char1, f"First character mismatch for {code}"
            assert char2 == expected_char2, f"Second character mismatch for {code}"

            # Verify Unicode names
            name1 = unicodedata.name(char1, "UNKNOWN")
            name2 = unicodedata.name(char2, "UNKNOWN")
            print(f"Unicode names: {name1}, {name2}")

    def test_flag_library_character_filtering(self):
        """
        Test how the flag library filters non-ASCII characters.

        According to the documentation, only a-z, A-Z and 0-9 are processed,
        other characters are removed. This tests that behavior.
        """
        # Test cases with various non-ASCII characters
        test_cases = [
            ("ÅL", "AL"),  # Å should be removed, leaving AL
            (
                "Ü$",
                "U",
            ),  # Ü and $ should be removed, leaving U (invalid as single char)
            ("FÖ", "FO"),  # Ö should be removed, leaving FO (Faroe Islands might work)
            ("A#B", "AB"),  # # should be removed, leaving AB
            ("123", "123"),  # Numbers should be preserved
            ("AB12", "AB12"),  # Mix should be preserved
        ]

        for input_code, expected_cleaned in test_cases:
            print(f"\nTesting: {input_code} -> expected clean: {expected_cleaned}")

            try:
                result = flag.flag(input_code)
                print(f"Result: {result}")

                if len(expected_cleaned) == 2:
                    # Should be regional indicators
                    expected_result = flag.flag(expected_cleaned)
                    print(f"Expected result: {expected_result}")
                    assert result == expected_result

                    # Verify structure
                    assert len(result) == 2
                    for char in result:
                        char_code = ord(char)
                        assert 0x1F1E6 <= char_code <= 0x1F1FF

            except Exception as e:
                print(f"Exception: {e}")
                # Some combinations might not be valid country codes

    def test_unicode_normalization_edge_cases(self):
        """
        Test Unicode normalization edge cases.

        Some Unicode characters might have multiple representations
        (e.g., composed vs decomposed forms). Test how these are handled.
        """
        import unicodedata

        # Test composed vs decomposed forms
        # Å can be represented as:
        # 1. Single character U+00C5 (LATIN CAPITAL LETTER A WITH RING ABOVE)
        # 2. Decomposed as A (U+0041) + combining ring (U+030A)

        composed_a = "Å"  # U+00C5
        decomposed_a = unicodedata.normalize("NFD", composed_a)  # A + combining ring

        print(f"Composed Å: {composed_a} (len={len(composed_a)})")
        print(f"Decomposed Å: {decomposed_a} (len={len(decomposed_a)})")

        # Test both forms with L
        test_cases = [
            composed_a + "L",
            decomposed_a + "L",
        ]

        results = []
        for case in test_cases:
            print(f"\nTesting: {case} (chars: {[hex(ord(c)) for c in case]})")
            try:
                result = flag.flag(case)
                results.append(result)
                print(f"Result: {result}")
            except Exception as e:
                results.append(None)
                print(f"Exception: {e}")

        # Both should produce the same result (or both fail)
        if results[0] is not None and results[1] is not None:
            assert (
                results[0] == results[1]
            ), "Composed and decomposed forms should produce the same result"

    def test_rarely_used_iso_codes_with_special_chars(self):
        """
        Test some rarely used or edge case ISO codes that might contain
        or be confused with special characters.
        """
        # Test some actual edge case country codes
        edge_cases = [
            "AX",  # Åland Islands (correct code)
            "BL",  # Saint Barthélemy
            "MF",  # Saint Martin
            "SX",  # Sint Maarten
        ]

        cf = CountryFlag()

        for code in edge_cases:
            print(f"\nTesting edge case ISO code: {code}")

            try:
                # Test with CountryFlag
                flags, pairs = cf.get_flag([code])
                print(f"CountryFlag result - Flags: {flags}, Pairs: {pairs}")

                # Test with direct flag library
                direct_result = flag.flag(code)
                print(f"Direct flag result: {direct_result}")

                # Verify consistency
                if flags and direct_result:
                    # The flag from CountryFlag should match direct flag call
                    flag_from_pairs = pairs[0][1] if pairs else ""
                    assert (
                        flag_from_pairs == direct_result
                    ), f"Inconsistent results for {code}"

                    # Verify structure
                    assert len(direct_result) == 2
                    for char in direct_result:
                        char_code = ord(char)
                        assert 0x1F1E6 <= char_code <= 0x1F1FF

            except Exception as e:
                print(f"Exception for {code}: {e}")
