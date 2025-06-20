Migration Guide
==============

This guide will help you migrate from countryflag v0.1.x to v0.2.0.

Overview of Changes
-----------------

Version 0.2.0 is a major update with significant improvements:

* Complete restructuring of the package architecture
* New caching system for improved performance
* Support for region-based lookups
* Enhanced command-line interface
* Many performance improvements and bug fixes

Breaking Changes
--------------

While we've tried to maintain backward compatibility, there are a few breaking changes:

1. The `getflag()` function now returns a tuple `(flags, pairs)` when used from the API. 
   The first element is the flags string (same as before), and the second element is a list of (country, flag) pairs.

2. Some command-line arguments have changed or been added.

3. Error handling has been improved with specific exception types.

Updating Code
-----------

Basic usage remains compatible:

.. code-block:: python

   # Old code (still works)
   import countryflag
   flags = countryflag.getflag(['Germany', 'France', 'Italy'])
   print(flags)  # 🇩🇪 🇫🇷 🇮🇹

   # New code with additional features
   import countryflag
   flags, pairs = countryflag.getflag(['Germany', 'France', 'Italy'])
   print(flags)  # 🇩🇪 🇫🇷 🇮🇹
   print(pairs)  # [('Germany', '🇩🇪'), ('France', '🇫🇷'), ('Italy', '🇮🇹')]

Using the Enhanced API
--------------------

The new version provides a more powerful API through the `CountryFlag` class:

.. code-block:: python

   from countryflag.core import CountryFlag
   
   # Create a CountryFlag instance
   cf = CountryFlag()
   
   # Convert country names to flags
   flags, pairs = cf.get_flag(['Germany', 'France', 'Italy'])
   
   # Format output in different formats
   json_output = cf.format_output(pairs, output_format='json')
   csv_output = cf.format_output(pairs, output_format='csv')
   
   # Reverse lookup (flag to country)
   flag_country_pairs = cf.reverse_lookup(['🇩🇪', '🇫🇷', '🇮🇹'])
   
   # Get flags for all countries in a region
   europe_flags, europe_pairs = cf.get_flags_by_region('Europe')

Using Caching
-----------

One of the biggest performance improvements in v0.2.0 is the caching system:

.. code-block:: python

   from countryflag.core import CountryFlag
   from countryflag.cache import MemoryCache, DiskCache
   
   # In-memory caching
   memory_cache = MemoryCache()
   cf = CountryFlag(cache=memory_cache)
   
   # Persistent disk caching
   disk_cache = DiskCache('/path/to/cache/dir')
   cf = CountryFlag(cache=disk_cache)
   
   # Subsequent calls with the same inputs will be much faster
   flags, pairs = cf.get_flag(['Germany', 'France', 'Italy'])

Error Handling
------------

The new version uses custom exceptions for better error handling:

.. code-block:: python

   from countryflag.core import CountryFlag
   from countryflag.core.exceptions import InvalidCountryError, ReverseConversionError
   
   cf = CountryFlag()
   
   try:
       flags, pairs = cf.get_flag(['Germany', 'Invalid Country'])
   except InvalidCountryError as e:
       print(f"Error: {e}")
       print(f"Invalid country: {e.country}")

Command Line Interface
-------------------

The command-line interface has been enhanced with many new options:

.. code-block:: bash

   # Basic usage (unchanged)
   countryflag Germany France Italy
   
   # New options
   countryflag --format json Germany France Italy  # Output as JSON
   countryflag --separator "|" Germany France Italy  # Custom separator
   countryflag --fuzzy Germny Frnce Itly  # Fuzzy matching
   countryflag --region Europe  # Get all European country flags
   countryflag --interactive  # Interactive mode with autocompletion
   countryflag --reverse 🇩🇪 🇫🇷 🇮🇹  # Reverse lookup
   countryflag --file countries.txt  # Read from file
   countryflag --cache  # Enable caching

Performance Considerations
-----------------------

See the :doc:`performance` guide for detailed information on optimizing performance in v0.2.0.

Final Notes
---------

If you encounter any issues migrating to v0.2.0, please report them on the 
`GitHub issue tracker <https://github.com/Lendersmark/countryflag/issues>`_.
