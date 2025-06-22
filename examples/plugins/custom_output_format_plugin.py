#!/usr/bin/env python3
"""
Example of a custom output format plugin for countryflag.

This plugin adds support for HTML and XML output formats.
"""

import xml.dom.minidom
import xml.etree.ElementTree as ET
from typing import Any, Callable, Dict, List, Tuple

from countryflag.core import CountryFlag


class OutputFormatPlugin:
    """
    Plugin for custom output formats.

    This class adds support for HTML and XML output formats.
    """

    def __init__(self):
        """Initialize the plugin."""
        self._original_format_output = None

    def _format_as_html(self, pairs: List[Tuple[str, str]]) -> str:
        """
        Format the output as HTML.

        Args:
            pairs: A list of (country, flag) pairs.

        Returns:
            str: The HTML output.
        """
        html = [
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            '    <meta charset="UTF-8">',
            "    <title>Country Flags</title>",
            "    <style>",
            "        table { border-collapse: collapse; width: 100%; }",
            "        th, td { text-align: left; padding: 8px; }",
            "        tr:nth-child(even) { background-color: #f2f2f2; }",
            "        th { background-color: #4CAF50; color: white; }",
            "    </style>",
            "</head>",
            "<body>",
            "    <h1>Country Flags</h1>",
            "    <table>",
            "        <tr>",
            "            <th>Country</th>",
            "            <th>Flag</th>",
            "        </tr>",
        ]

        for country, flag in pairs:
            html.append(f"        <tr>")
            html.append(f"            <td>{country}</td>")
            html.append(f"            <td>{flag}</td>")
            html.append(f"        </tr>")

        html.extend(["    </table>", "</body>", "</html>"])

        return "\n".join(html)

    def _format_as_xml(self, pairs: List[Tuple[str, str]]) -> str:
        """
        Format the output as XML.

        Args:
            pairs: A list of (country, flag) pairs.

        Returns:
            str: The XML output.
        """
        root = ET.Element("countries")

        for country, flag in pairs:
            country_elem = ET.SubElement(root, "country")
            name_elem = ET.SubElement(country_elem, "name")
            name_elem.text = country
            flag_elem = ET.SubElement(country_elem, "flag")
            flag_elem.text = flag

        # Convert to string with pretty formatting
        xml_str = ET.tostring(root, encoding="unicode")
        dom = xml.dom.minidom.parseString(xml_str)
        return dom.toprettyxml(indent="    ")

    def patch_format_output(self, country_flag: CountryFlag) -> None:
        """
        Patch the format_output method of CountryFlag to add support for HTML and XML.

        Args:
            country_flag: The CountryFlag instance to patch.
        """
        # Save the original method
        self._original_format_output = country_flag.format_output

        # Define the new method
        def new_format_output(
            pairs: List[Tuple[str, str]],
            output_format: str = "text",
            separator: str = " ",
        ) -> str:
            if output_format == "html":
                return self._format_as_html(pairs)
            elif output_format == "xml":
                return self._format_as_xml(pairs)
            else:
                # Call the original method
                return self._original_format_output(pairs, output_format, separator)

        # Replace the method
        country_flag.format_output = new_format_output.__get__(
            country_flag, CountryFlag
        )

    def restore_format_output(self, country_flag: CountryFlag) -> None:
        """
        Restore the original format_output method.

        Args:
            country_flag: The CountryFlag instance to restore.
        """
        if self._original_format_output:
            country_flag.format_output = self._original_format_output


def example_usage():
    """Example usage of the output format plugin."""
    # Create the CountryFlag instance
    from countryflag.core import CountryFlag

    cf = CountryFlag()

    # Create and apply the plugin
    plugin = OutputFormatPlugin()
    plugin.patch_format_output(cf)

    # Convert some country names to flags
    _, pairs = cf.get_flag(["United States", "Canada", "Germany"])

    # Format the output in different formats
    html_output = cf.format_output(pairs, output_format="html")
    xml_output = cf.format_output(pairs, output_format="xml")

    # Print results
    print("HTML Output:")
    print(html_output[:500] + "...\n")  # Show first 500 chars

    print("XML Output:")
    print(xml_output)

    # Restore the original method
    plugin.restore_format_output(cf)


if __name__ == "__main__":
    example_usage()
