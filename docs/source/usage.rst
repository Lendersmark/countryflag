Usage
=====

Basic Usage
----------

CountryFlag provides several ways to convert country names to emoji flags.

Python API
~~~~~~~~~

Using CountryFlag within Python:

.. code-block:: python

   import countryflag
   
   # Basic usage
   countries = ['Germany', 'BE', 'United States of America', 'Japan']
   flags = countryflag.getflag(countries)
   print(flags)  # 🇩🇪 🇧🇪 🇺🇸 🇯🇵
   
   # Using the core classes
   from countryflag.core import CountryFlag
   
   cf = CountryFlag()
   flags, pairs = cf.get_flag(["United States", "Canada", "Mexico"])
   print(flags)  # 🇺🇸 🇨🇦 🇲🇽
   
   # Output in different formats
   json_output = cf.format_output(pairs, output_format="json")
   csv_output = cf.format_output(pairs, output_format="csv")
   
   # Reverse lookup (flag to country)
   reverse_pairs = cf.reverse_lookup(["🇺🇸", "🇨🇦", "🇲🇽"])
   for flag, country in reverse_pairs:
       print(f"{flag} is the flag of {country}")

Command Line Interface
~~~~~~~~~~~~~~~~~~~~~

CountryFlag can also be used from the command line:

.. code-block:: bash

   # Basic usage
   countryflag Germany BE Spain 'United States of America'
   
   # Output in different formats
   countryflag Germany BE Spain --format json
   countryflag Germany BE Spain --format csv
   
   # Using a custom separator
   countryflag Germany BE Spain --separator "|"
   
   # Using fuzzy matching
   countryflag Germny Belgim Span --fuzzy
   
   # Reverse lookup
   countryflag --reverse 🇺🇸 🇨🇦 🇲🇽
   
   # Interactive mode
   countryflag --interactive
   
   # Get flags for a region
   countryflag --region Europe
   
   # List all supported countries
   countryflag --list-countries
   
   # List all supported regions
   countryflag --list-regions
   
   # Validate a country name
   countryflag --validate "United States"

Advanced Features
----------------

Fuzzy Matching
~~~~~~~~~~~~~

CountryFlag supports fuzzy matching for country names:

.. code-block:: python

   from countryflag.core import CountryFlag
   
   cf = CountryFlag()
   flags, pairs = cf.get_flag(["Germny", "Belgim", "Span"], fuzzy_matching=True)
   print(flags)  # 🇩🇪 🇧🇪 🇪🇸

Region-Based Lookup
~~~~~~~~~~~~~~~~~~

You can get flags for all countries in a specific region:

.. code-block:: python

   from countryflag.core import CountryFlag
   
   cf = CountryFlag()
   flags, pairs = cf.get_flags_by_region("Europe")
   print(flags)  # All European country flags

Asynchronous Processing
~~~~~~~~~~~~~~~~~~~~~~

For large files, you can use asynchronous processing:

.. code-block:: python

   import asyncio
   from countryflag.utils import process_file_input_async
   from countryflag.core import CountryFlag
   
   async def main():
       country_names = await process_file_input_async("countries.txt")
       cf = CountryFlag()
       flags, pairs = cf.get_flag(country_names)
       print(flags)
   
   asyncio.run(main())

Parallel Processing
~~~~~~~~~~~~~~~~~~

For multiple files, you can use parallel processing:

.. code-block:: python

   from countryflag.utils import process_multiple_files
   from countryflag.core import CountryFlag
   
   country_names = process_multiple_files(["countries1.txt", "countries2.txt"])
   cf = CountryFlag()
   flags, pairs = cf.get_flag(country_names)
   print(flags)

Caching
~~~~~~~

To improve performance, you can use caching:

.. code-block:: python

   from countryflag.core import CountryFlag
   from countryflag.cache import DiskCache
   
   # Create a disk cache
   cache = DiskCache("/path/to/cache/dir")
   
   # Create a CountryFlag instance with caching
   cf = CountryFlag(cache=cache)
   
   # Subsequent calls will use the cache
   flags, pairs = cf.get_flag(["United States", "Canada", "Mexico"])
   print(flags)  # 🇺🇸 🇨🇦 🇲🇽

Plugins
~~~~~~~

You can extend CountryFlag with plugins:

.. code-block:: python

   from countryflag.core import CountryFlag
   from countryflag.plugins import register_plugin
   from countryflag.plugins.base import BasePlugin
   
   # Create a custom plugin
   class MyPlugin(BasePlugin):
       def get_country_info(self, name):
           # Custom implementation
           pass
   
   # Register the plugin
   register_plugin("my_plugin", MyPlugin())
   
   # Create a CountryFlag instance with the plugin
   cf = CountryFlag(plugin="my_plugin")
   
   # Use the plugin
   flags, pairs = cf.get_flag(["United States", "Canada", "Mexico"])
   print(flags)  # 🇺🇸 🇨🇦 🇲🇽
