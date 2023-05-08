#!/usr/bin/env python3
# countryflag - Converts long country names to emoji flags

import sys
import flag
import argparse
import country_converter as coco

# Initialize cache
cache = {}

def getflag(country_names):
    # initialize variable
    country_flags = []
    for country_name in country_names:
        if country_name in cache:
            # Retrieve country flag from cache if available
            country_flags.append(cache[country_name])
        else:
            # convert country name into ISO2 code
            country_code = coco.convert(names=country_name, to="ISO2")
            if country_code is None:
                # If country code cannot be found, raise an error
                raise ValueError(f"Could not find ISO2 code for {country_name}")
            # convert ISO2 code into flag
            country_flag = flag.flag(country_code)
            # Add country flag to list of flags and to cache
            country_flags.append(country_flag)
            cache[country_name] = country_flag
    return " ".join(country_flags)


def main():
    """Entry point to the script"""

    # Parse arguments
    parser = argparse.ArgumentParser(
        description="Countryflag: a Python package for converting country names into emoji flags."
    )
    parser.add_argument(
        "countries",
        metavar="name",
        nargs="+",
        help="Country names to be converted into emojis, separated by spaces, commas, or semicolons",
    )
    args = parser.parse_args()

    # Convert input to list of country names
    country_names = []
    for arg in args.countries:
        country_names += arg.split(",") if "," in arg else arg.split(";")
    country_names = [name.strip() for name in country_names]

    # Converts country names into emojis
    try:
        flags = getflag(country_names)
    except ValueError as ve:
        print(str(ve))
        sys.exit(1)
    print(flags)


if __name__ == "__main__":
    main()
