Welcome to CountryFlag's documentation!
====================================

.. image:: https://img.shields.io/pypi/v/countryflag.svg
   :target: https://pypi.org/project/countryflag/
   :alt: PyPI version

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black
   :alt: Code style: black

.. image:: https://img.shields.io/github/license/lendersmark/countryflag
   :target: https://opensource.org/licenses/MIT
   :alt: MIT License

.. image:: https://img.shields.io/github/workflow/status/lendersmark/countryflag/CI
   :target: https://github.com/lendersmark/countryflag/actions
   :alt: Build Status

CountryFlag is a Python package for converting country names to emoji flags and vice versa.

Motivation
---------

The idea was to build a simple command to get the corresponding emoji flag starting from a country name.

Features
--------

* Convert country names to emoji flags
* Support for reverse lookup (flag to country name)
* Support for region/continent grouping
* Multiple output formats (text, JSON, CSV)
* Fuzzy matching for country names
* Interactive CLI mode with autocompletion
* Asynchronous and parallel processing
* Memory and disk caching for improved performance
* Thread-safe operations
* Comprehensive type hinting

Installation
-----------

.. code-block:: bash

   pip install countryflag

Quick Start
----------

.. code-block:: python

   import countryflag

   # Convert country names to emoji flags
   countries = ['Germany', 'BE', 'United States of America', 'Japan']
   flags = countryflag.getflag(countries)
   print(flags)  # 🇩🇪 🇧🇪 🇺🇸 🇯🇵

   # Command line usage
   # countryflag Germany BE Spain 'United States of America'

   # Using the core classes (advanced)
   from countryflag.core import CountryFlag
   from countryflag.cache import MemoryCache
   
   # Create a CountryFlag instance with caching
   cf = CountryFlag(cache=MemoryCache())
   
   # Convert country names to flags
   flags, pairs = cf.get_flag(['Germany', 'France', 'Italy'])
   print(flags)  # 🇩🇪 🇫🇷 🇮🇹
   
   # Output as JSON
   json_output = cf.format_output(pairs, output_format='json')
   print(json_output)

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   usage
   api
   plugins
   caching
   cli
   performance
   migration
   contributing
   changelog

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
