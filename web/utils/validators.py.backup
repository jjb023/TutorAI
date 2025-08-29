# web/utils/validators.py
"""
Data validation utilities for Tutor AI
Ensures data integrity and security
"""

import re
from datetime import datetime

class ValidationError(Exception):
    """Custom validation error"""
    pass

class StudentValidator:
    @staticmethod
    def validate_name(name):
        """Validate student name"""
        if not name or not name.strip():
            raise ValidationError("Name cannot be empty")
        
        name = name.strip()
        if len(name) < 2:
            raise ValidationError("Name must be at least 2 characters")
        
        if len(name) > 100:
            raise ValidationError("Name cannot exceed 100 characters")
        
        # Allow letters, spaces, hyphens, and apostrophes
        if not re.match(r"^[a-zA-Z\s\-']+$", name):
            raise ValidationError("Name can only contain letters, spaces, hyphens, and apostrophes")
        
        return name
    
    @staticmethod
    def validate_age(age):
        """Validate student age"""
        try:
            age = int(age)
        except (ValueError, TypeError):
            raise ValidationError("Age must be a number")
        
        if age < 4 or age > 18:
            raise ValidationError("Age must be between 4 and 18")
        
        return age
    
    @staticmethod
    def validate_year_group(year_group):
        """Validate year group"""
        valid_years = ["Year 1", "Year 2", "Year 3", "Year 4", "Year 5", "Year 6", 
                      "Year 7", "Year 8", "Year 9", "Year 10", "Year 11"]
        
        if year_group not in valid_years:
            raise ValidationError(f"Invalid year group. Must be one of: {', '.join(valid_years)}")
        
        return year_group
    
    @staticmethod
    def validate_email(email):
        """Validate parent email if provided"""
        if not email:
            return None
        
        email = email.strip()
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(email_pattern, email):
            raise ValidationError("Invalid email format")
        
        return email

class SessionValidator:
    @staticmethod
    def validate_duration(duration):
        """Validate session duration"""
        try:
            duration = int(duration)
        except (ValueError, TypeError):
            raise ValidationError("Duration must be a number")
        
        if duration < 15 or duration > 180:
            raise ValidationError("Duration must be between 15 and 180 minutes")
        
        return duration
    
    @staticmethod
    def validate_mastery_level(level):
        """Validate mastery level"""
        try:
            level = int(level)
        except (ValueError, TypeError):
            raise ValidationError("Mastery level must be a number")
        
        if level < 1 or level > 10:
            raise ValidationError("Mastery level must be between 1 and 10")
        
        return level
    
    @staticmethod
    def validate_subtopic_assessments(assessments):
        """Validate subtopic assessment data"""
        if not assessments:
            raise ValidationError("At least one subtopic must be assessed")
        
        validated = {}
        for subtopic_id, data in assessments.items():
            try:
                subtopic_id = int(subtopic_id)
            except (ValueError, TypeError):
                raise ValidationError(f"Invalid subtopic ID: {subtopic_id}")
            
            if 'level' not in data:
                raise ValidationError(f"No mastery level provided for subtopic {subtopic_id}")
            
            level = SessionValidator.validate_mastery_level(data['level'])
            
            validated[subtopic_id] = {
                'level': level,
                'notes': data.get('notes', '').strip()[:500]  # Limit notes length
            }
        
        return validated

class TutorValidator:
    @staticmethod
    def validate_username(username):
        """Validate tutor username"""
        if not username:
            raise ValidationError("Username cannot be empty")
        
        username = username.strip().lower()
        
        if len(username) < 3 or len(username) > 20:
            raise ValidationError("Username must be between 3 and 20 characters")
        
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            raise ValidationError("Username can only contain letters, numbers, and underscores")
        
        return username
    
    @staticmethod
    def validate_password(password):
        """Validate password strength"""
        if not password:
            raise ValidationError("Password cannot be empty")
        
        if len(password) < 6:
            raise ValidationError("Password must be at least 6 characters")
        
        # Add more password requirements as needed
        # if not re.search(r'[A-Z]', password):
        #     raise ValidationError("Password must contain at least one uppercase letter")
        
        return password

class TopicValidator:
    @staticmethod
    def validate_topic_name(name):
        """Validate topic name"""
        if not name or not name.strip():
            raise ValidationError("Topic name cannot be empty")
        
        name = name.strip()
        if len(name) < 2 or len(name) > 50:
            raise ValidationError("Topic name must be between 2 and 50 characters")
        
        return name
    
    @staticmethod
    def validate_color_code(color):
        """Validate hex color code"""
        if not color:
            return "#607EBC"  # Default color
        
        if not re.match(r'^#[0-9A-Fa-f]{6}$', color):
            raise ValidationError("Invalid color format. Use hex format like #FF0000")
        
        return color
    
    @staticmethod
    def validate_difficulty_order(order):
        """Validate difficulty order"""
        try:
            order = int(order)
        except (ValueError, TypeError):
            raise ValidationError("Difficulty order must be a number")
        
        if order < 1 or order > 999:
            raise ValidationError("Difficulty order must be between 1 and 999")
        
        return order

# Sanitization functions
def sanitize_html(text):
    """Remove HTML tags from text"""
    if not text:
        return ""
    
    # Simple HTML tag removal - for production use a proper library like bleach
    clean = re.sub('<.*?>', '', str(text))
    return clean.strip()

def sanitize_filename(filename):
    """Make filename safe for filesystem"""
    if not filename:
        return ""
    
    # Remove path separators and other dangerous characters
    filename = re.sub(r'[/\\:*?"<>|]', '_', filename)
    return filename[:255]  # Limit length

# Usage example for Flask routes
def validate_student_data(form_data):
    """Validate all student form data"""
    errors = {}
    cleaned_data = {}
    
    try:
        cleaned_data['name'] = StudentValidator.validate_name(form_data.get('name'))
    except ValidationError as e:
        errors['name'] = str(e)
    
    try:
        cleaned_data['age'] = StudentValidator.validate_age(form_data.get('age'))
    except ValidationError as e:
        errors['age'] = str(e)
    
    try:
        cleaned_data['year_group'] = StudentValidator.validate_year_group(form_data.get('year_group'))
    except ValidationError as e:
        errors['year_group'] = str(e)
    
    # Optional fields
    cleaned_data['target_school'] = sanitize_html(form_data.get('target_school', ''))[:100]
    cleaned_data['parent_contact'] = sanitize_html(form_data.get('parent_contact', ''))[:100]
    cleaned_data['notes'] = sanitize_html(form_data.get('notes', ''))[:500]
    
    return cleaned_data, errors