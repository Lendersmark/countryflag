#!/usr/bin/env python3
"""
Comprehensive Usage Examples for CountryFlag

This script demonstrates the various features and capabilities of the
CountryFlag package, including basic and advanced usage patterns.
"""

import json
import logging
from pprint import pprint

# Import both the simple interface and the core class
import countryflag
from countryflag.core.exceptions import (
    InvalidCountryError,
    RegionError,
    ReverseConversionError,
)
from countryflag.core.flag import CountryFlag
from countryflag.utils.text import norm_newlines

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("countryflag-demo")


def separator():
    """Print a separator line for better readability."""
    print("\n" + "=" * 80 + "\n")


def demo_basic_usage():
    """Demonstrate basic usage with the convenience function."""
    print("BASIC USAGE WITH CONVENIENCE FUNCTION")
    print("-------------------------------------")

    # Simple usage with the convenience function
    countries = ["Germany", "France", "Italy", "Spain"]
    flags = countryflag.getflag(countries)
    print(f"Flags for {countries}:")
    print(flags)

    # Using ISO codes
    iso_codes = ["DE", "FR", "IT", "ES"]
    flags = countryflag.getflag(iso_codes)
    print(f"\nFlags for ISO codes {iso_codes}:")
    print(flags)

    # Using custom separator
    flags = countryflag.getflag(countries, separator=" | ")
    print(f"\nFlags with custom separator:")
    print(flags)


def demo_core_class_usage():
    """Demonstrate usage with the core CountryFlag class."""
    print("CORE CLASS USAGE")
    print("---------------")

    # Create an instance of CountryFlag
    cf = CountryFlag()

    # Basic usage
    countries = ["United States", "Canada", "Mexico", "Brazil"]
    flags, pairs = cf.get_flag(countries)

    print(f"Flags for {countries}:")
    print(flags)

    print("\nCountry-flag pairs:")
    for country, flag in pairs:
        print(f"{country}: {flag}")


def demo_output_formats():
    """Demonstrate different output formats."""
    print("OUTPUT FORMATS")
    print("-------------")

    cf = CountryFlag()
    countries = ["Japan", "China", "South Korea", "Australia"]
    _, pairs = cf.get_flag(countries)

    # Text format (default)
    text_output = cf.format_output(pairs, "text")
    print("Text format:")
    print(norm_newlines(text_output) if isinstance(text_output, str) else text_output)

    # JSON format
    json_output = cf.format_output(pairs, "json")
    print("\nJSON format:")
    parsed_json = json.loads(json_output)
    pprint(parsed_json)

    # CSV format
    csv_output = cf.format_output(pairs, "csv")
    print("\nCSV format:")
    print(norm_newlines(csv_output) if isinstance(csv_output, str) else csv_output)

    # Custom separator for text format
    custom_text = cf.format_output(pairs, "text", " 🌍 ")
    print("\nText format with custom separator:")
    print(custom_text)


def demo_fuzzy_matching():
    """Demonstrate fuzzy matching capabilities."""
    print("FUZZY MATCHING")
    print("-------------")

    cf = CountryFlag()

    # Slightly misspelled country names
    misspelled = ["Germny", "Frnace", "Itly", "Spian"]

    # Without fuzzy matching (will fail)
    print("Without fuzzy matching:")
    try:
        flags, _ = cf.get_flag(misspelled, fuzzy_matching=False)
        print(flags)
    except InvalidCountryError as e:
        print(f"Error: {e}")

    # With fuzzy matching
    print("\nWith fuzzy matching:")
    flags, pairs = cf.get_flag(misspelled, fuzzy_matching=True)
    print(flags)

    print("\nMatched country-flag pairs:")
    for country, flag in pairs:
        print(f"{country}: {flag}")

    # With custom threshold
    print("\nWith custom threshold (higher strictness):")
    flags, pairs = cf.get_flag(misspelled, fuzzy_matching=True, fuzzy_threshold=0.95)
    print(flags)

    print("\nMatched country-flag pairs (high threshold):")
    for country, flag in pairs:
        print(f"{country}: {flag}")


def demo_region_based():
    """Demonstrate region-based flag retrieval."""
    print("REGION-BASED FLAG RETRIEVAL")
    print("-------------------------")

    cf = CountryFlag()

    # Get flags for different regions
    regions = ["Europe", "North America", "Asia", "Africa"]

    for region in regions:
        try:
            flags = cf.get_flags_by_region(region)
            print(f"\nFlags for {region} ({len(flags.split())} countries):")
            # Show just the first 5 flags to keep output manageable
            first_5_flags = " ".join(flags.split()[:5])
            print(f"{first_5_flags} ...")
        except RegionError as e:
            print(f"Error for region {region}: {e}")


def demo_reverse_lookup():
    """Demonstrate reverse lookup from flag to country name."""
    print("REVERSE LOOKUP")
    print("-------------")

    cf = CountryFlag()

    # Define some emoji flags
    emoji_flags = ["🇺🇸", "🇯🇵", "🇩🇪", "🇬🇧", "🇫🇷"]

    print(f"Performing reverse lookup for: {' '.join(emoji_flags)}")

    # Lookup countries from flags
    try:
        countries = cf.reverse_lookup(emoji_flags)
        for flag, country in zip(emoji_flags, countries):
            print(f"{flag} -> {country}")
    except ReverseConversionError as e:
        print(f"Error: {e}")

    # Invalid flag for reverse lookup
    print("\nTrying reverse lookup with invalid flag:")
    try:
        countries = cf.reverse_lookup(["🏳️"])
        print(countries)
    except ReverseConversionError as e:
        print(f"Error: {e}")


def demo_error_handling():
    """Demonstrate error handling."""
    print("ERROR HANDLING")
    print("-------------")

    cf = CountryFlag()

    # Invalid country name
    print("Trying to get flag for invalid country:")
    try:
        flags, _ = cf.get_flag(["Wakanda", "Narnia"])
        print(flags)
    except InvalidCountryError as e:
        print(f"Error: {e}")

    # Invalid region
    print("\nTrying to get flags for invalid region:")
    try:
        flags = cf.get_flags_by_region("Middle Earth")
        print(flags)
    except RegionError as e:
        print(f"Error: {e}")


def demo_supported_countries():
    """Demonstrate listing supported countries."""
    print("SUPPORTED COUNTRIES")
    print("------------------")

    cf = CountryFlag()
    supported = cf.get_supported_countries()

    print(f"Total supported countries: {len(supported)}")
    print("\nSample of supported countries:")
    # Print just the first 10 countries to keep output manageable
    for country in sorted(list(supported))[:10]:
        print(f"- {country}")
    print("...")


def main():
    """Run all the demonstrations."""
    print("COUNTRYFLAG COMPREHENSIVE USAGE EXAMPLES")
    print("======================================")
    print(f"Using CountryFlag version: {countryflag.__version__}")

    separator()
    demo_basic_usage()

    separator()
    demo_core_class_usage()

    separator()
    demo_output_formats()

    separator()
    demo_fuzzy_matching()

    separator()
    demo_region_based()

    separator()
    demo_reverse_lookup()

    separator()
    demo_error_handling()

    separator()
    demo_supported_countries()

    separator()
    print("END OF DEMONSTRATIONS")


if __name__ == "__main__":
    main()
