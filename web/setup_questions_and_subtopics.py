#!/usr/bin/env python3
"""
Setup script to fix questions table and enable all features
Run this from the web directory
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def setup_all():
    """Run all setup steps"""
    print("🚀 Setting up Tutor AI Worksheet System...")
    print("=" * 50)
    
    # Step 1: Fix questions table
    print("\n📋 Step 1: Fixing questions table...")
    from fix_questions_table import fix_questions_table
    if fix_questions_table():
        print("✅ Questions table fixed!")
    else:
        print("❌ Failed to fix questions table")
        return False
    
    # Step 2: Ensure worksheet directories exist
    print("\n📁 Step 2: Creating required directories...")
    from setup_worksheet_dirs import setup_directories
    setup_directories()
    
    # Step 3: Update populate_questions.py to handle answer field
    print("\n📝 Step 3: Updating question population script...")
    update_populate_questions()
    
    print("\n✅ Setup complete!")
    print("\n💡 Next steps:")
    print("1. Restart your Flask app")
    print("2. Login as admin")
    print("3. Try adding a question to any subtopic")
    print("4. Try editing a subtopic")
    
    return True

def update_populate_questions():
    """Update the populate_questions script to handle answer field"""
    populate_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'populate_questions.py')
    
    if os.path.exists(populate_script):
        print("✅ Found populate_questions.py")
        
        # Read the current content
        with open(populate_script, 'r') as f:
            content = f.read()
        
        # Check if it already handles answer field
        if ', answer,' not in content and 'answer' not in content.lower():
            print("⚠️  Updating populate_questions.py to handle answer field...")
            
            # Find and replace the INSERT statement
            # Look for the pattern more carefully
            old_pattern = """cursor.execute('''
                INSERT INTO questions 
                (subtopic_id, question_text, difficulty_level, time_estimate_minutes, 
                 space_required, created_by_tutor_id, active)
                VALUES (?, ?, ?, ?, ?, ?, 1)
            ''', (subtopic_id, question_text, difficulty, time_est, space, tutor_id))"""
            
            new_pattern = """cursor.execute('''
                INSERT INTO questions 
                (subtopic_id, question_text, answer, difficulty_level, time_estimate_minutes, 
                 space_required, created_by_tutor_id, active)
                VALUES (?, ?, NULL, ?, ?, ?, ?, 1)
            ''', (subtopic_id, question_text, difficulty, time_est, space, tutor_id))"""
            
            if old_pattern in content:
                content = content.replace(old_pattern, new_pattern)
                
                # Write back
                with open(populate_script, 'w') as f:
                    f.write(content)
                
                print("✅ Updated populate_questions.py")
            else:
                print("⚠️  Could not find the exact pattern to replace in populate_questions.py")
                print("   You may need to manually update it to include the answer field")
        else:
            print("✅ populate_questions.py already handles answer field")
    else:
        print("⚠️  populate_questions.py not found - you'll need to update it manually")

if __name__ == "__main__":
    # Change to web directory if we're not already there
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if os.path.basename(script_dir) != 'web':
        web_dir = os.path.join(script_dir, 'web')
        if os.path.exists(web_dir):
            os.chdir(web_dir)
            print(f"Changed to web directory: {os.getcwd()}")
    
    setup_all()