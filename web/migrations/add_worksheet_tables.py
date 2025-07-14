#!/usr/bin/env python3
"""
Add worksheet generation tables to the database
"""

import sqlite3
import os
from datetime import datetime

def migrate_worksheet_tables():
    """Add tables for worksheet generation system"""
    
    db_path = os.path.join('..', '..', 'data', 'tutor_ai.db')
    if not os.path.exists(db_path):
        print("❌ Database not found")
        return False
    
    print("🚀 Adding worksheet generation tables...")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 1. Modify questions table to better support worksheet generation
        print("\n📋 Creating enhanced questions table...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subtopic_id INTEGER NOT NULL,
            question_text TEXT NOT NULL,
            difficulty_level INTEGER CHECK(difficulty_level IN (1, 2, 3)),
            time_estimate_minutes INTEGER,
            space_required TEXT CHECK(space_required IN ('none', 'small', 'medium', 'large')),
            question_type TEXT,
            created_date TEXT DEFAULT CURRENT_TIMESTAMP,
            created_by_tutor_id INTEGER,
            active BOOLEAN DEFAULT 1,
            FOREIGN KEY (subtopic_id) REFERENCES subtopics(id),
            FOREIGN KEY (created_by_tutor_id) REFERENCES tutors(id)
        )
        """)
        
        # 2. Worksheet templates table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS worksheet_templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            subtopic_id INTEGER,
            difficulty_distribution TEXT,  -- JSON: {"easy": 40, "medium": 40, "hard": 20}
            total_questions INTEGER DEFAULT 20,
            created_by_tutor_id INTEGER,
            created_date TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (subtopic_id) REFERENCES subtopics(id),
            FOREIGN KEY (created_by_tutor_id) REFERENCES tutors(id)
        )
        """)
        
        # 3. Generated worksheets table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS worksheets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            subtopic_id INTEGER NOT NULL,
            title TEXT,
            difficulty_level TEXT,  -- 'easy', 'medium', 'hard', 'mixed'
            generated_date TEXT DEFAULT CURRENT_TIMESTAMP,
            generated_by_tutor_id INTEGER,
            pdf_path TEXT,
            status TEXT DEFAULT 'draft',  -- draft, finalized, printed
            session_id INTEGER,
            notes TEXT,
            FOREIGN KEY (student_id) REFERENCES students(id),
            FOREIGN KEY (subtopic_id) REFERENCES subtopics(id),
            FOREIGN KEY (generated_by_tutor_id) REFERENCES tutors(id),
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        )
        """)
        
        # 4. Worksheet questions (which questions are on which worksheet)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS worksheet_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            worksheet_id INTEGER NOT NULL,
            question_id INTEGER NOT NULL,
            question_order INTEGER,
            custom_question_text TEXT,  -- If tutor edits the question
            space_allocated TEXT,
            FOREIGN KEY (worksheet_id) REFERENCES worksheets(id),
            FOREIGN KEY (question_id) REFERENCES questions(id)
        )
        """)
        
        # 5. Add indexes for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_questions_subtopic ON questions(subtopic_id, difficulty_level)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_worksheets_student ON worksheets(student_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_worksheet_questions ON worksheet_questions(worksheet_id)")
        
        conn.commit()
        print("✅ Worksheet tables created successfully!")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False

if __name__ == "__main__":
    migrate_worksheet_tables()