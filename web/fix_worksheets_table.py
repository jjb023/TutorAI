#!/usr/bin/env python3
"""
Fix worksheets table by adding missing columns
Run this to resolve the 'no column named subtopic_id' error
"""

import sqlite3
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def fix_worksheets_table():
    """Add missing columns to worksheets table"""
    
    # Get the database path
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'tutor_ai.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        return False
    
    print("🔧 Fixing worksheets table...")
    print("=" * 50)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # First, check what columns currently exist
        cursor.execute("PRAGMA table_info(worksheets)")
        existing_columns = [column[1] for column in cursor.fetchall()]
        print(f"📋 Current columns in worksheets table: {existing_columns}")
        
        # Check if table exists at all
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='worksheets'")
        if not cursor.fetchone():
            print("❌ Worksheets table doesn't exist! Creating it from scratch...")
            
            # Create the complete worksheets table
            cursor.execute("""
            CREATE TABLE worksheets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                subtopic_id INTEGER NOT NULL,
                title TEXT,
                difficulty_level TEXT,
                generated_date TEXT DEFAULT CURRENT_TIMESTAMP,
                generated_by_tutor_id INTEGER,
                pdf_path TEXT,
                status TEXT DEFAULT 'draft',
                session_id INTEGER,
                notes TEXT,
                FOREIGN KEY (student_id) REFERENCES students(id),
                FOREIGN KEY (subtopic_id) REFERENCES subtopics(id),
                FOREIGN KEY (generated_by_tutor_id) REFERENCES tutors(id),
                FOREIGN KEY (session_id) REFERENCES sessions(id)
            )
            """)
            print("✅ Created worksheets table with all columns")
            
        else:
            # Table exists, add missing columns
            columns_to_add = {
                'subtopic_id': 'INTEGER NOT NULL DEFAULT 1',
                'title': 'TEXT',
                'difficulty_level': 'TEXT',
                'generated_date': 'TEXT DEFAULT CURRENT_TIMESTAMP',
                'generated_by_tutor_id': 'INTEGER DEFAULT 1',
                'pdf_path': 'TEXT',
                'status': "TEXT DEFAULT 'draft'",
                'session_id': 'INTEGER',
                'notes': 'TEXT'
            }
            
            for col_name, col_def in columns_to_add.items():
                if col_name not in existing_columns:
                    try:
                        print(f"➕ Adding column '{col_name}'...")
                        cursor.execute(f"ALTER TABLE worksheets ADD COLUMN {col_name} {col_def}")
                        print(f"✅ Added '{col_name}' column")
                    except sqlite3.OperationalError as e:
                        if "duplicate column" in str(e).lower():
                            print(f"✅ Column '{col_name}' already exists")
                        else:
                            print(f"⚠️ Error adding {col_name}: {e}")
                else:
                    print(f"✅ Column '{col_name}' already exists")
        
        # Also ensure worksheet_questions table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='worksheet_questions'")
        if not cursor.fetchone():
            print("\n📋 Creating worksheet_questions table...")
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
            print("✅ Created worksheet_questions table")
        
        # Create indexes
        print("\n📋 Creating indexes for performance...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_worksheets_student ON worksheets(student_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_worksheets_subtopic ON worksheets(subtopic_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_worksheet_questions ON worksheet_questions(worksheet_id)")
        print("✅ Indexes created")
        
        conn.commit()
        
        # Verify the fix
        print("\n🔍 Verifying fix...")
        cursor.execute("PRAGMA table_info(worksheets)")
        final_columns = [column[1] for column in cursor.fetchall()]
        print(f"📋 Final columns in worksheets table: {final_columns}")
        
        if 'subtopic_id' in final_columns:
            print("\n✅ SUCCESS! The worksheets table now has all required columns.")
            print("   You should be able to generate worksheets now!")
        else:
            print("\n❌ FAILED! The subtopic_id column is still missing.")
            print("   There may be a deeper issue with your database.")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def check_database_state():
    """Additional check to see the current state of worksheet-related tables"""
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'tutor_ai.db')
    
    print("\n📊 Current Database State:")
    print("=" * 50)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check all worksheet-related tables
    tables = ['worksheets', 'worksheet_questions', 'questions']
    
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='{table}'")
        exists = cursor.fetchone()[0] > 0
        
        if exists:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"✅ Table '{table}' exists with {count} records")
        else:
            print(f"❌ Table '{table}' does not exist")
    
    conn.close()

if __name__ == "__main__":
    print("🎯 Worksheet Table Fix Tool")
    print("This will add the missing subtopic_id column and ensure all worksheet tables are properly set up.")
    print()
    
    # Run the fix
    success = fix_worksheets_table()
    
    if success:
        # Show current state
        check_database_state()
        
        print("\n💡 Next steps:")
        print("1. Run the populate_test_questions.py script if you haven't already")
        print("2. Try generating a worksheet again")
        print("3. If you still get errors, check the Flask app logs for more details")
    else:
        print("\n❌ Fix failed. Please check the error messages above.")