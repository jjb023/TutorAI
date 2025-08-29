# tests/test_validators.py
""" 
Unit tests for data validation functions.
Tests all validators to ensure data integrity and security.
Author: Josh Beal
Date: 2025
"""

import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from web.utils.validators import (
    StudentValidator, 
    SessionValidator, 
    TutorValidator, 
    TopicValidator,
    ValidationError, 
    sanitize_html, 
    sanitize_filename
)


class TestStudentValidator(unittest.TestCase):
    """Test suite for student data validation."""
    
    def test_valid_names(self):
        """Test that valid names pass validation."""
        valid_names = [
            "John Doe",
            "Mary-Jane Smith", 
            "O'Connor",
            "Jean-Pierre",
            "A B"  # Minimum valid name
        ]
        
        for name in valid_names:
            result = StudentValidator.validate_name(name)
            self.assertEqual(result, name.strip())
    
    def test_invalid_names(self):
        """Test that invalid names raise ValidationError."""
        invalid_names = [
            "",  # Empty
            " ",  # Whitespace only
            "A",  # Too short
            "123",  # Numbers
            "John@Doe",  # Special characters
            "a" * 101,  # Too long
            "<script>alert('xss')</script>"  # HTML injection attempt
        ]
        
        for name in invalid_names:
            with self.assertRaises(ValidationError):
                StudentValidator.validate_name(name)
    
    def test_age_validation(self):
        """Test age validation boundaries."""
        # Valid ages
        for age in [4, 10, 18]:
            result = StudentValidator.validate_age(age)
            self.assertEqual(result, age)
        
        # Invalid ages  
        invalid_ages = [3, 19, -1, 0, "abc", None, 999]
        for age in invalid_ages:
            with self.assertRaises(ValidationError):
                StudentValidator.validate_age(age)
    
    def test_year_group_validation(self):
        """Test year group validation."""
        # Valid year groups
        valid_years = ["Year 1", "Year 7", "Year 11"]
        for year in valid_years:
            result = StudentValidator.validate_year_group(year)
            self.assertEqual(result, year)
        
        # Invalid year groups
        invalid_years = ["", "Year 12", "Year 0", "Grade 5", "year 5"]
        for year in invalid_years:
            with self.assertRaises(ValidationError):
                StudentValidator.validate_year_group(year)
    
    def test_email_validation(self):
        """Test email validation."""
        # Valid emails
        valid_emails = [
            "parent@example.com",
            "john.doe@company.co.uk", 
            "test+tag@email.com"
        ]
        for email in valid_emails:
            result = StudentValidator.validate_email(email)
            self.assertEqual(result, email.strip())
        
        # Invalid emails
        invalid_emails = [
            "notanemail",
            "@example.com",
            "user@",
            "user @example.com",
            "user@.com"
        ]
        for email in invalid_emails:
            with self.assertRaises(ValidationError):
                StudentValidator.validate_email(email)
        
        # None should return None (optional field)
        self.assertIsNone(StudentValidator.validate_email(None))
        self.assertIsNone(StudentValidator.validate_email(""))


class TestSessionValidator(unittest.TestCase):
    """Test suite for session data validation."""
    
    def test_duration_validation(self):
        """Test session duration validation."""
        # Valid durations
        valid_durations = [15, 30, 60, 90, 120, 180]
        for duration in valid_durations:
            result = SessionValidator.validate_duration(duration)
            self.assertEqual(result, duration)
        
        # Invalid durations
        invalid_durations = [14, 181, -30, 0, "sixty", None]
        for duration in invalid_durations:
            with self.assertRaises(ValidationError):
                SessionValidator.validate_duration(duration)
    
    def test_mastery_level_validation(self):
        """Test mastery level validation."""
        # Valid levels
        for level in range(1, 11):
            result = SessionValidator.validate_mastery_level(level)
            self.assertEqual(result, level)
        
        # Invalid levels
        invalid_levels = [0, 11, -1, 1.5, "five", None]
        for level in invalid_levels:
            with self.assertRaises(ValidationError):
                SessionValidator.validate_mastery_level(level)
    
    def test_subtopic_assessments_validation(self):
        """Test validation of subtopic assessment data."""
        # Valid assessment data
        valid_data = {
            "1": {"level": 5, "notes": "Good progress"},
            "2": {"level": 7},
            3: {"level": 10, "notes": ""}
        }
        result = SessionValidator.validate_subtopic_assessments(valid_data)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[1]["level"], 5)
        
        # Invalid - empty assessments
        with self.assertRaises(ValidationError):
            SessionValidator.validate_subtopic_assessments({})
        
        # Invalid - missing level
        with self.assertRaises(ValidationError):
            SessionValidator.validate_subtopic_assessments({
                "1": {"notes": "No level provided"}
            })
        
        # Invalid - bad level value
        with self.assertRaises(ValidationError):
            SessionValidator.validate_subtopic_assessments({
                "1": {"level": 11}
            })


class TestTutorValidator(unittest.TestCase):
    """Test suite for tutor data validation."""
    
    def test_username_validation(self):
        """Test username validation."""
        # Valid usernames
        valid_usernames = ["john", "mary_doe", "tutor123", "a_b_c"]
        for username in valid_usernames:
            result = TutorValidator.validate_username(username)
            self.assertEqual(result, username.lower())
        
        # Invalid usernames
        invalid_usernames = [
            "",  # Empty
            "ab",  # Too short
            "a" * 21,  # Too long
            "john@doe",  # Invalid character
            "user name",  # Space
            "user-name"  # Hyphen
        ]
        for username in invalid_usernames:
            with self.assertRaises(ValidationError):
                TutorValidator.validate_username(username)
    
    def test_password_validation(self):
        """Test password validation."""
        # Valid passwords
        valid_passwords = ["password123", "MyP@ssw0rd", "123456", "a" * 6]
        for password in valid_passwords:
            result = TutorValidator.validate_password(password)
            self.assertEqual(result, password)
        
        # Invalid passwords
        invalid_passwords = ["", "12345", None]
        for password in invalid_passwords:
            with self.assertRaises(ValidationError):
                TutorValidator.validate_password(password)


class TestTopicValidator(unittest.TestCase):
    """Test suite for topic data validation."""
    
    def test_topic_name_validation(self):
        """Test topic name validation."""
        # Valid names
        valid_names = ["Mathematics", "English Language", "Science", "AB"]
        for name in valid_names:
            result = TopicValidator.validate_topic_name(name)
            self.assertEqual(result, name.strip())
        
        # Invalid names
        invalid_names = ["", " ", "A", "a" * 51]
        for name in invalid_names:
            with self.assertRaises(ValidationError):
                TopicValidator.validate_topic_name(name)
    
    def test_color_code_validation(self):
        """Test hex color code validation."""
        # Valid colors
        valid_colors = ["#FF0000", "#00ff00", "#123ABC", "#000000"]
        for color in valid_colors:
            result = TopicValidator.validate_color_code(color)
            self.assertEqual(result, color)
        
        # Invalid colors
        invalid_colors = ["FF0000", "#FF00", "#GGGGGG", "red", "#FF00000"]
        for color in invalid_colors:
            with self.assertRaises(ValidationError):
                TopicValidator.validate_color_code(color)
        
        # None should return default
        result = TopicValidator.validate_color_code(None)
        self.assertEqual(result, "#607EBC")
    
    def test_difficulty_order_validation(self):
        """Test difficulty order validation."""
        # Valid orders
        valid_orders = [1, 50, 999]
        for order in valid_orders:
            result = TopicValidator.validate_difficulty_order(order)
            self.assertEqual(result, order)
        
        # Invalid orders
        invalid_orders = [0, 1000, -1, "first", None]
        for order in invalid_orders:
            with self.assertRaises(ValidationError):
                TopicValidator.validate_difficulty_order(order)


class TestSanitizationFunctions(unittest.TestCase):
    """Test suite for sanitization functions."""
    
    def test_html_sanitization(self):
        """Test HTML tag removal."""
        test_cases = [
            ("<script>alert('xss')</script>", "alert('xss')"),
            ("<b>Bold text</b>", "Bold text"),
            ("Normal text", "Normal text"),
            ("<div>Content</div>", "Content"),
            ("", ""),
            (None, "")
        ]
        
        for input_text, expected in test_cases:
            result = sanitize_html(input_text)
            self.assertEqual(result, expected)
    
    def test_filename_sanitization(self):
        """Test filename sanitization."""
        test_cases = [
            ("normal_file.pdf", "normal_file.pdf"),
            ("../../../etc/passwd", ".._.._.._.._etc_passwd"),
            ("file:with:colons.txt", "file_with_colons.txt"), 
            ("file*with?chars.doc", "file_with_chars.doc"),
            ("a" * 300, "a" * 255),  # Length limit
            ("", ""),
            (None, "")
        ]
        
        for input_name, expected in test_cases:
            result = sanitize_filename(input_name)
            self.assertEqual(result, expected)


def suite():
    """Create test suite."""
    test_suite = unittest.TestSuite()
    
    # Add all test classes
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestStudentValidator))
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSessionValidator))
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestTutorValidator))
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestTopicValidator))
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSanitizationFunctions))
    
    return test_suite


if __name__ == '__main__':
    # Run tests with verbosity
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite())
    
    # Print summary
    print("\n" + "="*50)
    print("🧪 VALIDATION TEST SUMMARY")
    print("="*50)
    
    if result.wasSuccessful():
        print("✅ All validation tests passed!")
        print("🔒 Data integrity and security measures are working correctly.")
    else:
        print(f"❌ {len(result.failures)} test(s) failed")
        print(f"💥 {len(result.errors)} error(s) occurred")
        print("⚠️  Review validators to ensure data safety")
    
    print(f"\n📊 Tests run: {result.testsRun}")
    print(f"🎯 Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    # Exit with appropriate code for CI/CD
    exit(0 if result.wasSuccessful() else 1)