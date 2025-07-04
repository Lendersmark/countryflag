"""
Command-line interface for the countryflag package.

This module contains the command-line interface for the countryflag package.
"""

import argparse
import asyncio
import csv
import json
import logging
import os
import re
import sys
from io import StringIO
from pathlib import Path
from typing import List, Tuple

import prompt_toolkit
from prompt_toolkit.completion import WordCompleter

from countryflag import __version__
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
from countryflag.utils.text import norm_newlines

# Configure UTF-8 output for Windows to prevent mojibake
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Configure logging
logger = logging.getLogger("countryflag.cli")


def _merge_country_tokens(tokens: List[str], cf: CountryFlag) -> List[str]:
    """
    Re-assemble tokens that were unintentionally split by the shell
    (typical on Windows when quotes are not honoured).

    We scan greedily from left to right, always taking the longest sequence
    of remaining tokens that forms a valid country name. We avoid merging
    tokens if it results in fuzzy matches that don't represent real countries.
    """
    merged: List[str] = []
    i = 0
    n = len(tokens)

    # List of known multi-word countries to avoid false matches
    known_multi_word_countries = {
        "united states",
        "united kingdom",
        "south africa",
        "new zealand",
        "costa rica",
        "puerto rico",
        "sri lanka",
        "saudi arabia",
        "south korea",
        "north korea",
        "czech republic",
        "dominican republic",
        "el salvador",
        "hong kong",
        "san marino",
        "burkina faso",
        "cape verde",
        "ivory coast",
        "papua new guinea",
        "sierra leone",
        "south sudan",
        "trinidad and tobago",
        "united arab emirates",
        "bosnia and herzegovina",
        "antigua and barbuda",
        "saint kitts and nevis",
        "saint vincent and the grenadines",
        "central african republic",
        "united states of america",
        "united states america",
        "usa",
    }

    while i < n:
        found_match = False
        # Try longest slice first, but limit to reasonable boundaries
        for j in range(
            min(n, i + 6), i, -1
        ):  # Max 6 tokens for very long country names
            candidate = " ".join(tokens[i:j])
            candidate_lower = candidate.lower()

            # Check if it's a known multi-word country first,
            # or try combinations for multi-word candidates
            if candidate_lower in known_multi_word_countries:
                # Validate it's actually recognized by the converter
                try:
                    code = cf._converter.convert(candidate)
                    if code != "not found" and len(code) <= 3:
                        merged.append(candidate)
                        i = j
                        found_match = True
                        break
                except Exception:
                    pass
            elif j > i + 1:  # Only try multi-word combinations for reasonable cases
                # For non-known multi-word combinations, be more conservative
                # Only merge if each individual token doesn't work on its own
                individual_tokens_invalid = True
                for k in range(i, j):
                    try:
                        individual_code = cf._converter.convert(tokens[k])
                        if individual_code != "not found":
                            individual_tokens_invalid = False
                            break
                    except Exception:
                        pass

                # Only merge if individual tokens are invalid
                # AND the combined result is valid
                if individual_tokens_invalid:
                    try:
                        code = cf._converter.convert(candidate)
                        if code != "not found" and len(code) <= 3:
                            merged.append(candidate)
                            i = j
                            found_match = True
                            break
                    except Exception:
                        pass

        if not found_match:
            # No multi-word match found - keep original token as-is
            merged.append(tokens[i])
            i += 1

    return merged


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
            country_names = _merge_country_tokens(args.countries, country_flag)
        # Note: positional arguments are not used in async mode as they are
        # handled in preprocessing

        # Handle region-based lookup
        if args.region:
            flags, country_flag_pairs = country_flag.get_flags_by_region(
                args.region, args.separator
            )
            output = country_flag.format_output(
                country_flag_pairs, args.format, args.separator
            )
            if isinstance(output, str):
                print(norm_newlines(output))
            else:
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
                output = json.dumps(result, ensure_ascii=False)
                print(norm_newlines(output) if isinstance(output, str) else output)
            elif args.format == "csv":
                output = StringIO()
                writer = csv.writer(output)
                writer.writerow(["Flag", "Country"])
                for flag, country in flag_country_pairs:
                    writer.writerow([flag, country])
                output_str = output.getvalue()
                print(
                    norm_newlines(output_str)
                    if isinstance(output_str, str)
                    else output_str
                )
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
            print(norm_newlines(output) if isinstance(output, str) else output)

    except InvalidCountryError as ice:
        print(f"Error: {str(ice)}", file=sys.stderr)

        # If fuzzy matching is enabled, suggest alternatives
        if args.fuzzy:
            converter = CountryConverterSingleton()
            matches = converter.find_close_matches(ice.country, args.threshold)
            if matches:
                print("\nDid you mean one of these?", file=sys.stderr)
                for name, code in matches:
                    print(f"  - {name} ({code})", file=sys.stderr)

        print(
            "\nUse --list-countries to see all supported country names", file=sys.stderr
        )
        sys.exit(1)

    except RegionError as re:
        print(f"Error: {str(re)}", file=sys.stderr)
        print(
            f"\nSupported regions: {', '.join(RegionDefinitions.REGIONS)}",
            file=sys.stderr,
        )
        sys.exit(1)

    except ReverseConversionError as rce:
        print(f"Error: {str(rce)}", file=sys.stderr)
        sys.exit(1)

    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


def preprocess_args(args: List[str]) -> Tuple[List[str], List[str]]:
    """
    Preprocess command line arguments to handle backwards compatibility.

    When mutually exclusive flags are present along with positional arguments,
    the positional arguments should be ignored (backwards compatibility).

    Args:
        args: List of command line arguments

    Returns:
        Tuple of (processed_args_for_parser, extracted_positional_args)
    """
    # Flags that are mutually exclusive with positional arguments
    mutually_exclusive_flags = {
        "--countries",
        "--file",
        "--files",
        "--reverse",
        "--region",
        "--interactive",
    }

    # Check if any mutually exclusive flag is present
    has_mutually_exclusive_flag = any(flag in args for flag in mutually_exclusive_flags)

    processed_args = []
    extracted_positional = []
    i = 0

    while i < len(args):
        arg = args[i]
        if arg.startswith("-"):
            processed_args.append(arg)
            # Handle flags that take values
            if arg in [
                "--file",
                "--region",
                "--threshold",
                "--language",
                "--validate",
                "--workers",
                "--cache-dir",
                "--separator",
                "--format",
            ]:
                # Single value flags
                if i + 1 < len(args) and not args[i + 1].startswith("-"):
                    i += 1
                    processed_args.append(args[i])
            elif arg in ["--countries", "--files", "--reverse"]:
                # Multi-value flags - collect all non-flag arguments following this flag
                while i + 1 < len(args) and not args[i + 1].startswith("-"):
                    i += 1
                    processed_args.append(args[i])
        else:
            # This is a positional argument
            if has_mutually_exclusive_flag:
                # Ignore positional args when mutually exclusive flags are
                # present (backwards compatibility)
                pass
            else:
                # Keep positional args when no mutually exclusive flags are present
                extracted_positional.append(arg)
        i += 1

    return processed_args, extracted_positional


def main() -> None:
    """
    Entry point to the script.

    Parses command line arguments and executes the main functionality.
    """
    # Preprocess arguments for backwards compatibility
    import sys

    processed_args, extracted_positional = preprocess_args(sys.argv[1:])

    # Parse arguments
    parser = argparse.ArgumentParser(
        description=(
            "Countryflag: a Python package for converting country names into "
            "emoji flags."
        ),
        epilog="""Examples:
  countryflag italy france spain                    # Positional arguments
  countryflag --countries italy france spain       # Named arguments
  countryflag --format json italy france           # JSON output
  countryflag --region Europe                       # Regional flags
  countryflag --reverse 🇮🇹 🇫🇷 🇪🇸              # Flag to country
  countryflag --interactive                         # Interactive mode

Both positional and named argument forms are equivalent.""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
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

    # Note: Positional arguments are handled via preprocessing to maintain
    # backwards compatibility

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
    parser.add_argument(
        "--version",
        action="version",
        version=f"countryflag {__version__}",
        help="Show program's version number and exit",
    )

    # Parse the preprocessed arguments
    args = parser.parse_args(processed_args)

    # Normalize quoted arguments (Windows compatibility)
    # Handle separator argument
    if (
        args.separator
        and len(args.separator) >= 2
        and args.separator[0] == args.separator[-1] in {'"', "'"}
    ):
        args.separator = args.separator[1:-1]

    # Handle cache_dir argument - strip quotes and normalize path
    if args.cache_dir:
        # Strip surrounding quotes if present
        if len(args.cache_dir) >= 2 and args.cache_dir[0] == args.cache_dir[-1] in {
            '"',
            "'",
        }:
            args.cache_dir = args.cache_dir[1:-1]
        # Normalize path with user expansion and resolution
        args.cache_dir = str(Path(os.path.expanduser(args.cache_dir)).resolve())

    # Handle other single-char options that might be wrapped in quotes
    # No other single-char options currently need this treatment, but this
    # provides a pattern for future options

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
            output = json.dumps(countries, ensure_ascii=False)
            print(norm_newlines(output) if isinstance(output, str) else output)
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
            output_str = output.getvalue()
            print(
                norm_newlines(output_str) if isinstance(output_str, str) else output_str
            )
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
            output = json.dumps(regions, ensure_ascii=False)
            print(norm_newlines(output) if isinstance(output, str) else output)
        elif args.format == "csv":
            output = StringIO()
            writer = csv.writer(output)
            writer.writerow(["Region"])
            for region in regions:
                writer.writerow([region])
            output_str = output.getvalue()
            print(
                norm_newlines(output_str) if isinstance(output_str, str) else output_str
            )
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
            country_names = _merge_country_tokens(args.countries, country_flag)
        elif extracted_positional and not any(
            [
                args.file,
                args.files,
                args.reverse,
                args.region,
                args.interactive,
            ]
        ):
            # Treat positional countries same as --countries when no other
            # input source is specified
            country_names = _merge_country_tokens(extracted_positional, country_flag)

        # Handle region-based lookup
        if args.region:
            flags, country_flag_pairs = country_flag.get_flags_by_region(
                args.region, args.separator
            )
            output = country_flag.format_output(
                country_flag_pairs, args.format, args.separator
            )
            print(norm_newlines(output) if isinstance(output, str) else output)
            return

        # Handle flag to country conversion (reverse lookup)
        if args.reverse:
            flag_country_pairs = country_flag.reverse_lookup(args.reverse)

            if args.format == "json":
                result = [
                    {"flag": flag, "country": country}
                    for flag, country in flag_country_pairs
                ]
                output = json.dumps(result, ensure_ascii=False)
                print(norm_newlines(output) if isinstance(output, str) else output)
            elif args.format == "csv":
                output = StringIO()
                writer = csv.writer(output)
                writer.writerow(["Flag", "Country"])
                for flag, country in flag_country_pairs:
                    writer.writerow([flag, country])
                output_str = output.getvalue()
                print(
                    norm_newlines(output_str)
                    if isinstance(output_str, str)
                    else output_str
                )
            else:
                for flag, country in flag_country_pairs:
                    print(f"{flag} -> {country}")

        # Handle country to flag conversion
        elif country_names:
            # Pre-process country names to handle shell-escaped empty strings
            processed_names = []
            for name in country_names:
                # Convert shell-escaped empty string to actual empty string
                if name == "''" or name == '""':
                    processed_names.append("")
                else:
                    processed_names.append(name)

            # Check for empty strings first
            has_empty_string = any(name == "" for name in processed_names)
            if has_empty_string:
                print("Error: country names cannot be empty", file=sys.stderr)
                print(
                    "\nUse --list-countries to see all supported country names",
                    file=sys.stderr,
                )
                sys.exit(1)

            # Handle mixed valid/invalid countries by processing individually
            successful_pairs = []
            had_errors = False

            for country_name in processed_names:
                try:
                    flags, pairs = country_flag.get_flag(
                        [country_name], args.separator, args.fuzzy, args.threshold
                    )
                    successful_pairs.extend(pairs)
                except InvalidCountryError as ice:
                    had_errors = True
                    print(f"Error: {str(ice)}", file=sys.stderr)

                    # If fuzzy matching is enabled, suggest alternatives
                    if args.fuzzy:
                        converter = CountryConverterSingleton()
                        matches = converter.find_close_matches(
                            ice.country, args.threshold
                        )
                        if matches:
                            print(
                                f"Did you mean one of these for '{ice.country}'?",
                                file=sys.stderr,
                            )
                            for name, code in matches[:3]:  # Show top 3 matches
                                print(f"  - {name} ({code})", file=sys.stderr)

                    # For single invalid country, exit with error
                    if len(processed_names) == 1:
                        print(
                            "\nUse --list-countries to see all supported country names",
                            file=sys.stderr,
                        )
                        sys.exit(1)

            # Output successful results if any
            if successful_pairs:
                output = country_flag.format_output(
                    successful_pairs, args.format, args.separator
                )
                print(norm_newlines(output) if isinstance(output, str) else output)

            # If we had errors but also successful conversions, don't exit with error
            # Only exit with error if ALL countries failed
            if had_errors and not successful_pairs:
                print(
                    "\nUse --list-countries to see all supported country names",
                    file=sys.stderr,
                )
                sys.exit(1)
        else:
            # No input provided - show helpful message and examples
            print("CountryFlag: Convert country names to emoji flags\n")
            print("Usage examples:")
            print(
                "  countryflag italy france spain                    "
                "# Convert countries to flags"
            )
            print(
                "  countryflag --countries italy france spain       " "# Same as above"
            )
            print(
                "  countryflag --reverse 🇮🇹 🇫🇷 🇪🇸              "
                "# Convert flags to countries"
            )
            print(
                "  countryflag --region Europe                       "
                "# Get all European flags"
            )
            print(
                "  countryflag --interactive                         # Interactive mode"
            )
            print(
                "  countryflag --list-countries                      "
                "# List all supported countries"
            )
            print("  countryflag --help                               # Show full help")
            print("\nFor more options, use: countryflag --help")
            sys.exit(0)

    except InvalidCountryError as ice:
        print(f"Error: {str(ice)}", file=sys.stderr)

        # If fuzzy matching is enabled, suggest alternatives
        if args.fuzzy:
            converter = CountryConverterSingleton()
            matches = converter.find_close_matches(ice.country, args.threshold)
            if matches:
                print("\nDid you mean one of these?", file=sys.stderr)
                for name, code in matches:
                    print(f"  - {name} ({code})", file=sys.stderr)

        print(
            "\nUse --list-countries to see all supported country names", file=sys.stderr
        )
        sys.exit(1)

    except RegionError as re:
        print(f"Error: {str(re)}", file=sys.stderr)
        print(
            f"\nSupported regions: {', '.join(RegionDefinitions.REGIONS)}",
            file=sys.stderr,
        )
        sys.exit(1)

    except ReverseConversionError as rce:
        print(f"Error: {str(rce)}", file=sys.stderr)
        sys.exit(1)

    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)

    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
