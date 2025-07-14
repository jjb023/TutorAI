#!/usr/bin/env python3
"""
Complete fix for questions table - ensures all required columns exist
"""

import sqlite3
import os

def fix_questions_table_complete():
    """Ensure questions table has all required columns"""
    
    db_path = os.path.join('..', 'data', 'tutor_ai.db')
    if not os.path.exists(db_path):
        print("❌ Database not found")
        return False
    
    print("🚀 Fixing questions table completely...")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # First, check what columns currently exist
        cursor.execute("PRAGMA table_info(questions)")
        existing_columns = [column[1] for column in cursor.fetchall()]
        print(f"Existing columns: {existing_columns}")
        
        # Check if questions table exists but is incomplete
        if existing_columns:
            # Add missing columns one by one
            required_columns = {
                'active': 'BOOLEAN DEFAULT 1',
                'time_estimate_minutes': 'INTEGER DEFAULT 2',
                'space_required': "TEXT DEFAULT 'medium'",
                'question_type': 'TEXT',
                'created_date': 'TEXT DEFAULT CURRENT_TIMESTAMP',
                'created_by_tutor_id': 'INTEGER DEFAULT 1'
            }
            
            for col_name, col_def in required_columns.items():
                if col_name not in existing_columns:
                    print(f"➕ Adding '{col_name}' column...")
                    try:
                        cursor.execute(f"ALTER TABLE questions ADD COLUMN {col_name} {col_def}")
                        print(f"✅ Added '{col_name}' column")
                    except sqlite3.OperationalError as e:
                        print(f"⚠️  Could not add {col_name}: {e}")
        else:
            # Table doesn't exist or is empty, create it fresh
            print("Creating questions table from scratch...")
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS questions (
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
            print("✅ Created complete questions table")
        
        # Create indexes for performance
        try:
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_questions_subtopic ON questions(subtopic_id, difficulty_level)")
            print("✅ Created indexes")
        except:
            pass
        
        conn.commit()
        
        # Verify final structure
        cursor.execute("PRAGMA table_info(questions)")
        final_columns = cursor.fetchall()
        print("\n✅ Final table structure:")
        for col in final_columns:
            print(f"   - {col[1]} ({col[2]})")
        
        conn.close()
        print("\n✅ Questions table fixed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    fix_questions_table_complete()