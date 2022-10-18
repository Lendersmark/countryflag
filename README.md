# countryflag

Countryflag is a Python package to convert country names into emoji flags.


![PyPI](https://img.shields.io/pypi/v/countryflag)
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

### Use within Python

Convert various country names to emojy flags:

    import countryflag
    countries = ['Germany', 'BE', 'United States of America', 'Japan']
    flags = countryflag.getflag(countries)
    print(flags)

The default output is a space separated list of emoji flags, one for each country:

🇩🇪 🇧🇪 🇺🇸 🇯🇵

### Command line usage

Countryflag can also be used as a command line tool, specifying one or more country name(s) as command line arguments, separated by spaces.

    countryflag Germany BE Spain 'United States of America'

Will result in:

🇩🇪 🇧🇪 🇪🇸 🇺🇸

### Country names formats

Country names can be expressed in various classification schemes such as ISO-2, ISO-3, ISO-numeric, official name, etc.
The input format is determined automatically, based on ISO two letter, ISO three letter, ISO numeric or regular expression matching.
Countryflag uses [Country Converter (coco)](https://pypi.org/project/country-converter/) to convert country names to ISO-2 codes and then [Emoji-country-flag](https://pypi.org/project/emoji-country-flag/) to render the emoji flags: please see their documentation for further details.


## How it works

All the flag emoji are actually composed of two unicode letters. These are the 26 regional indicator symbols:

🇦 🇧 🇨 🇩 🇪 🇫 🇬 🇭 🇮 🇯 🇰 🇱 🇲 🇳 🇴 🇵 🇶 🇷 🇸 🇹 🇺 🇻 🇼 🇽 🇾 🇿

According to ISO 3166, pairing unicode letters of the country code, compatible browsers/phones/terminals will display the correspondent Emoji flag.
For example BE is Belgium: 🇧 + 🇪 = 🇧🇪

So, to encode an ASCII code like :BE: to 🇧🇪, Countrycode converts country names to the corresponding regional indicator symbols.


## Compatible terminals

Some terminals, such as [iTerm2](https://iterm2.com/) on Mac Os, support Emoji country flags very well.

However, many others don't, such as Windows Terminal on Windows or Gnome Terminal on Linux: instead of the flag, they will display unicode letters.  
For example, invoking `countryflag belgium` into Windows Terminal will return 🇧 🇪 as output, instead of the emojy country flag 🇧🇪.

At least on Windows, the reason seems to be political/PR-related, as explained [here](https://answers.microsoft.com/en-us/windows/forum/all/flag-emoji/85b163bc-786a-4918-9042-763ccf4b6c05).

Therefore, Countryflag makes much more sense when used on systems/terminals that can properly render Emoji country flags.

## Issues, bugs and enhancements

Please use the issue tracker for documenting bugs, proposing
enhancements and all other communication related to countryflag.

## Acknowledgements

This package depends on:

* [Country Converter (coco)](https://pypi.org/project/country-converter/) by [Konstantin Stadler](https://pypi.org/user/konstantinstadler/)
* [Emoji-country-flag](https://pypi.org/project/emoji-country-flag/) by [cuzi](https://pypi.org/user/cuzi/)
