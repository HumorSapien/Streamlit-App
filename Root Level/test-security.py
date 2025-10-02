import unittest
import pandas as pd
from config.security import SecurityConfig
import sys
import os

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestSecurity(unittest.TestCase):
    """Test security functionality"""

    def setUp(self):
        self.security = SecurityConfig()

    def test_input_sanitization(self):
        """Test input sanitization"""
        malicious_input = "<script>alert('xss')</script>"
        sanitized = self.security.sanitize_input(malicious_input)
        self.assertNotIn('<script>', sanitized.lower())

    def test_data_validation_safe(self):
        """Test data validation with safe data"""
        safe_data = pd.DataFrame({
            'name': ['John', 'Jane', 'Bob'],
            'age': [25, 30, 35],
            'city': ['New York', 'Chicago', 'LA']
        })

        result = self.security.validate_data_content(safe_data)
        self.assertTrue(result['safe'])
        self.assertEqual(len(result['errors']), 0)

    def test_data_validation_suspicious(self):
        """Test data validation with suspicious data"""
        suspicious_data = pd.DataFrame({
            'name': ['John', 'Jane'],
            'comment': ['Normal comment', '<script>alert("xss")</script>']
        })

        result = self.security.validate_data_content(suspicious_data)
        self.assertGreater(len(result['warnings']), 0)

    def test_api_rate_limiting(self):
        """Test API rate limiting"""
        # First call should be allowed
        result1 = self.security.validate_api_usage("test_user")
        self.assertTrue(result1['allowed'])

        # Simulate many calls
        for _ in range(10):
            result = self.security.validate_api_usage("test_user")

        # Should be rate limited
        final_result = self.security.validate_api_usage("test_user")
        self.assertFalse(final_result['allowed'])

if __name__ == '__main__':
    unittest.main()
