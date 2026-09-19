"""
Utility functions for input sanitization and data processing.
"""

import re


def sanitize_location(location: str) -> str:
    """
    Sanitize location string by removing invalid characters.
    
    Keeps only alphanumeric characters, spaces, commas, periods, hyphens, and apostrophes.
    All other characters are removed.
    
    Args:
        location: Raw location string input from user
        
    Returns:
        Sanitized location string with only allowed characters
        
    Example:
        >>> sanitize_location("San Francisco, CA!")
        'San Francisco, CA'
        >>> sanitize_location("New York; NY (Manhattan)")
        'New York NY Manhattan'
        >>> sanitize_location("St. Mary's-on-the-Hill")
        "St. Mary's-on-the-Hill"
    
    Requirements:
        Validates Requirement 10.8: Backend SHALL sanitize location string inputs
        by removing or escaping characters that are not alphanumeric, spaces,
        commas, periods, hyphens, or apostrophes before processing.
    """
    # Pattern matches alphanumeric, spaces, commas, periods, hyphens, and apostrophes
    # Using character class with allowed characters
    pattern = r"[^a-zA-Z0-9 ,.\-']"
    
    # Remove all characters that don't match the allowed set
    sanitized = re.sub(pattern, '', location)
    
    return sanitized
