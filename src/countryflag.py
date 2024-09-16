#!/usr/bin/env python3
# countryflag - Converts long country names to emoji flags

import sys
import flag
import argparse
import country_converter as coco


def getflag(country_name: str | list[str]) -> str:
    country_flag = ""
    
    if isinstance(country_name, str):
        country_code = coco.convert(names=country_name, to="ISO2")
        country_flag += flag.flag(country_code)
    elif isinstance(country_name, list):
        for i, name in enumerate(country_name):
            country_code = coco.convert(names=name, to="ISO2")
            if i > 0:
                country_flag += " "
            country_flag += flag.flag(country_code)
    else:
        raise ValueError("Input must be a string or a list of strings")
    
    return country_flag


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
        help="Country names to be converted into emojis, separated by spaces",
    )
    args = parser.parse_args()

    # Converts country names into emojis
    try:
        flags = getflag(args.countries)
    except ValueError as ve:
        print("Please use one of the supported country names classifications.")
        sys.exit(1)
    print(flags)


if __name__ == "__main__":
    main()
