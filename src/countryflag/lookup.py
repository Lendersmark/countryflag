"""
Robust reverse-lookup functionality for flag emojis.

This module provides enhanced reverse lookup capabilities that handle
regional-indicator sequences for territories like United Kingdom (🇬🇧),
Ascension Island (🇦🇨), and other special cases.
"""

import logging
import re
import unicodedata
from typing import Dict, List, Optional, Set, Tuple

import flag

# Configure logging
logger = logging.getLogger("countryflag.lookup")

# Regional indicator Unicode range (U+1F1E6 to U+1F1FF)
REGIONAL_INDICATOR_START = 0x1F1E6
REGIONAL_INDICATOR_END = 0x1F1FF


def normalize_emoji_flag(emoji_flag: str) -> str:
    """
    Normalize a flag emoji to ensure consistent representation.

    This function handles various input formats and normalizes them to
    standard regional indicator sequences.

    Args:
        emoji_flag: The flag emoji string to normalize.

    Returns:
        str: The normalized flag emoji.

    Example:
        >>> normalize_emoji_flag("🇬🇧")
        '🇬🇧'
        >>> normalize_emoji_flag("🇺🇰")
        '🇺🇰'
    """
    if not emoji_flag or not isinstance(emoji_flag, str):
        return emoji_flag

    # Remove leading/trailing whitespace
    emoji_flag = emoji_flag.strip()

    # Ensure the emoji consists of exactly 2 regional indicator symbols
    chars = list(emoji_flag)
    if len(chars) == 2:
        # Check if both characters are regional indicators
        if all(
            REGIONAL_INDICATOR_START <= ord(c) <= REGIONAL_INDICATOR_END for c in chars
        ):
            return emoji_flag

    # If not a valid regional indicator sequence, return as-is
    return emoji_flag


def extract_iso_codes_from_regex(iso2_pattern: str) -> List[str]:
    """
    Extract ISO2 codes from regex patterns in country data.

    Some entries in the country converter data use regex patterns like
    '^GB$|^UK$' instead of simple ISO codes. This function extracts
    the actual codes from these patterns.

    Args:
        iso2_pattern: The ISO2 field value (may be a regex pattern).

    Returns:
        List[str]: List of extracted ISO2 codes.

    Example:
        >>> extract_iso_codes_from_regex("^GB$|^UK$")
        ['GB', 'UK']
        >>> extract_iso_codes_from_regex("US")
        ['US']
        >>> extract_iso_codes_from_regex("^GR$|^EL$")
        ['GR', 'EL']
    """
    if not iso2_pattern or iso2_pattern == "not found":
        return []

    # Check if it's a regex pattern (contains | or ^ or $)
    if "|" in iso2_pattern or "^" in iso2_pattern or "$" in iso2_pattern:
        # Extract codes from patterns like "^GB$|^UK$"
        # Split by | and remove regex anchors
        parts = iso2_pattern.split("|")
        codes = []
        for part in parts:
            # Remove ^ and $ anchors
            clean_code = part.strip("^$").strip()
            if clean_code and len(clean_code) == 2:
                codes.append(clean_code.upper())
        return codes
    else:
        # Simple ISO2 code
        return [iso2_pattern.upper()] if len(iso2_pattern) == 2 else []


def is_regional_indicator_sequence(text: str) -> bool:
    """
    Check if a string is a valid regional indicator sequence (flag emoji).

    Args:
        text: The string to check.

    Returns:
        bool: True if the string is a valid regional indicator sequence.

    Example:
        >>> is_regional_indicator_sequence("🇬🇧")
        True
        >>> is_regional_indicator_sequence("🏴󠁧󠁢󠁵󠁫󠁿")
        False
        >>> is_regional_indicator_sequence("GB")
        False
    """
    if not text or len(text) != 2:
        return False

    # Check if both characters are regional indicators
    return all(
        REGIONAL_INDICATOR_START <= ord(c) <= REGIONAL_INDICATOR_END for c in text
    )


def get_iso_code_from_flag(emoji_flag: str) -> Optional[str]:
    """
    Extract the ISO code from a regional indicator sequence flag emoji.

    Args:
        emoji_flag: The flag emoji to convert to ISO code.

    Returns:
        Optional[str]: The corresponding ISO code, or None if not a valid flag.

    Example:
        >>> get_iso_code_from_flag("🇬🇧")
        'GB'
        >>> get_iso_code_from_flag("🇺🇸")
        'US'
        >>> get_iso_code_from_flag("🇦🇨")
        'AC'
        >>> get_iso_code_from_flag("invalid")
        None
    """
    if not is_regional_indicator_sequence(emoji_flag):
        return None

    # Convert regional indicators to ASCII letters
    chars = list(emoji_flag)
    letters = []
    for char in chars:
        # Regional indicators start at U+1F1E6 (A) and go to U+1F1FF (Z)
        letter_offset = ord(char) - REGIONAL_INDICATOR_START
        if 0 <= letter_offset <= 25:  # A-Z
            letters.append(chr(ord("A") + letter_offset))
        else:
            return None

    return "".join(letters) if len(letters) == 2 else None


def create_enhanced_flag_mapping(country_data) -> Dict[str, str]:
    """
    Create an enhanced flag-to-country mapping that handles edge cases.

    This function creates a comprehensive mapping that includes:
    - Standard regional indicator flags (🇺🇸 → United States)
    - Alternative ISO codes (🇬🇧 → United Kingdom, 🇺🇰 → United Kingdom)
    - Special territories (🇦🇨 → Ascension Island)

    Args:
        country_data: DataFrame containing country information.

    Returns:
        Dict[str, str]: Enhanced mapping of flag emojis to country names.
    """
    mapping = {}

    # Process each row in the country data
    for _, row in country_data.iterrows():
        country_name = row["name_short"]
        iso2_field = row["ISO2"]

        # Extract ISO codes from the field (handles regex patterns)
        iso_codes = extract_iso_codes_from_regex(iso2_field)

        for iso_code in iso_codes:
            try:
                # Generate flag emoji for this ISO code
                emoji_flag = flag.flag(iso_code)
                emoji_flag = normalize_emoji_flag(emoji_flag)

                # Only add if it's a valid regional indicator sequence
                if is_regional_indicator_sequence(emoji_flag):
                    mapping[emoji_flag] = country_name
                    logger.debug(
                        f"Added mapping: {emoji_flag} -> {country_name} (ISO: {iso_code})"
                    )

            except Exception as e:
                logger.debug(f"Could not generate flag for ISO code '{iso_code}': {e}")

    # Add special mappings for known edge cases
    _add_special_territory_mappings(mapping)

    return mapping


def _add_special_territory_mappings(mapping: Dict[str, str]) -> None:
    """
    Add special mappings for territories and edge cases.

    This function adds mappings for special territories that might not be
    handled correctly by the standard country data.

    Args:
        mapping: The mapping dictionary to enhance.
    """
    # Special territories and their preferred names
    special_territories = {
        "AC": "Ascension Island",
        "TA": "Tristan da Cunha",
        "SH": "Saint Helena",
    }

    for iso_code, preferred_name in special_territories.items():
        try:
            emoji_flag = flag.flag(iso_code)
            emoji_flag = normalize_emoji_flag(emoji_flag)

            if is_regional_indicator_sequence(emoji_flag):
                # Only add if not already mapped or if we prefer this name
                if emoji_flag not in mapping:
                    mapping[emoji_flag] = preferred_name
                    logger.debug(
                        f"Added special mapping: {emoji_flag} -> {preferred_name}"
                    )

        except Exception as e:
            logger.debug(
                f"Could not generate flag for special territory '{iso_code}': {e}"
            )


def reverse_lookup_flag(emoji_flag: str, flag_mapping: Dict[str, str]) -> Optional[str]:
    """
    Perform reverse lookup for a flag emoji with robust handling.

    This function attempts to find the country name for a given flag emoji,
    handling various edge cases and normalization.

    Args:
        emoji_flag: The flag emoji to look up.
        flag_mapping: The flag-to-country mapping to use.

    Returns:
        Optional[str]: The country name, or None if not found.

    Example:
        >>> mapping = {"🇬🇧": "United Kingdom", "🇺🇸": "United States"}
        >>> reverse_lookup_flag("🇬🇧", mapping)
        'United Kingdom'
        >>> reverse_lookup_flag("🇦🇨", mapping)
        None
    """
    if not emoji_flag:
        return None

    # Normalize the input flag
    normalized_flag = normalize_emoji_flag(emoji_flag)

    # Direct lookup
    if normalized_flag in flag_mapping:
        return flag_mapping[normalized_flag]

    # If not found, try to extract ISO code and generate variations
    iso_code = get_iso_code_from_flag(normalized_flag)
    if iso_code:
        # Try common variations for territories like GB/UK
        variations = _get_iso_code_variations(iso_code)
        for variation in variations:
            try:
                variation_flag = flag.flag(variation)
                variation_flag = normalize_emoji_flag(variation_flag)
                if variation_flag in flag_mapping:
                    return flag_mapping[variation_flag]
            except Exception:
                continue

    return None


def _get_iso_code_variations(iso_code: str) -> List[str]:
    """
    Get common variations of an ISO code.

    Some territories have multiple valid ISO codes (e.g., GB/UK for United Kingdom).
    This function returns common variations to try.

    Args:
        iso_code: The base ISO code.

    Returns:
        List[str]: List of ISO code variations to try.
    """
    variations = [iso_code]

    # Add known variations
    variation_map = {
        "GB": ["UK"],
        "UK": ["GB"],
        "GR": ["EL"],
        "EL": ["GR"],
    }

    if iso_code in variation_map:
        variations.extend(variation_map[iso_code])

    return variations
