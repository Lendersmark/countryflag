Installation Guide
================

Basic Installation
----------------

The simplest way to install CountryFlag is via pip:

.. code-block:: bash

   pip install countryflag

This will install the latest stable version of the package along with all required dependencies.

Requirements
-----------

CountryFlag requires:

* Python 3.6 or newer
* emoji-country-flag
* country_converter
* typeguard
* prompt_toolkit
* aioconsole

Development Installation
----------------------

For development, you can install the package with additional dependencies:

.. code-block:: bash

   # Clone the repository
   git clone https://github.com/Lendersmark/countryflag.git
   cd countryflag

   # Create and activate a virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Install in development mode with extra dependencies
   pip install -e ".[dev]"

Docker Installation
-----------------

You can also run CountryFlag using Docker:

.. code-block:: bash

   # Build the image
   docker build -t countryflag-api -f deploy/Dockerfile .

   # Run the container
   docker run -p 8000:8000 countryflag-api

Verification
-----------

To verify your installation:

.. code-block:: bash

   # Check the version
   countryflag --version

   # Try a simple conversion
   countryflag "United States" Germany France

Next Steps
---------

After installation, you might want to:

* Read the :doc:`quickstart` guide
* Check the :doc:`usage` documentation
* Learn about :doc:`cli` usage
