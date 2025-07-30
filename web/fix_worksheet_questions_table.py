#!/usr/bin/env python3
"""
Fix worksheet_questions table by adding missing columns
Run this to resolve the 'no column named space_allocated' error
"""

import sqlite3
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def fix_worksheet_questions_table():
    """Add missing columns to worksheet_questions table"""
    
    # Get the database path
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'tutor_ai.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        return False
    
    print("🔧 Fixing worksheet_questions table...")
    print("=" * 50)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # First, check what columns currently exist in worksheet_questions
        cursor.execute("PRAGMA table_info(worksheet_questions)")
        existing_columns = [column[1] for column in cursor.fetchall()]
        print(f"📋 Current columns in worksheet_questions table: {existing_columns}")
        
        # Check if table exists at all
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='worksheet_questions'")
        if not cursor.fetchone():
            print("❌ worksheet_questions table doesn't exist! Creating it from scratch...")
            
            # Create the complete worksheet_questions table
            cursor.execute("""
            CREATE TABLE worksheet_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                worksheet_id INTEGER NOT NULL,
                question_id INTEGER NOT NULL,
                question_order INTEGER,
                custom_question_text TEXT,
                space_allocated TEXT,
                FOREIGN KEY (worksheet_id) REFERENCES worksheets(id),
                FOREIGN KEY (question_id) REFERENCES questions(id)
            )
            """)
            print("✅ Created worksheet_questions table with all columns")
            
        else:
            # Table exists, add missing columns
            columns_to_add = {
                'question_order': 'INTEGER',
                'custom_question_text': 'TEXT',
                'space_allocated': 'TEXT'
            }
            
            for col_name, col_def in columns_to_add.items():
                if col_name not in existing_columns:
                    try:
                        print(f"➕ Adding column '{col_name}'...")
                        cursor.execute(f"ALTER TABLE worksheet_questions ADD COLUMN {col_name} {col_def}")
                        print(f"✅ Added '{col_name}' column")
                    except sqlite3.OperationalError as e:
                        if "duplicate column" in str(e).lower():
                            print(f"✅ Column '{col_name}' already exists")
                        else:
                            print(f"⚠️ Error adding {col_name}: {e}")
                else:
                    print(f"✅ Column '{col_name}' already exists")
        
        # Also verify the questions table has required columns
        print("\n📋 Checking questions table...")
        cursor.execute("PRAGMA table_info(questions)")
        question_columns = [column[1] for column in cursor.fetchall()]
        print(f"📋 Current columns in questions table: {question_columns}")
        
        # Add missing columns to questions table if needed
        question_columns_to_add = {
            'space_required': "TEXT DEFAULT 'medium'",
            'answer': 'TEXT',
            'active': 'BOOLEAN DEFAULT 1'
        }
        
        for col_name, col_def in question_columns_to_add.items():
            if col_name not in question_columns:
                try:
                    print(f"➕ Adding column '{col_name}' to questions table...")
                    cursor.execute(f"ALTER TABLE questions ADD COLUMN {col_name} {col_def}")
                    print(f"✅ Added '{col_name}' column to questions table")
                except sqlite3.OperationalError as e:
                    if "duplicate column" in str(e).lower():
                        print(f"✅ Column '{col_name}' already exists in questions table")
                    else:
                        print(f"⚠️ Error adding {col_name} to questions: {e}")
        
        # Create indexes
        print("\n📋 Creating indexes for performance...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_worksheet_questions_worksheet ON worksheet_questions(worksheet_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_worksheet_questions_question ON worksheet_questions(question_id)")
        print("✅ Indexes created")
        
        conn.commit()
        
        # Verify the fix
        print("\n🔍 Verifying fix...")
        cursor.execute("PRAGMA table_info(worksheet_questions)")
        final_columns = [column[1] for column in cursor.fetchall()]
        print(f"📋 Final columns in worksheet_questions table: {final_columns}")
        
        if 'space_allocated' in final_columns:
            print("\n✅ SUCCESS! The worksheet_questions table now has all required columns.")
            
            # Check if there are any worksheet records
            cursor.execute("SELECT COUNT(*) FROM worksheets")
            worksheet_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM questions WHERE active = 1")
            question_count = cursor.fetchone()[0]
            
            print(f"\n📊 Current status:")
            print(f"   - Worksheets: {worksheet_count}")
            print(f"   - Active questions: {question_count}")
            
            if question_count == 0:
                print("\n⚠️  No questions found! Run populate_test_questions.py first")
            else:
                print("\n✅ You should be able to generate worksheets now!")
        else:
            print("\n❌ FAILED! The space_allocated column is still missing.")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def verify_all_tables():
    """Comprehensive check of all worksheet-related tables"""
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'tutor_ai.db')
    
    print("\n📊 Complete Database Verification:")
    print("=" * 50)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Define expected structure
    expected_structure = {
        'worksheets': [
            'id', 'student_id', 'subtopic_id', 'title', 'difficulty_level',
            'generated_date', 'generated_by_tutor_id', 'pdf_path', 'status',
            'session_id', 'notes'
        ],
        'worksheet_questions': [
            'id', 'worksheet_id', 'question_id', 'question_order',
            'custom_question_text', 'space_allocated'
        ],
        'questions': [
            'id', 'subtopic_id', 'question_text', 'answer', 'difficulty_level',
            'time_estimate_minutes', 'space_required', 'question_type',
            'created_date', 'created_by_tutor_id', 'active'
        ]
    }
    
    all_good = True
    
    for table_name, expected_columns in expected_structure.items():
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
        if cursor.fetchone():
            cursor.execute(f"PRAGMA table_info({table_name})")
            actual_columns = [col[1] for col in cursor.fetchall()]
            
            missing_columns = set(expected_columns) - set(actual_columns)
            
            if missing_columns:
                print(f"\n❌ Table '{table_name}' is missing columns: {missing_columns}")
                all_good = False
            else:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f"\n✅ Table '{table_name}' is complete with {count} records")
        else:
            print(f"\n❌ Table '{table_name}' does not exist!")
            all_good = False
    
    if all_good:
        print("\n🎉 All tables are properly structured!")
    else:
        print("\n⚠️  Some tables need fixing. Run the appropriate fix scripts.")
    
    conn.close()
    return all_good

if __name__ == "__main__":
    print("🎯 Worksheet Questions Table Fix Tool")
    print("This will add the missing space_allocated column and ensure all worksheet tables are properly set up.")
    print()
    
    # Run the fix
    success = fix_worksheet_questions_table()
    
    if success:
        # Comprehensive verification
        all_good = verify_all_tables()
        
        if all_good:
            print("\n💡 Next steps:")
            print("1. If you haven't already, run: python populate_test_questions.py")
            print("2. Try generating a worksheet again in the web app")
            print("3. The worksheet generation should now work!")
        else:
            print("\n⚠️  Some issues remain. You may need to run fix_worksheets_table.py as well.")
    else:
        print("\n❌ Fix failed. Please check the error messages above.")