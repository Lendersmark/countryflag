#!/usr/bin/env python3
# countryflag - Converts long country names to emoji flags

import sys
import flag
import argparse
import country_converter as coco


def getflag(country_name):
    # initialize variable
    country_flag = ""
    for i in range(0, len(country_name)):
        # convert country name into ISO2 code
        country_code = coco.convert(names=country_name[i], to="ISO2")
        # convert ISO2 code into flag
        if i >= 1:
            # If more than a country, adds a space as separator
            country_flag += " "
        country_flag += flag.flag(country_code)
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
