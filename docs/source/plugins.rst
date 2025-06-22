Plugin System
=============
The CountryFlag package includes a flexible plugin system that allows you to extend its functionality.

Overview
--------
The plugin system allows you to:

* Add custom data sources for country information
* Implement custom caching mechanisms
* Add new output formats
* Customize flag rendering

Creating a Plugin
-----------------
To create a plugin, you need to implement the BasePlugin interface:

.. code-block:: python

   from countryflag.plugins.base import BasePlugin
   from countryflag.core.models import CountryInfo
   from typing import List, Optional

   class CustomPlugin(BasePlugin):
       def get_country_info(self, name: str) -> Optional[CountryInfo]:
           """Get country information for a given country name."""
           # Implementation here
           pass

       def get_supported_countries(self) -> List[CountryInfo]:
           """Get a list of supported countries."""
           # Implementation here
           pass

       def get_supported_regions(self) -> List[str]:
           """Get a list of supported regions/continents."""
           # Implementation here
           pass

       def get_countries_by_region(self, region: str) -> List[CountryInfo]:
           """Get countries in a specific region/continent."""
           # Implementation here
           pass

Example Plugins
---------------
Custom Data Source
~~~~~~~~~~~~~~~~~~
Here\'s an example of a plugin that uses a JSON file as a data source:

.. literalinclude:: ../../examples/plugins/custom_data_source_plugin.py
   :language: python
   :linenos:
   :caption: custom_data_source_plugin.py

Custom Cache
~~~~~~~~~~~~
Example of a Redis-based cache plugin:

.. literalinclude:: ../../examples/plugins/custom_cache_plugin.py
   :language: python
   :linenos:
   :caption: custom_cache_plugin.py

Custom Output Format
~~~~~~~~~~~~~~~~~~~~
Example of a plugin that adds HTML and XML output formats:

.. literalinclude:: ../../examples/plugins/custom_output_format_plugin.py
   :language: python
   :linenos:
   :caption: custom_output_format_plugin.py

Using Plugins
-------------
To use a plugin:

.. code-block:: python

   from countryflag.plugins import register_plugin
   from countryflag.core import CountryFlag
   from my_plugin import CustomPlugin

   # Create and register the plugin
   plugin = CustomPlugin()
   register_plugin("custom_plugin", plugin)

   # Use the plugin
   cf = CountryFlag()
   flags = cf.get_flag(["United States", "Canada"])

Plugin API Reference
--------------------
.. autoclass:: countryflag.plugins.base.BasePlugin
   :members:
   :undoc-members:
   :show-inheritance:

Best Practices
--------------
1. **Error Handling**: Always implement proper error handling in your plugins
2. **Performance**: Consider caching results for better performance
3. **Documentation**: Document your plugin\'s behavior and requirements
4. **Testing**: Write comprehensive tests for your plugin
