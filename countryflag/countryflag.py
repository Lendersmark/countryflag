#!/usr/bin/env python3
# countryflag - Converts long country names to emoji flags

import sys
import flag
import country_converter as coco

def run():
    # Initializing variable
    countryFlag=''
    # Fetches long country name from argument
    if len(sys.argv) <= 1:
        print ('countryflag: missing country name')
        return
    else:
        for i in range(1, len(sys.argv)): 
            # Takes the argument
            countryName = sys.argv[i]
            # Converts long country name to ISO2 code, if needed
            countryCode = coco.convert(names=countryName, to='ISO2')
            # Returns the emoji flag
            countryFlag += " "
            countryFlag += (flag.flag(countryCode))
        return countryFlag
