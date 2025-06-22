#!/usr/bin/env python3
"""
Example CLI script using countryflag.

This script demonstrates how to create a custom command-line tool
that uses countryflag to convert country names to emoji flags.
"""

import argparse
import csv
import io
import json
import sys
from typing import Any, Dict, List, Optional, Tuple

from countryflag.cache import DiskCache, MemoryCache
from countryflag.core import CountryFlag
from countryflag.core.exceptions import CountryFlagError, InvalidCountryError


def read_countries_from_file(file_path: str) -> List[str]:
    """
    Read country names from a file.

    Args:
        file_path: Path to the file containing country names.

    Returns:
        List[str]: A list of country names.

    Raises:
        FileNotFoundError: If the file does not exist.
        IOError: If the file cannot be read.
    """
    try:
        with open(file_path, encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}")
        sys.exit(1)
    except OSError as e:
        print(f"Error reading file {file_path}: {e}")
        sys.exit(1)


def write_output_to_file(output: str, file_path: str) -> None:
    """
    Write output to a file.

    Args:
        output: The output to write.
        file_path: Path to the file to write to.

    Raises:
        IOError: If the file cannot be written.
    """
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(output)
    except OSError as e:
        print(f"Error writing to file {file_path}: {e}")
        sys.exit(1)


def process_countries(
    countries: List[str],
    output_format: str = "text",
    separator: str = " ",
    fuzzy_matching: bool = False,
    cache_type: Optional[str] = None,
    cache_dir: Optional[str] = None,
) -> str:
    """
    Process a list of country names.

    Args:
        countries: A list of country names to process.
        output_format: The output format ("text", "json", or "csv").
        separator: The separator to use between flags.
        fuzzy_matching: Whether to use fuzzy matching.
        cache_type: The type of cache to use ("memory" or "disk").
        cache_dir: The directory to use for disk cache.

    Returns:
        str: The processed output.

    Raises:
        InvalidCountryError: If a country name is invalid and fuzzy matching is disabled.
    """
    # Create a cache if requested
    cache = None
    if cache_type == "memory":
        cache = MemoryCache()
    elif cache_type == "disk":
        if not cache_dir:
            cache_dir = "./.countryflag_cache"
        cache = DiskCache(cache_dir)

    # Create a CountryFlag instance with the cache
    cf = CountryFlag(cache=cache)

    try:
        # Convert country names to flags
        flags, pairs = cf.get_flag(
            countries, separator=separator, fuzzy_matching=fuzzy_matching
        )

        # Format the output
        return cf.format_output(pairs, output_format=output_format, separator=separator)
    except InvalidCountryError as e:
        if fuzzy_matching:
            print(f"Warning: {str(e)}")
            print("Using fuzzy matching to find similar country names.")
            return process_countries(
                countries, output_format, separator, True, cache_type, cache_dir
            )
        else:
            raise


def get_region_flags(
    region: str,
    output_format: str = "text",
    separator: str = " ",
    cache_type: Optional[str] = None,
    cache_dir: Optional[str] = None,
) -> str:
    """
    Get flags for all countries in a region.

    Args:
        region: The region name.
        output_format: The output format ("text", "json", or "csv").
        separator: The separator to use between flags.
        cache_type: The type of cache to use ("memory" or "disk").
        cache_dir: The directory to use for disk cache.

    Returns:
        str: The processed output.

    Raises:
        RegionError: If the region is invalid.
    """
    # Create a cache if requested
    cache = None
    if cache_type == "memory":
        cache = MemoryCache()
    elif cache_type == "disk":
        if not cache_dir:
            cache_dir = "./.countryflag_cache"
        cache = DiskCache(cache_dir)

    # Create a CountryFlag instance with the cache
    cf = CountryFlag(cache=cache)

    # Get flags for the region
    flags, pairs = cf.get_flags_by_region(region, separator=separator)

    # Format the output
    return cf.format_output(pairs, output_format=output_format, separator=separator)


def list_regions(output_format: str = "text") -> str:
    """
    List all supported regions.

    Args:
        output_format: The output format ("text", "json", or "csv").

    Returns:
        str: The list of regions in the specified format.
    """
    cf = CountryFlag()
    regions = cf._converter.get_supported_regions()

    if output_format == "json":
        return json.dumps(regions)
    elif output_format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Region"])
        for region in regions:
            writer.writerow([region])
        return output.getvalue()
    else:
        return "\n".join(regions)


def list_countries(output_format: str = "text") -> str:
    """
    List all supported countries.

    Args:
        output_format: The output format ("text", "json", or "csv").

    Returns:
        str: The list of countries in the specified format.
    """
    cf = CountryFlag()
    countries = cf.get_supported_countries()

    if output_format == "json":
        return json.dumps(countries)
    elif output_format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Name", "ISO2", "ISO3", "Official Name"])
        for country in countries:
            writer.writerow(
                [
                    country["name"],
                    country["iso2"],
                    country["iso3"],
                    country["official_name"],
                ]
            )
        return output.getvalue()
    else:
        return "\n".join(
            [f"{country['name']} ({country['iso2']})" for country in countries]
        )


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Convert country names to emoji flags."
    )

    # Input group
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "countries", nargs="*", metavar="COUNTRY", help="Country names to convert"
    )
    input_group.add_argument(
        "--file",
        "-i",
        metavar="FILE",
        help="File containing country names, one per line",
    )
    input_group.add_argument(
        "--region",
        "-r",
        metavar="REGION",
        help="Get flags for all countries in a region",
    )
    input_group.add_argument(
        "--list-regions", action="store_true", help="List all supported regions"
    )
    input_group.add_argument(
        "--list-countries", action="store_true", help="List all supported countries"
    )

    # Output options
    parser.add_argument(
        "--output", "-o", metavar="FILE", help="Output file (default: stdout)"
    )
    parser.add_argument(
        "--format",
        "-f",
        choices=["text", "json", "csv"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--separator",
        "-s",
        default=" ",
        help="Separator for text output (default: space)",
    )

    # Processing options
    parser.add_argument(
        "--fuzzy",
        "-z",
        action="store_true",
        help="Enable fuzzy matching for country names",
    )

    # Cache options
    cache_group = parser.add_argument_group("cache options")
    cache_group.add_argument(
        "--cache", choices=["memory", "disk"], help="Enable caching (memory or disk)"
    )
    cache_group.add_argument(
        "--cache-dir", metavar="DIR", help="Directory for disk cache"
    )

    args = parser.parse_args()

    try:
        # Process based on the input option
        if args.list_regions:
            output = list_regions(args.format)
        elif args.list_countries:
            output = list_countries(args.format)
        elif args.region:
            output = get_region_flags(
                args.region, args.format, args.separator, args.cache, args.cache_dir
            )
        else:
            # Get country names
            if args.file:
                countries = read_countries_from_file(args.file)
            else:
                countries = args.countries

            # Process the countries
            output = process_countries(
                countries,
                args.format,
                args.separator,
                args.fuzzy,
                args.cache,
                args.cache_dir,
            )

        # Output the result
        if args.output:
            write_output_to_file(output, args.output)
        else:
            print(output)

    except CountryFlagError as e:
        print(f"Error: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
