#!/usr/bin/env python3
"""
Fix questions table - ensures all required columns exist
"""

import sqlite3
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def fix_questions_table():
    """Ensure questions table has all required columns"""
    
    # Get the correct path to your database
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'tutor_ai.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        return False
    
    print(f"🚀 Fixing questions table at {db_path}...")
    
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # First, check if questions table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='questions'")
        if not cursor.fetchone():
            print("📋 Creating questions table from scratch...")
            cursor.execute("""
            CREATE TABLE questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subtopic_id INTEGER NOT NULL,
                question_text TEXT NOT NULL,
                difficulty_level INTEGER CHECK(difficulty_level IN (1, 2, 3)),
                time_estimate_minutes INTEGER DEFAULT 2,
                space_required TEXT DEFAULT 'medium' CHECK(space_required IN ('none', 'small', 'medium', 'large')),
                question_type TEXT,
                created_date TEXT DEFAULT CURRENT_TIMESTAMP,
                created_by_tutor_id INTEGER DEFAULT 1,
                active BOOLEAN DEFAULT 1,
                FOREIGN KEY (subtopic_id) REFERENCES subtopics(id),
                FOREIGN KEY (created_by_tutor_id) REFERENCES tutors(id)
            )
            """)
            print("✅ Created questions table")
        else:
            # Table exists, check for missing columns
            cursor.execute("PRAGMA table_info(questions)")
            existing_columns = [column[1] for column in cursor.fetchall()]
            print(f"📋 Existing columns: {existing_columns}")
            
            # Add missing columns
            required_columns = {
                'difficulty_level': 'INTEGER CHECK(difficulty_level IN (1, 2, 3))',
                'time_estimate_minutes': 'INTEGER DEFAULT 2',
                'space_required': "TEXT DEFAULT 'medium'",
                'question_type': 'TEXT',
                'created_date': 'TEXT DEFAULT CURRENT_TIMESTAMP',
                'created_by_tutor_id': 'INTEGER DEFAULT 1',
                'active': 'BOOLEAN DEFAULT 1'
            }
            
            for col_name, col_def in required_columns.items():
                if col_name not in existing_columns:
                    print(f"➕ Adding '{col_name}' column...")
                    try:
                        cursor.execute(f"ALTER TABLE questions ADD COLUMN {col_name} {col_def}")
                        print(f"✅ Added '{col_name}' column")
                    except sqlite3.OperationalError as e:
                        if "duplicate column" in str(e).lower():
                            print(f"✅ Column '{col_name}' already exists")
                        else:
                            print(f"⚠️ Could not add {col_name}: {e}")
        
        # Create indexes for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_questions_subtopic ON questions(subtopic_id, difficulty_level)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_questions_active ON questions(active)")
        print("✅ Created indexes")
        
        # Also ensure worksheet tables exist
        print("\n📋 Checking worksheet tables...")
        
        # Worksheets table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS worksheets (
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
        
        # Worksheet questions table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS worksheet_questions (
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
        
        print("✅ Worksheet tables ready")
        
        conn.commit()
        
        # Verify final structure
        cursor.execute("PRAGMA table_info(questions)")
        final_columns = cursor.fetchall()
        print("\n✅ Final questions table structure:")
        for col in final_columns:
            print(f"   - {col[1]} ({col[2]})")
        
        print("\n✅ Database fixed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    fix_questions_table()