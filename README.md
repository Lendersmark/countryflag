# countryflag

Countryflag is a Python package to convert country names into emoji flags.


[![image](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![image](https://img.shields.io/github/license/lendersmark/countryflag)](https://opensource.org/licenses/MIT)

## Motivation

I'm new to Python and to programming in general, and I have lots of things to learn, but instead of exercising on "Hello World"-like trivial examples I wanted to create a "real" project from the beginning.  
The idea was to build a simple command to get the correspondent emoji flag starting from a country name.


## Installation

Countryflag is registered at PyPI. From the command line:

    pip install countryflag --upgrade

Source code is also available on
[GitHub](https://github.com/lendersmark/countryflag).


## Usage

Countryflag accepts one or more country name(s) as command line arguments, separated by spaces.
Country names can be expressed in various classification schemes such as ISO-2, ISO-3, ISO-numeric, official name, etc.  
Countryflag uses [Country Converter (coco)](https://pypi.org/project/country-converter/) to convert country names to ISO-2 codes before returning emoji flags, so please see [Country Converter README.md](https://github.com/konstantinstadler/country_converter/blob/master/README.md#classification-schemes) for further details about supported classification schemes.

    countryflag Germany BE Spain 'United States of America'

The default output is a space separated list of emoji flags, one for each country.

## Compatible terminals

Some terminals, such as [iTerm2](https://iterm2.com/) on Mac Os, support Emoji Flags very well.

However, many others don't, such as Windows Terminal on Windows or Gnome Terminal on Linux: instead of the flag, they display country initials.  
At least on Windows, the reason seems to be political/PR-related, as explained [here](https://answers.microsoft.com/en-us/windows/forum/all/flag-emoji/85b163bc-786a-4918-9042-763ccf4b6c05).

Therefore, countryflag makes much more sense on systems that can properly render Emoji flags in terminal.

## Issues, bugs and enhancements

Please use the issue tracker for documenting bugs, proposing
enhancements and all other communication related to countryflag.

## Acknowledgements

This package depends on:

* [Country Converter (coco)](https://pypi.org/project/country-converter/) by [Konstantin Stadler](https://pypi.org/user/konstantinstadler/)
* [Emoji-country-flag](https://pypi.org/project/emoji-country-flag/) by [cuzi](https://pypi.org/user/cuzi/)
