#!/usr/bin/env python3
"""
Step 9: Alias and case-insensitivity handling validation test

This script validates that inputs `uk`, `UK`, and `Gb` all map to the same result
as the canonical `"GB"`. It validates the normalisation logic (upper-case, alias table).
"""

import sys

sys.path.insert(0, "src")

from countryflag import CountryFlag


def test_alias_and_case_normalization():
    """
    Test that various forms of UK/GB country codes all map to the same result.

    Validates:
    - Case insensitivity (uk, UK, Uk, etc.)
    - Alias handling (UK → GB mapping)
    - Consistent results across all variants
    """
    print("=" * 60)
    print("Step 9: Alias and Case-Insensitivity Validation")
    print("=" * 60)

    cf = CountryFlag()

    # Test inputs as specified in the task
    test_inputs = ["uk", "UK", "Gb", "GB"]

    print(f"Testing inputs: {test_inputs}")
    print()

    results = []
    canonical_flag = None
    canonical_country = None

    # Test each input
    for i, country_input in enumerate(test_inputs):
        try:
            flags, pairs = cf.get_flag([country_input])

            if flags and pairs:
                flag_emoji = flags
                country_name = pairs[0][0] if pairs else "Unknown"

                # Store the canonical result (first successful conversion)
                if i == 0:
                    canonical_flag = flag_emoji
                    canonical_country = (
                        "United Kingdom"  # Expected canonical country name
                    )

                results.append(
                    {
                        "input": country_input,
                        "flag": flag_emoji,
                        "country": country_name,
                        "success": True,
                        "matches_canonical": flag_emoji == canonical_flag,
                    }
                )

                print(
                    f"✓ Input: '{country_input:2}' → Flag: {flag_emoji} → Country: {country_name}"
                )

            else:
                results.append(
                    {
                        "input": country_input,
                        "flag": None,
                        "country": None,
                        "success": False,
                        "matches_canonical": False,
                    }
                )

                print(f"✗ Input: '{country_input}' → FAILED: No flag returned")

        except Exception as e:
            results.append(
                {
                    "input": country_input,
                    "flag": None,
                    "country": None,
                    "success": False,
                    "matches_canonical": False,
                }
            )
            print(f"✗ Input: '{country_input}' → ERROR: {e}")

    print()
    print("Validation Results:")
    print("-" * 30)

    # Check if all inputs produced the same flag
    all_successful = all(r["success"] for r in results)
    all_same_flag = all(r["matches_canonical"] for r in results if r["success"])

    if all_successful and all_same_flag:
        print("✓ SUCCESS: All inputs map to the same flag")
        print(f"✓ Canonical flag: {canonical_flag}")
        print("✓ Normalization logic works correctly")

        # Test reverse lookup as well
        print()
        print("Testing reverse lookup:")
        try:
            reverse_result = cf.reverse_lookup([canonical_flag])
            if reverse_result:
                reverse_country = reverse_result[0][1]
                print(f"✓ Reverse lookup: {canonical_flag} → {reverse_country}")
            else:
                print("✗ Reverse lookup failed")
        except Exception as e:
            print(f"✗ Reverse lookup error: {e}")

        return True

    else:
        print("✗ FAILURE: Not all inputs map to the same result")

        # Show detailed results
        for result in results:
            status = "✓" if result["success"] else "✗"
            match_status = "✓" if result["matches_canonical"] else "✗"
            print(
                f"  {status} '{result['input']}' → {result['flag']} (matches canonical: {match_status})"
            )

        return False


def test_additional_case_variations():
    """
    Test additional case variations to ensure comprehensive coverage.
    """
    print()
    print("Testing additional case variations:")
    print("-" * 40)

    cf = CountryFlag()

    # Additional test cases for thorough validation
    additional_cases = [
        "gb",  # lowercase gb
        "gB",  # mixed case
        "Uk",  # mixed case UK
        "uK",  # mixed case
    ]

    success_count = 0

    for case in additional_cases:
        try:
            flags, pairs = cf.get_flag([case])
            if flags and "🇬🇧" in flags:
                print(f"✓ '{case}' → {flags}")
                success_count += 1
            else:
                print(f"✗ '{case}' → {flags} (unexpected)")
        except Exception as e:
            print(f"✗ '{case}' → ERROR: {e}")

    print(f"Additional cases passed: {success_count}/{len(additional_cases)}")
    return success_count == len(additional_cases)


def main():
    """Main test function"""
    print("Country Flag Alias and Case-Insensitivity Test")
    print("=" * 50)

    # Run primary test
    primary_success = test_alias_and_case_normalization()

    # Run additional tests
    additional_success = test_additional_case_variations()

    # Final result
    print()
    print("=" * 60)
    if primary_success and additional_success:
        print("🎉 ALL TESTS PASSED!")
        print("✓ Alias handling works correctly (UK ↔ GB)")
        print("✓ Case insensitivity works correctly")
        print("✓ Normalization logic is robust")
        return 0
    else:
        print("❌ SOME TESTS FAILED!")
        if not primary_success:
            print("✗ Primary alias/case tests failed")
        if not additional_success:
            print("✗ Additional case variation tests failed")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
