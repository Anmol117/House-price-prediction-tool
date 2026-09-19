"""
Unit tests for utility functions.
"""

import pytest
from backend.utils import sanitize_location


class TestSanitizeLocation:
    """Test suite for sanitize_location function."""
    
    def test_sanitize_location_keeps_alphanumeric(self):
        """Test that alphanumeric characters are preserved."""
        result = sanitize_location("SanFrancisco123")
        assert result == "SanFrancisco123"
    
    def test_sanitize_location_keeps_spaces(self):
        """Test that spaces are preserved."""
        result = sanitize_location("San Francisco")
        assert result == "San Francisco"
    
    def test_sanitize_location_keeps_commas(self):
        """Test that commas are preserved."""
        result = sanitize_location("San Francisco, CA")
        assert result == "San Francisco, CA"
    
    def test_sanitize_location_keeps_periods(self):
        """Test that periods are preserved."""
        result = sanitize_location("St. Louis")
        assert result == "St. Louis"
    
    def test_sanitize_location_keeps_hyphens(self):
        """Test that hyphens are preserved."""
        result = sanitize_location("Winston-Salem")
        assert result == "Winston-Salem"
    
    def test_sanitize_location_keeps_apostrophes(self):
        """Test that apostrophes are preserved."""
        result = sanitize_location("St. Mary's")
        assert result == "St. Mary's"
    
    def test_sanitize_location_removes_exclamation(self):
        """Test that exclamation marks are removed."""
        result = sanitize_location("San Francisco!")
        assert result == "San Francisco"
    
    def test_sanitize_location_removes_semicolon(self):
        """Test that semicolons are removed."""
        result = sanitize_location("New York; NY")
        assert result == "New York NY"
    
    def test_sanitize_location_removes_parentheses(self):
        """Test that parentheses are removed."""
        result = sanitize_location("New York (Manhattan)")
        assert result == "New York Manhattan"
    
    def test_sanitize_location_removes_brackets(self):
        """Test that brackets are removed."""
        result = sanitize_location("San Francisco [CA]")
        assert result == "San Francisco CA"
    
    def test_sanitize_location_removes_special_chars(self):
        """Test that various special characters are removed."""
        result = sanitize_location("City@#$%^&*Name")
        assert result == "CityName"
    
    def test_sanitize_location_complex_case(self):
        """Test complex location with multiple valid and invalid characters."""
        result = sanitize_location("St. Mary's-on-the-Hill, CA 94102!")
        assert result == "St. Mary's-on-the-Hill, CA 94102"
    
    def test_sanitize_location_empty_string(self):
        """Test that empty string returns empty string."""
        result = sanitize_location("")
        assert result == ""
    
    def test_sanitize_location_only_invalid_chars(self):
        """Test that string with only invalid characters returns empty string."""
        result = sanitize_location("!@#$%^&*()")
        assert result == ""
    
    def test_sanitize_location_unicode_characters(self):
        """Test that unicode characters are removed."""
        result = sanitize_location("São Paulo")
        assert result == "So Paulo"
    
    def test_sanitize_location_preserves_multiple_spaces(self):
        """Test that multiple consecutive spaces are preserved."""
        result = sanitize_location("San  Francisco")
        assert result == "San  Francisco"
    
    def test_sanitize_location_with_numbers(self):
        """Test location with numbers and address components."""
        result = sanitize_location("123 Main St., Apt. 4B")
        assert result == "123 Main St., Apt. 4B"
    
    def test_sanitize_location_with_slash(self):
        """Test that forward slash is removed."""
        result = sanitize_location("City/Town")
        assert result == "CityTown"
    
    def test_sanitize_location_with_backslash(self):
        """Test that backslash is removed."""
        result = sanitize_location("City\\Town")
        assert result == "CityTown"
    
    def test_sanitize_location_with_quotes(self):
        """Test that double quotes are removed (apostrophes/single quotes are kept)."""
        result = sanitize_location('"San Francisco"')
        assert result == "San Francisco"
    
    def test_sanitize_location_requirement_example(self):
        """Test example based on requirement 10.8."""
        # Valid characters should be preserved
        result = sanitize_location("San Francisco, CA 94102 - O'Reilly St.")
        assert result == "San Francisco, CA 94102 - O'Reilly St."
        
        # Invalid characters should be removed
        result = sanitize_location("San@Francisco#CA$94102%")
        assert result == "SanFranciscoCA94102"
