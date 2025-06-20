Command Line Interface
======================
CountryFlag provides a powerful command-line interface for converting country names to emoji flags.

Basic Usage
-----------
Converting Country Names
~~~~~~~~~~~~~~~~~~~~~~~~
Convert one or more country names to flags:

.. code-block:: bash

   # Basic usage
   countryflag Germany France Italy

   # Using ISO codes
   countryflag DE FR IT

   # Mixed formats
   countryflag "United States" DE France

Options and Flags
-----------------
Format Options
~~~~~~~~~~~~~~
Specify output format:

.. code-block:: bash

   # JSON output
   countryflag --format json Germany France Italy

   # CSV output
   countryflag --format csv Germany France Italy

   # Custom separator
   countryflag --separator "|" Germany France Italy

Fuzzy Matching
~~~~~~~~~~~~~~
Enable fuzzy matching for misspelled country names:

.. code-block:: bash

   # Enable fuzzy matching
   countryflag --fuzzy Germny Frnace Itly

   # Adjust fuzzy matching threshold
   countryflag --fuzzy --threshold 0.8 Germny Frnace Itly

Region-Based Lookup
~~~~~~~~~~~~~~~~~~~
Get flags for all countries in a region:

.. code-block:: bash

   # Get European country flags
   countryflag --region Europe

   # Get Asian country flags
   countryflag --region Asia

File Processing
~~~~~~~~~~~~~~~
Process country names from files:

.. code-block:: bash

   # Process a single file
   countryflag --file countries.txt

   # Process multiple files in parallel
   countryflag --files file1.txt file2.txt file3.txt

   # Specify number of worker threads
   countryflag --files file1.txt file2.txt --workers 4

Interactive Mode
~~~~~~~~~~~~~~~~
Run in interactive mode with autocompletion:

.. code-block:: bash

   countryflag --interactive

Utility Commands
~~~~~~~~~~~~~~~~
Various utility commands:

.. code-block:: bash

   # List all supported countries
   countryflag --list-countries

   # List all supported regions
   countryflag --list-regions

   # Validate a country name
   countryflag --validate "United States"

   # Show version
   countryflag --version

   # Show help
   countryflag --help

Advanced Usage
--------------
Caching
~~~~~~~
Enable caching for better performance:

.. code-block:: bash

   # Use memory cache
   countryflag --cache memory Germany France Italy

   # Use disk cache
   countryflag --cache disk --cache-dir /path/to/cache Germany France Italy

Asynchronous Processing
~~~~~~~~~~~~~~~~~~~~~~~
Use async processing for large files:

.. code-block:: bash

   # Enable async processing
   countryflag --async --file large_file.txt

Environment Variables
---------------------
The CLI supports several environment variables:

* ``COUNTRYFLAG_CACHE_DIR``: Default cache directory
* ``COUNTRYFLAG_LOG_LEVEL``: Logging level (DEBUG, INFO, WARNING, ERROR)
* ``COUNTRYFLAG_DEFAULT_FORMAT``: Default output format
* ``COUNTRYFLAG_LANGUAGE``: Language for country names

Exit Codes
----------
The CLI uses the following exit codes:

* ``0``: Success
* ``1``: General error
* ``2``: Invalid arguments
* ``3``: Invalid country name
* ``4``: File error
* ``5``: Cache error

Examples
--------
1. Basic conversion with custom format:

   .. code-block:: bash

      countryflag --format json "United States" Canada Mexico

2. Process a file with fuzzy matching:

   .. code-block:: bash

      countryflag --file countries.txt --fuzzy --format csv

3. Get European flags with custom separator:

   .. code-block:: bash

      countryflag --region Europe --separator " | " --format text

4. Interactive mode with custom cache:

   .. code-block:: bash

      countryflag --interactive --cache disk --cache-dir ~/.cache/countryflag

Error Handling
--------------
The CLI provides detailed error messages:

.. code-block:: bash

   # Invalid country
   $ countryflag InvalidCountry
   Error: Country not found: InvalidCountry

   # Invalid region
   $ countryflag --region InvalidRegion
   Error: Unsupported region: InvalidRegion

   # File not found
   $ countryflag --file nonexistent.txt
   Error: File not found: nonexistent.txt

Best Practices
--------------
1. Use appropriate output formats for different use cases
2. Enable caching for repeated operations
3. Use fuzzy matching when processing user input
4. Consider async processing for large files
5. Monitor cache usage and performance

For more information, see the :doc:`usage` guide.
