#!/usr/bin/env python3
# countryflag - Converts long country names to emoji flags

import sys
import flag
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


def run():
    # Check if missing arguments
    if len(sys.argv) <= 1:
        print(
            "usage: countryflag [<countryname_1] [<countryname_2>] [<countryname_n>] [...]"
        )
    else:
        countries = sys.argv[1:]
        flags = getflag(countries)
        print(flags)
    sys.exit()
