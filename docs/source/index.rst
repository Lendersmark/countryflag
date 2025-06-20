Welcome to CountryFlag's Documentation!
=======================================
.. image:: https://img.shields.io/pypi/v/countryflag.svg
   :target: https://pypi.org/project/countryflag/
   :alt: PyPI version

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black
   :alt: Code style: black

.. image:: https://img.shields.io/github/license/lendersmark/countryflag
   :target: https://opensource.org/licenses/MIT
   :alt: MIT License

CountryFlag is a Python package for converting country names to emoji flags and vice versa.

Motivation
----------
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

Installation
------------
.. code-block:: bash

   pip install countryflag

Quick Start
-----------
.. code-block:: python

   import countryflag

   # Convert country names to emoji flags
   countries = ['Germany', 'BE', 'United States of America', 'Japan']
   flags = countryflag.getflag(countries)
   print(flags)  # 🇩🇪 🇧🇪 🇺🇸 🇯🇵

   # Command line usage
   # countryflag Germany BE Spain 'United States of America'

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   usage
   quickstart
   cli
   plugins
   caching
   performance
   migration
   api
   contributing

Indices and tables
==================
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
