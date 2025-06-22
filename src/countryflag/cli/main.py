"""
Command-line interface for the countryflag package.

This module contains the command-line interface for the countryflag package.
"""

import argparse
import asyncio
import csv
import json
import logging
import re
import sys
from io import StringIO
from typing import Any, Dict, List, Optional, Tuple

import prompt_toolkit
from prompt_toolkit.completion import WordCompleter

from countryflag.cache import DiskCache, MemoryCache
from countryflag.core.converters import CountryConverterSingleton
from countryflag.core.exceptions import (
    InvalidCountryError,
    RegionError,
    ReverseConversionError,
)
from countryflag.core.flag import CountryFlag
from countryflag.core.models import RegionDefinitions
from countryflag.utils.io import (
    process_file_input,
    process_file_input_async,
    process_multiple_files,
)

# Configure logging
logger = logging.getLogger("countryflag.cli")


def run_interactive_mode(country_flag: CountryFlag) -> None:
    """
    Run the interactive CLI mode with autocomplete.

    Args:
        country_flag: The CountryFlag instance to use.
    """
    # Get all country names for autocompletion
    countries = country_flag.get_supported_countries()
    country_names = [country["name"] for country in countries]

    print("CountryFlag Interactive Mode")
    print("Type country names to get their flags. Type 'exit' or 'quit' to exit.")
    print("Press Tab for autocompletion.")

    # Create a completer with country names
    country_completer = WordCompleter(country_names, ignore_case=True)

    while True:
        try:
            # Get input with autocompletion
            user_input = prompt_toolkit.prompt("> ", completer=country_completer)

            if user_input.lower() in ("exit", "quit"):
                break

            # Split input by commas or spaces
            country_list = [
                c.strip() for c in re.split(r"[,\s]+", user_input) if c.strip()
            ]

            if country_list:
                flags, pairs = country_flag.get_flag(country_list, fuzzy_matching=True)

                # Display results
                for name, emoji in pairs:
                    print(f"{name}: {emoji}")

                print("\nCombined: " + flags)

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {str(e)}")

    print("Exiting interactive mode.")


async def run_async_main(args: argparse.Namespace) -> None:
    """
    Asynchronous version of the main function.

    Args:
        args: The parsed command-line arguments.
    """
    # Set logging level based on verbose flag
    if args.verbose:
        logger.setLevel(logging.DEBUG)

    # Initialize the CountryFlag class with caching if enabled
    cache = None
    if args.cache:
        if args.cache_dir:
            cache = DiskCache(args.cache_dir)
        else:
            cache = MemoryCache()

    country_flag = CountryFlag(language=args.language, cache=cache)

    try:
        # Process input
        country_names = []
        if args.file:
            # Use async file processing for larger files
            country_names = await process_file_input_async(args.file)
        elif args.files:
            # Use parallel processing for multiple files
            country_names = process_multiple_files(args.files, max_workers=args.workers)
        elif args.countries:
            country_names = args.countries

        # Handle region-based lookup
        if args.region:
            flags, country_flag_pairs = country_flag.get_flags_by_region(
                args.region, args.separator
            )
            output = country_flag.format_output(
                country_flag_pairs, args.format, args.separator
            )
            print(output)
            return

        # Handle flag to country conversion (reverse lookup)
        if args.reverse:
            flag_country_pairs = country_flag.reverse_lookup(args.reverse)

            if args.format == "json":
                result = [
                    {"flag": flag, "country": country}
                    for flag, country in flag_country_pairs
                ]
                print(json.dumps(result, ensure_ascii=False))
            elif args.format == "csv":
                output = StringIO()
                writer = csv.writer(output)
                writer.writerow(["Flag", "Country"])
                for flag, country in flag_country_pairs:
                    writer.writerow([flag, country])
                print(output.getvalue())
            else:
                for flag, country in flag_country_pairs:
                    print(f"{flag} -> {country}")

        # Handle country to flag conversion
        elif country_names:
            flags, country_flag_pairs = country_flag.get_flag(
                country_names, args.separator, args.fuzzy, args.threshold
            )
            output = country_flag.format_output(
                country_flag_pairs, args.format, args.separator
            )
            print(output)

    except InvalidCountryError as ice:
        logger.error(str(ice))
        print(f"Error: {str(ice)}")

        # If fuzzy matching is enabled, suggest alternatives
        if args.fuzzy:
            converter = CountryConverterSingleton()
            matches = converter.find_close_matches(ice.country, args.threshold)
            if matches:
                print("\nDid you mean one of these?")
                for name, code in matches:
                    print(f"  - {name} ({code})")

        print("\nUse --list-countries to see all supported country names")
        sys.exit(1)

    except RegionError as re:
        logger.error(str(re))
        print(f"Error: {str(re)}")
        print(f"\nSupported regions: {', '.join(RegionDefinitions.REGIONS)}")
        sys.exit(1)

    except ReverseConversionError as rce:
        logger.error(str(rce))
        print(f"Error: {str(rce)}")
        sys.exit(1)

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        print(f"Error: {str(e)}")
        sys.exit(1)


def main() -> None:
    """
    Entry point to the script.

    Parses command line arguments and executes the main functionality.
    """
    # Parse arguments
    parser = argparse.ArgumentParser(
        description="Countryflag: a Python package for converting country names into emoji flags."
    )

    # Input group
    input_group = parser.add_mutually_exclusive_group(required=False)
    input_group.add_argument(
        "--countries",
        metavar="COUNTRY",
        nargs="*",
        help="Country names to be converted into emojis, separated by spaces",
    )
    input_group.add_argument(
        "--file",
        "-i",
        metavar="FILE",
        help="File containing country names, one per line",
    )
    input_group.add_argument(
        "--files",
        nargs="+",
        metavar="FILES",
        help="Multiple files containing country names, processed in parallel",
    )
    input_group.add_argument(
        "--reverse",
        "-r",
        nargs="+",
        metavar="FLAG",
        help="Convert flag emojis to country names",
    )
    input_group.add_argument(
        "--region",
        choices=RegionDefinitions.REGIONS,
        help="Get flags for all countries in a specific region/continent",
    )
    input_group.add_argument(
        "--interactive",
        "-I",
        action="store_true",
        help="Run in interactive mode with autocompletion",
    )

    # Output options
    parser.add_argument(
        "--format",
        "-f",
        choices=["text", "json", "csv"],
        default="text",
        help="Output format (text, json, or csv)",
    )
    parser.add_argument(
        "--separator",
        "-s",
        default=" ",
        help="Separator character between flags (default: space)",
    )

    # Utility options
    parser.add_argument(
        "--fuzzy",
        "-z",
        action="store_true",
        help="Enable fuzzy matching for country names",
    )
    parser.add_argument(
        "--threshold",
        "-t",
        type=float,
        default=0.6,
        help="Similarity threshold for fuzzy matching (0-1, default: 0.6)",
    )
    parser.add_argument(
        "--language",
        "-l",
        default="en",
        help="Language for country names (ISO 639-1 code, default: en)",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )
    parser.add_argument(
        "--list-countries",
        action="store_true",
        help="List all supported countries and exit",
    )
    parser.add_argument(
        "--list-regions",
        action="store_true",
        help="List all supported regions/continents and exit",
    )
    parser.add_argument(
        "--validate", metavar="COUNTRY", help="Validate a country name and exit"
    )
    parser.add_argument(
        "--workers",
        "-w",
        type=int,
        default=4,
        help="Number of worker threads for parallel processing (default: 4)",
    )
    parser.add_argument(
        "--async",
        "-a",
        action="store_true",
        dest="use_async",
        help="Use asynchronous file processing (faster for large files)",
    )
    parser.add_argument(
        "--cache",
        "-c",
        action="store_true",
        help="Enable caching to improve performance",
    )
    parser.add_argument(
        "--cache-dir",
        metavar="DIR",
        help="Directory to store cache files (if not specified, in-memory cache is used)",
    )

    args = parser.parse_args()

    # Set logging level based on verbose flag
    if args.verbose:
        logger.setLevel(logging.DEBUG)

    # Initialize the CountryFlag class with caching if enabled
    cache = None
    if args.cache:
        if args.cache_dir:
            cache = DiskCache(args.cache_dir)
        else:
            cache = MemoryCache()

    country_flag = CountryFlag(language=args.language, cache=cache)

    # Handle special commands
    if args.list_countries:
        countries = country_flag.get_supported_countries()
        if args.format == "json":
            print(json.dumps(countries, ensure_ascii=False))
        elif args.format == "csv":
            output = StringIO()
            writer = csv.writer(output)
            writer.writerow(["Name", "ISO2", "ISO3", "Official Name", "Region"])
            for country in countries:
                writer.writerow(
                    [
                        country["name"],
                        country["iso2"],
                        country["iso3"],
                        country["official_name"],
                        country.get("region", ""),
                    ]
                )
            print(output.getvalue())
        else:
            for country in countries:
                region = (
                    f" ({country.get('region', '')})" if country.get("region") else ""
                )
                print(f"{country['name']} ({country['iso2']}){region}")
        sys.exit(0)

    if args.list_regions:
        regions = RegionDefinitions.REGIONS
        if args.format == "json":
            print(json.dumps(regions, ensure_ascii=False))
        elif args.format == "csv":
            output = StringIO()
            writer = csv.writer(output)
            writer.writerow(["Region"])
            for region in regions:
                writer.writerow([region])
            print(output.getvalue())
        else:
            print("Supported regions/continents:")
            for region in regions:
                print(f"  - {region}")
        sys.exit(0)

    if args.validate:
        is_valid = country_flag.validate_country_name(args.validate)
        if is_valid:
            print(f"'{args.validate}' is a valid country name")
        else:
            print(f"'{args.validate}' is NOT a valid country name")

            # If fuzzy matching is enabled, suggest alternatives
            if args.fuzzy:
                converter = CountryConverterSingleton()
                matches = converter.find_close_matches(args.validate, args.threshold)
                if matches:
                    print("\nDid you mean one of these?")
                    for name, code in matches:
                        print(f"  - {name} ({code})")

        sys.exit(0 if is_valid else 1)

    # Run interactive mode
    if args.interactive:
        run_interactive_mode(country_flag)
        sys.exit(0)

    # Use async main if requested
    if args.use_async or args.file or args.files:
        try:
            # Run the async version
            asyncio.run(run_async_main(args))
        except KeyboardInterrupt:
            print("\nOperation cancelled by user.")
            sys.exit(1)
        return

    # Regular synchronous execution
    try:
        # Process input
        country_names = []
        if args.file:
            country_names = process_file_input(args.file)
        elif args.files:
            country_names = process_multiple_files(args.files, max_workers=args.workers)
        elif args.countries:
            country_names = args.countries

        # Handle region-based lookup
        if args.region:
            flags, country_flag_pairs = country_flag.get_flags_by_region(
                args.region, args.separator
            )
            output = country_flag.format_output(
                country_flag_pairs, args.format, args.separator
            )
            print(output)
            return

        # Handle flag to country conversion (reverse lookup)
        if args.reverse:
            flag_country_pairs = country_flag.reverse_lookup(args.reverse)

            if args.format == "json":
                result = [
                    {"flag": flag, "country": country}
                    for flag, country in flag_country_pairs
                ]
                print(json.dumps(result, ensure_ascii=False))
            elif args.format == "csv":
                output = StringIO()
                writer = csv.writer(output)
                writer.writerow(["Flag", "Country"])
                for flag, country in flag_country_pairs:
                    writer.writerow([flag, country])
                print(output.getvalue())
            else:
                for flag, country in flag_country_pairs:
                    print(f"{flag} -> {country}")

        # Handle country to flag conversion
        elif country_names:
            flags, country_flag_pairs = country_flag.get_flag(
                country_names, args.separator, args.fuzzy, args.threshold
            )
            output = country_flag.format_output(
                country_flag_pairs, args.format, args.separator
            )
            print(output)

    except InvalidCountryError as ice:
        logger.error(str(ice))
        print(f"Error: {str(ice)}")

        # If fuzzy matching is enabled, suggest alternatives
        if args.fuzzy:
            converter = CountryConverterSingleton()
            matches = converter.find_close_matches(ice.country, args.threshold)
            if matches:
                print("\nDid you mean one of these?")
                for name, code in matches:
                    print(f"  - {name} ({code})")

        print("\nUse --list-countries to see all supported country names")
        sys.exit(1)

    except RegionError as re:
        logger.error(str(re))
        print(f"Error: {str(re)}")
        print(f"\nSupported regions: {', '.join(RegionDefinitions.REGIONS)}")
        sys.exit(1)

    except ReverseConversionError as rce:
        logger.error(str(rce))
        print(f"Error: {str(rce)}")
        sys.exit(1)

    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
