#!/usr/bin/env python3
"""
Example of integrating countryflag with a Flask web application.

This example demonstrates how to create a simple web application that
uses countryflag to convert country names to emoji flags.
"""

try:
    from flask import Flask, request, render_template_string, jsonify
except ImportError:
    print("This example requires Flask. Install it with 'pip install flask'.")
    import sys
    sys.exit(1)

from countryflag.core import CountryFlag
from countryflag.cache import MemoryCache


# Create a Flask application
app = Flask(__name__)

# Create a CountryFlag instance with caching
cache = MemoryCache()
cf = CountryFlag(cache=cache)


# HTML template for the web interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CountryFlag Web Demo</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        h1 {
            color: #333;
            border-bottom: 1px solid #ccc;
            padding-bottom: 10px;
        }
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        input[type="text"] {
            width: 100%;
            padding: 8px;
            border: 1px solid #ccc;
            border-radius: 4px;
        }
        button {
            background-color: #4CAF50;
            color: white;
            padding: 10px 15px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        button:hover {
            background-color: #45a049;
        }
        .result {
            margin-top: 20px;
            padding: 15px;
            border: 1px solid #ddd;
            border-radius: 4px;
            background-color: #f9f9f9;
        }
        .flags {
            font-size: 2em;
            margin-bottom: 10px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            padding: 8px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background-color: #f2f2f2;
        }
    </style>
</head>
<body>
    <h1>CountryFlag Web Demo</h1>
    
    <form id="flagForm" method="POST">
        <div class="form-group">
            <label for="countries">Enter Country Names (separated by commas):</label>
            <input type="text" id="countries" name="countries" value="{{ countries }}">
        </div>
        
        <div class="form-group">
            <label for="format">Output Format:</label>
            <select id="format" name="format">
                <option value="html" {% if format == 'html' %}selected{% endif %}>HTML</option>
                <option value="json" {% if format == 'json' %}selected{% endif %}>JSON</option>
                <option value="text" {% if format == 'text' %}selected{% endif %}>Text</option>
            </select>
        </div>
        
        <div class="form-group">
            <label for="fuzzy">
                <input type="checkbox" id="fuzzy" name="fuzzy" {% if fuzzy %}checked{% endif %}>
                Enable Fuzzy Matching
            </label>
        </div>
        
        <button type="submit">Convert</button>
    </form>
    
    {% if flags %}
    <div class="result">
        <h2>Results:</h2>
        
        <div class="flags">
            {{ flags }}
        </div>
        
        <table>
            <tr>
                <th>Country</th>
                <th>Flag</th>
            </tr>
            {% for country, flag in pairs %}
            <tr>
                <td>{{ country }}</td>
                <td>{{ flag }}</td>
            </tr>
            {% endfor %}
        </table>
    </div>
    {% endif %}
    
    <script>
        // Simple client-side validation
        document.getElementById('flagForm').addEventListener('submit', function(e) {
            const countries = document.getElementById('countries').value.trim();
            if (!countries) {
                alert('Please enter at least one country name');
                e.preventDefault();
            }
        });
    </script>
</body>
</html>
"""


@app.route('/', methods=['GET', 'POST'])
def index():
    """Handle the index page."""
    flags = ""
    pairs = []
    countries = ""
    format_type = "html"
    fuzzy = False
    
    if request.method == 'POST':
        # Get form data
        countries = request.form.get('countries', '')
        format_type = request.form.get('format', 'html')
        fuzzy = 'fuzzy' in request.form
        
        # Convert country names to a list
        country_list = [c.strip() for c in countries.split(',') if c.strip()]
        
        if country_list:
            try:
                # Convert country names to flags
                flags_text, pairs = cf.get_flag(country_list, fuzzy_matching=fuzzy)
                
                if format_type == 'json':
                    # Return JSON response
                    return jsonify({
                        'flags': flags_text,
                        'pairs': [{'country': country, 'flag': flag} for country, flag in pairs]
                    })
                
                flags = flags_text
                
            except Exception as e:
                # Handle errors
                flags = f"Error: {str(e)}"
    
    # Render the template
    return render_template_string(
        HTML_TEMPLATE,
        flags=flags,
        pairs=pairs,
        countries=countries,
        format=format_type,
        fuzzy=fuzzy
    )


@app.route('/api/countries')
def api_countries():
    """API endpoint to get a list of supported countries."""
    countries = cf.get_supported_countries()
    return jsonify([{
        'name': country['name'],
        'iso2': country['iso2'],
        'iso3': country['iso3']
    } for country in countries])


@app.route('/api/convert', methods=['POST'])
def api_convert():
    """API endpoint to convert country names to flags."""
    data = request.json or {}
    countries = data.get('countries', [])
    separator = data.get('separator', ' ')
    fuzzy = data.get('fuzzy', False)
    
    try:
        flags, pairs = cf.get_flag(countries, separator=separator, fuzzy_matching=fuzzy)
        return jsonify({
            'success': True,
            'flags': flags,
            'pairs': [{'country': country, 'flag': flag} for country, flag in pairs]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/regions')
def api_regions():
    """API endpoint to get a list of supported regions."""
    regions = cf._converter.get_supported_regions()
    return jsonify(regions)


@app.route('/api/region/<region>')
def api_region(region):
    """API endpoint to get flags for a specific region."""
    try:
        flags, pairs = cf.get_flags_by_region(region)
        return jsonify({
            'success': True,
            'region': region,
            'flags': flags,
            'pairs': [{'country': country, 'flag': flag} for country, flag in pairs]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


def run_app():
    """Run the Flask application."""
    app.run(debug=True)


if __name__ == '__main__':
    run_app()
