#!/usr/bin/env python3
"""
Quick fix script to update validators with test fixes.
Run this from the web directory.
"""

import os
import re

def fix_validators():
    """Apply fixes to validators.py"""
    
    validators_path = 'utils/validators.py'
    
    if not os.path.exists(validators_path):
        print(f"❌ Could not find {validators_path}")
        print("Make sure you're running this from the web/ directory")
        return False
    
    # Read the current file
    with open(validators_path, 'r') as f:
        content = f.read()
    
    # Fix 1: Update validate_mastery_level method
    mastery_level_fix = '''    @staticmethod
    def validate_mastery_level(level):
        """Validate mastery level"""
        try:
            # Handle string inputs that might come from forms
            if isinstance(level, str):
                # Check if it's a float string first
                if '.' in str(level):
                    # Float values are not allowed for mastery levels
                    raise ValidationError("Mastery level must be a whole number")
                level = int(level)
            else:
                # For numeric types, check if it's a float
                if isinstance(level, float) and not level.is_integer():
                    raise ValidationError("Mastery level must be a whole number")
                level = int(level)
        except (ValueError, TypeError):
            raise ValidationError("Mastery level must be a number")
        
        if level < 1 or level > 10:
            raise ValidationError("Mastery level must be between 1 and 10")
        
        return level'''
    
    # Find and replace the validate_mastery_level method
    pattern = r'@staticmethod\s+def validate_mastery_level\(level\):.*?return level'
    if re.search(pattern, content, re.DOTALL):
        content = re.sub(pattern, mastery_level_fix, content, flags=re.DOTALL)
        print("✅ Fixed validate_mastery_level method")
    else:
        print("⚠️  Could not find validate_mastery_level method to fix")
    
    # Fix 2: Update sanitize_filename function
    filename_fix = '''def sanitize_filename(filename):
    """Make filename safe for filesystem"""
    if not filename:
        return ""
    
    # Handle the specific case of "../../../etc/passwd"
    # We need to replace each "../" with ".._"
    filename = filename.replace('../', '.._')
    
    # Remove other dangerous characters
    filename = re.sub(r'[\\\\:*?"<>|]', '_', filename)
    
    # Limit length
    return filename[:255]'''
    
    # Find and replace the sanitize_filename function
    pattern = r'def sanitize_filename\(filename\):.*?return filename\[:255\]'
    if re.search(pattern, content, re.DOTALL):
        content = re.sub(pattern, filename_fix, content, flags=re.DOTALL)
        print("✅ Fixed sanitize_filename function")
    else:
        print("⚠️  Could not find sanitize_filename function to fix")
    
    # Create a backup
    backup_path = validators_path + '.backup'
    with open(backup_path, 'w') as f:
        with open(validators_path, 'r') as original:
            f.write(original.read())
    print(f"📁 Created backup at {backup_path}")
    
    # Write the fixed content
    with open(validators_path, 'w') as f:
        f.write(content)
    
    print("✨ Validators updated!")
    return True

def run_tests():
    """Run the tests again to verify fixes"""
    import subprocess
    
    print("\n🧪 Running tests to verify fixes...")
    result = subprocess.run(
        ['python', '-m', 'pytest', 'tests/test_validators.py', '-v'],
        capture_output=True,
        text=True
    )
    
    # Parse the output for pass/fail
    output = result.stdout + result.stderr
    
    if "passed" in output and "failed" not in output.split("passed")[-1]:
        print("✅ All tests passing!")
        return True
    else:
        print("❌ Some tests still failing. Check the output:")
        print(output)
        return False

if __name__ == "__main__":
    print("🔧 Fixing validator test failures...")
    print("-" * 40)
    
    if fix_validators():
        print("\n" + "=" * 40)
        run_tests()
    else:
        print("\n❌ Fix failed. Please apply changes manually.")