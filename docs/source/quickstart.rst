Quickstart Guide
===============

This quickstart guide will help you get up and running with CountryFlag quickly.

Installation
-----------

Install CountryFlag using pip:

.. code-block:: bash

   pip install countryflag

Basic Usage
----------

Converting Country Names to Flags
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The simplest way to use CountryFlag is to import the package and use the `getflag()` function:

.. code-block:: python

   import countryflag
   
   # Convert a list of country names to emoji flags
   flags = countryflag.getflag(['Germany', 'France', 'Italy'])
   print(flags)  # 🇩🇪 🇫🇷 🇮🇹
   
   # Use different separators
   flags = countryflag.getflag(['Germany', 'France', 'Italy'], separator='|')
   print(flags)  # 🇩🇪|🇫🇷|🇮🇹

The `getflag()` function accepts various country name formats:

.. code-block:: python

   # ISO-2 codes
   flags = countryflag.getflag(['DE', 'FR', 'IT'])
   print(flags)  # 🇩🇪 🇫🇷 🇮🇹
   
   # ISO-3 codes
   flags = countryflag.getflag(['DEU', 'FRA', 'ITA'])
   print(flags)  # 🇩🇪 🇫🇷 🇮🇹
   
   # Full names
   flags = countryflag.getflag(['Germany', 'France', 'Italy'])
   print(flags)  # 🇩🇪 🇫🇷 🇮🇹
   
   # Mixed formats
   flags = countryflag.getflag(['Germany', 'FR', 'ITA'])
   print(flags)  # 🇩🇪 🇫🇷 🇮🇹

Using the CountryFlag Class
~~~~~~~~~~~~~~~~~~~~~~~~~

For more advanced usage, you can use the `CountryFlag` class directly:

.. code-block:: python

   from countryflag.core import CountryFlag
   
   # Create a CountryFlag instance
   cf = CountryFlag()
   
   # Convert country names to flags
   flags, pairs = cf.get_flag(['Germany', 'France', 'Italy'])
   print(flags)  # 🇩🇪 🇫🇷 🇮🇹
   print(pairs)  # [('Germany', '🇩🇪'), ('France', '🇫🇷'), ('Italy', '🇮🇹')]
   
   # Format output as JSON
   json_output = cf.format_output(pairs, output_format='json')
   print(json_output)
   # [{"country": "Germany", "flag": "🇩🇪"}, {"country": "France", "flag": "🇫🇷"}, {"country": "Italy", "flag": "🇮🇹"}]

Reverse Lookup
~~~~~~~~~~~~

You can also convert flag emojis back to country names:

.. code-block:: python

   from countryflag.core import CountryFlag
   
   cf = CountryFlag()
   pairs = cf.reverse_lookup(['🇩🇪', '🇫🇷', '🇮🇹'])
   print(pairs)  # [('🇩🇪', 'Germany'), ('🇫🇷', 'France'), ('🇮🇹', 'Italy')]

Region-Based Lookup
~~~~~~~~~~~~~~~~

Get flags for all countries in a specific region:

.. code-block:: python

   from countryflag.core import CountryFlag
   
   cf = CountryFlag()
   
   # Get all European country flags
   flags, pairs = cf.get_flags_by_region('Europe')
   print(f"Found {len(pairs)} European countries")
   print(flags)  # All European country flags

Command Line Usage
----------------

CountryFlag can also be used from the command line:

.. code-block:: bash

   # Basic usage
   countryflag Germany France Italy
   
   # Custom separator
   countryflag --separator "|" Germany France Italy
   
   # JSON output
   countryflag --format json Germany France Italy
   
   # Reading from a file
   countryflag --file countries.txt
   
   # Get flags for a region
   countryflag --region Europe
   
   # Interactive mode
   countryflag --interactive

Common Use Cases
--------------

Handling Invalid Country Names
~~~~~~~~~~~~~~~~~~~~~~~~~~

Use fuzzy matching to handle slightly misspelled country names:

.. code-block:: python

   from countryflag.core import CountryFlag
   from countryflag.core.exceptions import InvalidCountryError
   
   cf = CountryFlag()
   
   try:
       flags, pairs = cf.get_flag(['Germny', 'Frnce', 'Itly'], fuzzy_matching=True)
       print(flags)  # 🇩🇪 🇫🇷 🇮🇹
   except InvalidCountryError as e:
       print(f"Error: {e}")

Caching for Performance
~~~~~~~~~~~~~~~~~~~~

Use caching to improve performance for repeated lookups:

.. code-block:: python

   from countryflag.core import CountryFlag
   from countryflag.cache import MemoryCache
   
   # Create a memory cache
   cache = MemoryCache()
   
   # Create a CountryFlag instance with caching
   cf = CountryFlag(cache=cache)
   
   # First lookup (cache miss)
   flags1, pairs1 = cf.get_flag(['Germany', 'France', 'Italy'])
   
   # Second lookup (cache hit - much faster)
   flags2, pairs2 = cf.get_flag(['Germany', 'France', 'Italy'])

For persistent caching, use DiskCache:

.. code-block:: python

   from countryflag.core import CountryFlag
   from countryflag.cache import DiskCache
   
   # Create a disk cache
   cache = DiskCache("/path/to/cache/dir")
   
   # Create a CountryFlag instance with disk caching
   cf = CountryFlag(cache=cache)

File Processing
~~~~~~~~~~~~

Process country names from a file:

.. code-block:: python

   from countryflag.utils.io import process_file_input
   from countryflag.core import CountryFlag
   
   # Read country names from a file
   countries = process_file_input("countries.txt")
   
   # Convert to flags
   cf = CountryFlag()
   flags, pairs = cf.get_flag(countries)
   print(flags)

For large files, use asynchronous processing:

.. code-block:: python

   import asyncio
   from countryflag.utils.io import process_file_input_async
   from countryflag.core import CountryFlag
   
   async def process_large_file():
       # Read country names from a file asynchronously
       countries = await process_file_input_async("large_file.txt")
       
       # Convert to flags
       cf = CountryFlag()
       flags, pairs = cf.get_flag(countries)
       print(flags)
   
   asyncio.run(process_large_file())

Best Practices
------------

1. **Reuse CountryFlag Instances**

   Create a single CountryFlag instance and reuse it:

   .. code-block:: python

      # Good
      cf = CountryFlag()
      flags1, _ = cf.get_flag(['Germany', 'France'])
      flags2, _ = cf.get_flag(['Italy', 'Spain'])
      
      # Bad (creates multiple instances)
      flags1, _ = CountryFlag().get_flag(['Germany', 'France'])
      flags2, _ = CountryFlag().get_flag(['Italy', 'Spain'])

2. **Use Caching for Repeated Lookups**

   Enable caching for improved performance:

   .. code-block:: python

      from countryflag.cache import MemoryCache
      
      cache = MemoryCache()
      cf = CountryFlag(cache=cache)

3. **Process in Batches**

   For large datasets, process in batches:

   .. code-block:: python

      def process_large_list(countries, batch_size=500):
          cf = CountryFlag()
          result_pairs = []
          
          for i in range(0, len(countries), batch_size):
              batch = countries[i:i+batch_size]
              _, pairs = cf.get_flag(batch)
              result_pairs.extend(pairs)
          
          return result_pairs

4. **Handle Errors Gracefully**

   Catch and handle exceptions:

   .. code-block:: python

      from countryflag.core.exceptions import InvalidCountryError
      
      try:
          flags, pairs = cf.get_flag(['Germany', 'InvalidCountry'])
      except InvalidCountryError as e:
          print(f"Error: {e}")
          # Handle the error or use fuzzy matching
          flags, pairs = cf.get_flag(['Germany'], fuzzy_matching=True)

5. **Use Proper Output Formats**

   Choose the appropriate output format for your needs:

   .. code-block:: python

      # For display to users
      text_output = cf.format_output(pairs, output_format='text')
      
      # For APIs
      json_output = cf.format_output(pairs, output_format='json')
      
      # For data processing
      csv_output = cf.format_output(pairs, output_format='csv')

Performance Tips
--------------

1. **Use Memory Caching for Speed**

   Memory caching offers the best performance:

   .. code-block:: python

      from countryflag.cache import MemoryCache
      
      cache = MemoryCache()
      cf = CountryFlag(cache=cache)

2. **Use Disk Caching for Persistence**

   Disk caching provides persistence across runs:

   .. code-block:: python

      from countryflag.cache import DiskCache
      
      cache = DiskCache("/path/to/cache/dir")
      cf = CountryFlag(cache=cache)

3. **Use Parallel Processing for Large Datasets**

   Process large datasets in parallel:

   .. code-block:: python

      import concurrent.futures
      
      def process_in_parallel(countries, num_workers=4):
          chunks = [countries[i:i+500] for i in range(0, len(countries), 500)]
          results = []
          
          with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
              futures = [executor.submit(process_chunk, chunk) for chunk in chunks]
              for future in concurrent.futures.as_completed(futures):
                  results.extend(future.result())
          
          return results
      
      def process_chunk(chunk):
          cf = CountryFlag()
          _, pairs = cf.get_flag(chunk)
          return pairs

4. **Remove Duplicates**

   Remove duplicate country names before processing:

   .. code-block:: python

      # Remove duplicates to avoid redundant processing
      unique_countries = list(set(countries))
      flags, pairs = cf.get_flag(unique_countries)

5. **Use Asynchronous Processing for I/O-Bound Operations**

   Use async/await for I/O-bound operations:

   .. code-block:: python

      import asyncio
      
      async def process_files(file_paths):
          from countryflag.utils.io import process_file_input_async
          
          tasks = [process_file_input_async(file_path) for file_path in file_paths]
          results = await asyncio.gather(*tasks)
          
          # Flatten the results
          countries = [country for sublist in results for country in sublist]
          
          return countries

Next Steps
---------

Now that you've got the basics, check out these guides for more advanced usage:

* :doc:`usage` - More detailed usage examples
* :doc:`api` - Complete API reference
* :doc:`caching` - Advanced caching strategies
* :doc:`plugins` - Creating custom plugins
* :doc:`performance` - Performance optimization techniques
