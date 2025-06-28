Migration Guide
===============
This guide will help you migrate between different versions of countryflag.

Migrating to v1.1.0 from v1.0.1
--------------------------------

**Cache Singleton Behavior (Breaking Change)**

Version 1.1.0 enhances the automatic cache sharing feature introduced in v1.0.1 across CountryFlag instances.

**What Changed:**

.. code-block:: python

   # Before v1.0.1
   cf1 = CountryFlag()  # No caching (cache=None)
   cf2 = CountryFlag()  # No caching (cache=None)
   
   # From v1.0.1 onwards (enhanced in v1.1.0)
   cf1 = CountryFlag()  # Automatic global cache sharing
   cf2 = CountryFlag()  # Same global cache as cf1

**Impact:**

- **Performance Improvement**: Instances now automatically benefit from shared caching
- **Memory Efficiency**: Single cache instance reduces memory usage
- **Thread Safety**: Enhanced with proper locking mechanisms
- **Backward Compatibility**: Existing code continues to work unchanged

**Migration Steps:**

1. **No code changes required** - existing applications will automatically benefit
2. **Test cache behavior** - if your tests depend on no caching, use ``CountryFlag.clear_global_cache()``
3. **Monitor performance** - expect significant improvements in repeated operations

**For Testing Code:**

.. code-block:: python

   import unittest
   from countryflag.core import CountryFlag
   
   class MyTest(unittest.TestCase):
       def setUp(self):
           # Clear global cache before each test
           CountryFlag.clear_global_cache()
       
       def test_something(self):
           cf = CountryFlag()
           # Test code here

**Disabling Global Cache (if needed):**

.. code-block:: python

   from countryflag.cache.base import NoOpCache
   
   # Create instance with no caching (pre-v1.0.1 behavior)
   cf = CountryFlag(cache=NoOpCache())

Migrating to v1.0.0 from v0.2.0
--------------------------------
Version 1.0.0 is primarily focused on production readiness and deployment features. Most API changes are additive.

Migrating to v0.2.0 from v0.1.x
--------------------------------

Overview of Changes
-------------------
Version 0.2.0 is a major update with significant improvements:

* Complete restructuring of the package architecture
* New caching system for improved performance
* Support for region-based lookups
* Enhanced command-line interface
* Many performance improvements and bug fixes

Breaking Changes
----------------
While we've tried to maintain backward compatibility, there are a few breaking changes:

1. The `getflag()` function now returns a tuple `(flags, pairs)` when used from the API.
   The first element is the flags string (same as before), and the second element is a list of (country, flag) pairs.

2. Some command-line arguments have changed or been added.

3. Error handling has been improved with specific exception types.

Updating Code
-------------
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
----------------------
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
-------------
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
--------------
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
----------------------
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
--------------------------
See the :doc:`performance` guide for detailed information on optimizing performance in v0.2.0.

Final Notes
-----------
If you encounter any issues migrating to v0.2.0, please report them on the
`GitHub issue tracker <https://github.com/Lendersmark/countryflag/issues>`_.
