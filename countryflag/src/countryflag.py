#!/usr/bin/env python3
# countryflag - Converts long country names to emoji flags

import sys
import flag
import country_converter as coco


def run():
    # Initializing variable
    country_flag = ""
    # Fetches long country name from argument
    if len(sys.argv) <= 1:
        print("countryflag: missing country name")
    else:
        for i in range(1, len(sys.argv)):
            # Takes the argument
            country_name = sys.argv[i]
            # Converts long country name to ISO2 code, if needed
            country_code = coco.convert(names=country_name, to="ISO2")
            # Returns emoji flags
            if i >= 2:
                # If more than a country, adds a space as separator
                country_flag += " "
            country_flag += flag.flag(country_code)
        print(country_flag)
    sys.exit()
