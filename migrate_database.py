#!/usr/bin/env python3
"""
Database Migration Script for Tutor AI
This script updates your existing database to support all new features
Run this after pulling the latest changes from GitHub
"""

import sqlite3
import os
from datetime import datetime

def migrate_database():
    """Safely migrate database to support new features"""
    
    # Get database path
    db_path = os.path.join('data', 'tutor_ai.db')
    if not os.path.exists(db_path):
        print("❌ Database not found at data/tutor_ai.db")
        return False
    
    print("🚀 Starting database migration...")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 1. Check and add missing columns to sessions table
        print("\n📋 Checking sessions table...")
        cursor.execute("PRAGMA table_info(sessions)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'tutor_id' not in columns:
            print("  ➕ Adding tutor_id column to sessions...")
            cursor.execute("""
                ALTER TABLE sessions ADD COLUMN tutor_id INTEGER REFERENCES tutors(id)
            """)
            # Set default tutor_id to 1 (admin) for existing sessions
            cursor.execute("UPDATE sessions SET tutor_id = 1 WHERE tutor_id IS NULL")
            print("  ✅ Added tutor_id column")
        else:
            print("  ✅ tutor_id column already exists")
        
        # 2. Add session-subtopic tracking table (for better history tracking)
        print("\n📋 Creating session progress tracking table...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS session_subtopic_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            subtopic_id INTEGER NOT NULL,
            old_mastery_level INTEGER,
            new_mastery_level INTEGER,
            notes TEXT,
            FOREIGN KEY (session_id) REFERENCES sessions(id),
            FOREIGN KEY (subtopic_id) REFERENCES subtopics(id)
        )
        """)
        print("  ✅ Session progress tracking table ready")
        
        # 3. Add indexes for better performance
        print("\n📋 Adding performance indexes...")
        
        # Index for quick student progress lookups
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_subtopic_progress_student 
        ON subtopic_progress(student_id)
        """)
        
        # Index for session lookups by student
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_sessions_student 
        ON sessions(student_id)
        """)
        
        # Index for subtopic lookups by main topic
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_subtopics_main_topic 
        ON subtopics(main_topic_id)
        """)
        
        print("  ✅ Performance indexes added")
        
        # 4. Add worksheet-related tables for future use
        print("\n📋 Creating worksheet tables for Phase 4...")
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subtopic_id INTEGER,
            question_text TEXT NOT NULL,
            answer TEXT NOT NULL,
            difficulty_level INTEGER CHECK(difficulty_level BETWEEN 1 AND 10),
            question_type TEXT,
            options TEXT,
            explanation TEXT,
            created_date TEXT DEFAULT CURRENT_TIMESTAMP,
            created_by_tutor_id INTEGER,
            FOREIGN KEY (subtopic_id) REFERENCES subtopics(id),
            FOREIGN KEY (created_by_tutor_id) REFERENCES tutors(id)
        )
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS worksheets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            title TEXT,
            generated_date TEXT DEFAULT CURRENT_TIMESTAMP,
            generated_by_tutor_id INTEGER,
            pdf_path TEXT,
            status TEXT DEFAULT 'generated',
            FOREIGN KEY (student_id) REFERENCES students(id),
            FOREIGN KEY (generated_by_tutor_id) REFERENCES tutors(id)
        )
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS worksheet_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            worksheet_id INTEGER,
            question_id INTEGER,
            question_order INTEGER,
            student_answer TEXT,
            is_correct BOOLEAN,
            marked_date TEXT,
            FOREIGN KEY (worksheet_id) REFERENCES worksheets(id),
            FOREIGN KEY (question_id) REFERENCES questions(id)
        )
        """)
        
        print("  ✅ Worksheet tables created")
        
        # 5. Data integrity checks
        print("\n🔍 Running data integrity checks...")
        
        # Check for orphaned progress records
        cursor.execute("""
        SELECT COUNT(*) FROM subtopic_progress sp
        WHERE NOT EXISTS (SELECT 1 FROM students s WHERE s.id = sp.student_id)
        """)
        orphaned = cursor.fetchone()[0]
        if orphaned > 0:
            print(f"  ⚠️  Found {orphaned} orphaned progress records - cleaning up...")
            cursor.execute("""
            DELETE FROM subtopic_progress 
            WHERE student_id NOT IN (SELECT id FROM students)
            """)
        
        # 6. Add sample subtopics if main topics exist but have no subtopics
        cursor.execute("""
        SELECT mt.id, mt.topic_name 
        FROM main_topics mt
        WHERE NOT EXISTS (
            SELECT 1 FROM subtopics s WHERE s.main_topic_id = mt.id
        )
        """)
        empty_topics = cursor.fetchall()
        
        if empty_topics:
            print(f"\n📚 Found {len(empty_topics)} topics without subtopics")
            for topic_id, topic_name in empty_topics:
                print(f"  ➕ Adding sample subtopics for {topic_name}...")
                
                # Add basic subtopics based on topic
                if "Number" in topic_name:
                    sample_subtopics = [
                        ("Basic Counting", "Understanding numbers 1-100", 1),
                        ("Addition Facts", "Single digit addition", 2),
                        ("Subtraction Facts", "Single digit subtraction", 3)
                    ]
                elif "Algebra" in topic_name:
                    sample_subtopics = [
                        ("Patterns", "Recognizing number patterns", 1),
                        ("Simple Equations", "Solving x + a = b", 2),
                        ("Word Problems", "Translating words to equations", 3)
                    ]
                else:
                    sample_subtopics = [
                        (f"Basic {topic_name}", f"Introduction to {topic_name}", 1),
                        (f"Intermediate {topic_name}", f"Building {topic_name} skills", 2),
                        (f"Advanced {topic_name}", f"Mastering {topic_name}", 3)
                    ]
                
                for subtopic_name, desc, order in sample_subtopics:
                    cursor.execute("""
                    INSERT INTO subtopics (main_topic_id, subtopic_name, description, difficulty_order)
                    VALUES (?, ?, ?, ?)
                    """, (topic_id, subtopic_name, desc, order))
        
        # 7. Update statistics
        print("\n📊 Database statistics:")
        
        tables = ['students', 'tutors', 'main_topics', 'subtopics', 'sessions', 'subtopic_progress']
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  • {table}: {count} records")
        
        # Commit all changes
        conn.commit()
        print("\n✅ Database migration completed successfully!")
        
        # Create a migration log
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS migration_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            migration_date TEXT DEFAULT CURRENT_TIMESTAMP,
            version TEXT,
            notes TEXT
        )
        """)
        
        cursor.execute("""
        INSERT INTO migration_log (version, notes)
        VALUES (?, ?)
        """, ("2.0", "Added session-subtopic integration, worksheet tables, and performance indexes"))
        
        conn.commit()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during migration: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False

def verify_database():
    """Verify database structure after migration"""
    print("\n🔍 Verifying database structure...")
    
    db_path = os.path.join('data', 'tutor_ai.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check all required tables exist
    required_tables = [
        'students', 'tutors', 'main_topics', 'subtopics', 
        'sessions', 'subtopic_progress', 'session_subtopic_progress',
        'questions', 'worksheets', 'worksheet_questions'
    ]
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    existing_tables = [table[0] for table in cursor.fetchall()]
    
    all_good = True
    for table in required_tables:
        if table in existing_tables:
            print(f"  ✅ {table} table exists")
        else:
            print(f"  ❌ {table} table missing!")
            all_good = False
    
    conn.close()
    return all_good

if __name__ == "__main__":
    print("🎯 Tutor AI Database Migration Tool")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not os.path.exists('data'):
        print("❌ 'data' directory not found. Please run this from your project root directory.")
        exit(1)
    
    # Backup reminder
    print("\n⚠️  IMPORTANT: This will modify your database!")
    print("It's recommended to backup your data/tutor_ai.db file first.")
    
    response = input("\nProceed with migration? (yes/no): ").strip().lower()
    
    if response == 'yes':
        success = migrate_database()
        
        if success:
            verified = verify_database()
            if verified:
                print("\n🎉 Your database is now ready for all the new features!")
                print("\n💡 Next steps:")
                print("  1. Run your Flask app: python web/app.py")
                print("  2. Test the new session entry with topic assessment")
                print("  3. Check student progress views for the enhanced displays")
            else:
                print("\n⚠️  Some issues were found. Please check the errors above.")
        else:
            print("\n❌ Migration failed. Your database has not been modified.")
    else:
        print("\n Migration cancelled.")