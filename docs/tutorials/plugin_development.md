# Plugin Development Tutorial

This tutorial explains how to develop custom plugins for the CountryFlag package and integrate them with different frameworks.

## Overview of the Plugin System

The CountryFlag package includes a plugin system that allows you to extend its functionality in various ways. Plugins can provide:

- Custom country data sources
- Alternative flag rendering
- Integration with frameworks and databases
- Specialized functionality for specific use cases

## Creating a Custom Plugin

### 1. Understanding the BasePlugin Interface

All plugins must implement the `BasePlugin` abstract base class, which defines the following methods:

```python
class BasePlugin(ABC):
    @abstractmethod
    def get_country_info(self, name: str) -> Optional[CountryInfo]:
        """Get country information for a given country name."""
        pass

    @abstractmethod
    def get_supported_countries(self) -> List[CountryInfo]:
        """Get a list of supported countries."""
        pass

    @abstractmethod
    def get_supported_regions(self) -> List[str]:
        """Get a list of supported regions/continents."""
        pass

    @abstractmethod
    def get_countries_by_region(self, region: str) -> List[CountryInfo]:
        """Get countries in a specific region/continent."""
        pass

    @abstractmethod
    def convert_country_name(self, name: str, to_format: str) -> str:
        """Convert a country name to the specified format."""
        pass

    @abstractmethod
    def get_flag(self, country_name: str) -> Optional[str]:
        """Get the flag emoji for a country name."""
        pass

    @abstractmethod
    def reverse_lookup(self, flag_emoji: str) -> Optional[str]:
        """Get the country name for a flag emoji."""
        pass
```

### 2. Creating Your Plugin Class

Here's an example of a simple custom plugin that uses a local JSON file as a data source:

```python
import json
from typing import Dict, List, Optional
from pathlib import Path

from countryflag.plugins.base import BasePlugin
from countryflag.core.models import CountryInfo
from countryflag.core.exceptions import RegionError

class JsonFilePlugin(BasePlugin):
    """
    Plugin that uses a JSON file as a data source for country information.

    Expected JSON format:
    {
        "countries": [
            {
                "name": "United States",
                "iso2": "US",
                "iso3": "USA",
                "official_name": "United States of America",
                "region": "Americas",
                "subregion": "Northern America"
            },
            ...
        ]
    }
    """

    def __init__(self, json_file_path: str):
        """
        Initialize the plugin with a JSON file path.

        Args:
            json_file_path: Path to the JSON file containing country data.
        """
        self.file_path = Path(json_file_path)
        if not self.file_path.exists():
            raise FileNotFoundError(f"JSON file not found: {json_file_path}")

        # Load the data
        with open(self.file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Process and store the data
        self._countries: Dict[str, CountryInfo] = {}
        self._iso2_map: Dict[str, CountryInfo] = {}
        self._iso3_map: Dict[str, CountryInfo] = {}
        self._flag_map: Dict[str, CountryInfo] = {}
        self._region_map: Dict[str, List[CountryInfo]] = {}

        import flag  # For generating flag emojis

        for country_data in data["countries"]:
            country_info = CountryInfo(
                name=country_data["name"],
                iso2=country_data["iso2"],
                iso3=country_data["iso3"],
                official_name=country_data["official_name"],
                region=country_data.get("region", ""),
                subregion=country_data.get("subregion", ""),
                flag=flag.flag(country_data["iso2"])
            )

            # Add to our maps for easy lookup
            self._countries[country_data["name"].lower()] = country_info
            self._iso2_map[country_data["iso2"]] = country_info
            self._iso3_map[country_data["iso3"]] = country_info
            self._flag_map[country_info.flag] = country_info

            # Add to region map
            region = country_data.get("region", "")
            if region:
                if region not in self._region_map:
                    self._region_map[region] = []
                self._region_map[region].append(country_info)

    def get_country_info(self, name: str) -> Optional[CountryInfo]:
        # Try as a name
        if name.lower() in self._countries:
            return self._countries[name.lower()]

        # Try as ISO2
        if name.upper() in self._iso2_map:
            return self._iso2_map[name.upper()]

        # Try as ISO3
        if name.upper() in self._iso3_map:
            return self._iso3_map[name.upper()]

        return None

    def get_supported_countries(self) -> List[CountryInfo]:
        return list(self._countries.values())

    def get_supported_regions(self) -> List[str]:
        return list(self._region_map.keys())

    def get_countries_by_region(self, region: str) -> List[CountryInfo]:
        if region not in self._region_map:
            raise RegionError(f"Unsupported region: {region}", region)
        return self._region_map[region]

    def convert_country_name(self, name: str, to_format: str) -> str:
        country = self.get_country_info(name)
        if not country:
            return "not found"

        if to_format.upper() == "ISO2":
            return country.iso2
        elif to_format.upper() == "ISO3":
            return country.iso3
        elif to_format.upper() == "NAME":
            return country.name
        else:
            return "not found"

    def get_flag(self, country_name: str) -> Optional[str]:
        country = self.get_country_info(country_name)
        return country.flag if country else None

    def reverse_lookup(self, flag_emoji: str) -> Optional[str]:
        return self._flag_map[flag_emoji].name if flag_emoji in self._flag_map else None
```

### 3. Registering Your Plugin

Once you've created your plugin, you need to register it with the CountryFlag plugin registry:

```python
from countryflag.plugins import register_plugin
from mypackage.plugins import JsonFilePlugin

# Create your plugin instance
my_plugin = JsonFilePlugin("/path/to/my_countries.json")

# Register it with a unique name
register_plugin("json_file_plugin", my_plugin)
```

### 4. Using Your Plugin

After registering your plugin, you can retrieve it using the `get_plugin` function:

```python
from countryflag.plugins import get_plugin

# Get your plugin
plugin = get_plugin("json_file_plugin")

# Use the plugin
country_info = plugin.get_country_info("United States")
print(f"Country: {country_info.name}, Flag: {country_info.flag}")
```

## Framework Integration Examples

### Django Integration

Here's how to integrate CountryFlag with Django:

```python
# myapp/plugins.py
from django.conf import settings
from countryflag.plugins.base import BasePlugin
from countryflag.core.models import CountryInfo
from countryflag.plugins import register_plugin
from myapp.models import Country

class DjangoModelPlugin(BasePlugin):
    """Plugin that uses Django models as the data source."""

    def get_country_info(self, name: str) -> Optional[CountryInfo]:
        try:
            # Try to find by name, ISO2, or ISO3
            country = Country.objects.filter(
                models.Q(name__iexact=name) |
                models.Q(iso2__iexact=name) |
                models.Q(iso3__iexact=name)
            ).first()

            if not country:
                return None

            return CountryInfo(
                name=country.name,
                iso2=country.iso2,
                iso3=country.iso3,
                official_name=country.official_name,
                region=country.region,
                subregion=country.subregion,
                flag=flag.flag(country.iso2)
            )
        except Exception:
            return None

    # Implement other required methods...

# Register the plugin when Django starts
def register_django_plugin():
    plugin = DjangoModelPlugin()
    register_plugin("django_model", plugin)

# In your Django AppConfig's ready() method
from django.apps import AppConfig

class MyAppConfig(AppConfig):
    name = 'myapp'

    def ready(self):
        from myapp.plugins import register_django_plugin
        register_django_plugin()
```

### Flask Integration

Here's how to integrate with Flask:

```python
from flask import Flask, request, jsonify
from countryflag.core.flag import CountryFlag
from countryflag.plugins import get_plugin, register_plugin
from mypackage.plugins import JsonFilePlugin

app = Flask(__name__)

# Register plugin at startup
my_plugin = JsonFilePlugin("countries.json")
register_plugin("flask_json", my_plugin)

@app.route('/api/country/<name>')
def get_country(name):
    plugin = get_plugin("flask_json")
    country_info = plugin.get_country_info(name)

    if not country_info:
        return jsonify({"error": "Country not found"}), 404

    return jsonify({
        "name": country_info.name,
        "iso2": country_info.iso2,
        "iso3": country_info.iso3,
        "flag": country_info.flag,
        "region": country_info.region
    })

@app.route('/api/flags', methods=['POST'])
def get_flags():
    data = request.get_json()
    countries = data.get('countries', [])

    cf = CountryFlag()
    flags, pairs = cf.get_flag(countries)

    return jsonify({
        "flags": flags,
        "pairs": [{"country": c, "flag": f} for c, f in pairs]
    })

if __name__ == '__main__':
    app.run(debug=True)
```

### FastAPI Integration

Here's how to integrate with FastAPI:

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from countryflag.core.flag import CountryFlag
from countryflag.plugins import get_plugin, register_plugin
from mypackage.plugins import JsonFilePlugin

app = FastAPI()

# Register plugin at startup
my_plugin = JsonFilePlugin("countries.json")
register_plugin("fastapi_json", my_plugin)

class CountryRequest(BaseModel):
    countries: List[str]

class CountryResponse(BaseModel):
    name: str
    iso2: str
    iso3: str
    flag: str
    region: str

@app.get('/api/country/{name}', response_model=CountryResponse)
def get_country(name: str):
    plugin = get_plugin("fastapi_json")
    country_info = plugin.get_country_info(name)

    if not country_info:
        raise HTTPException(status_code=404, detail="Country not found")

    return CountryResponse(
        name=country_info.name,
        iso2=country_info.iso2,
        iso3=country_info.iso3,
        flag=country_info.flag,
        region=country_info.region
    )

@app.post('/api/flags')
def get_flags(request: CountryRequest):
    cf = CountryFlag()
    flags, pairs = cf.get_flag(request.countries)

    return {
        "flags": flags,
        "pairs": [{"country": c, "flag": f} for c, f in pairs]
    }
```

## Large-Scale Usage Techniques

### 1. Caching Strategies

CountryFlag supports caching to improve performance in high-traffic scenarios:

```python
from countryflag.core.flag import CountryFlag
from countryflag.cache.memory import MemoryCache
from countryflag.cache.redis import RedisCache

# Use memory cache for small applications
memory_cache = MemoryCache(max_size=1000)
cf_memory = CountryFlag(cache=memory_cache)

# Use Redis cache for distributed applications
redis_cache = RedisCache(host='localhost', port=6379, db=0)
cf_redis = CountryFlag(cache=redis_cache)
```

### 2. Batch Processing

For processing large datasets, use batch processing techniques:

```python
import pandas as pd
from countryflag.core.flag import CountryFlag

# Process a CSV file with country data
def add_flags_to_dataframe(file_path, country_column, output_path):
    # Load data in chunks to save memory
    cf = CountryFlag()
    chunk_size = 10000

    for chunk in pd.read_csv(file_path, chunksize=chunk_size):
        # Get country names from the dataframe
        countries = chunk[country_column].tolist()

        # Process in smaller batches for better performance
        batch_size = 100
        for i in range(0, len(countries), batch_size):
            batch = countries[i:i+batch_size]
            _, pairs = cf.get_flag(batch)

            # Create a mapping of country to flag
            flag_map = {country: flag for country, flag in pairs}

            # Add flags to the chunk
            chunk['flag'] = chunk[country_column].map(flag_map)

        # Append to output file
        mode = 'a' if i > 0 else 'w'
        header = False if i > 0 else True
        chunk.to_csv(output_path, mode=mode, header=header, index=False)
```

### 3. Asynchronous Processing

For web applications, use asynchronous processing to avoid blocking:

```python
import asyncio
from countryflag.core.flag import CountryFlag

async def process_countries_async(countries):
    loop = asyncio.get_event_loop()
    cf = CountryFlag()

    # Run the potentially slow operation in a thread pool
    flags, pairs = await loop.run_in_executor(
        None, lambda: cf.get_flag(countries)
    )

    return flags, pairs

# In an async web framework like FastAPI
@app.post('/api/flags')
async def get_flags(request: CountryRequest):
    flags, pairs = await process_countries_async(request.countries)

    return {
        "flags": flags,
        "pairs": [{"country": c, "flag": f} for c, f in pairs]
    }
```

### 4. Distributed Processing

For extremely large datasets, use distributed processing with tools like Celery:

```python
# tasks.py
from celery import Celery
from countryflag.core.flag import CountryFlag

app = Celery('tasks', broker='redis://localhost:6379/0')

@app.task
def process_country_batch(countries):
    cf = CountryFlag()
    flags, pairs = cf.get_flag(countries)
    return [{"country": c, "flag": f} for c, f in pairs]

# Usage
from tasks import process_country_batch

def process_large_country_list(countries, batch_size=100):
    results = []

    # Split into batches and process in parallel
    for i in range(0, len(countries), batch_size):
        batch = countries[i:i+batch_size]
        results.append(process_country_batch.delay(batch))

    # Collect results
    processed = []
    for result in results:
        processed.extend(result.get())

    return processed
```

## Best Practices

1. **Use the plugin system for extensibility**: Implement the BasePlugin interface to add custom data sources or functionality.

2. **Implement caching**: Use the built-in caching mechanisms or implement your own for improved performance.

3. **Handle errors gracefully**: Catch and handle exceptions, provide meaningful error messages, and use fallback mechanisms when possible.

4. **Validate input data**: Always validate country names and other inputs before processing.

5. **Optimize for your use case**: Choose the appropriate processing strategy (batch, async, distributed) based on your specific requirements.

6. **Consider internationalization**: Use the language parameter to support multiple languages where applicable.

7. **Monitor performance**: Keep track of processing times and resource usage, especially in production environments.

8. **Keep data up-to-date**: Regularly update your country data to reflect geopolitical changes.

## Conclusion

The CountryFlag package provides a flexible plugin system that allows you to extend its functionality and integrate with various frameworks. By following this tutorial, you should be able to create custom plugins, integrate with popular web frameworks, and implement efficient processing strategies for large-scale applications.

For more information, refer to the API documentation and example code in the repository.
