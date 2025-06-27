#!/usr/bin/env python3
"""
Debug script to check session creation issue
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import TutorAIDatabase

def test_student_access():
    """Test how student data is accessed"""
    db_path = os.path.join('data', 'tutor_ai.db')
    db = TutorAIDatabase(db_path)
    
    print("🔍 Testing student data access...")
    
    # Get a student
    db.cursor.execute("SELECT * FROM students LIMIT 1")
    student = db.cursor.fetchone()
    
    if student:
        print(f"\n📋 Student data type: {type(student)}")
        print(f"Student data: {student}")
        
        # Test different access methods
        try:
            print(f"\nTrying student[1] (index): {student[1]}")  # Should be name
        except Exception as e:
            print(f"❌ Index access failed: {e}")
        
        try:
            print(f"Trying student['name']: Not possible with basic cursor")
        except Exception as e:
            print(f"❌ Dict access failed: {e}")
        
        # Now test with row_factory
        import sqlite3
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM students LIMIT 1")
        student_row = cursor.fetchone()
        
        print(f"\n📋 With row_factory - type: {type(student_row)}")
        
        try:
            print(f"Trying student_row['name']: {student_row['name']}")
        except Exception as e:
            print(f"❌ Row dict access failed: {e}")
        
        try:
            # List available keys
            print(f"Available columns: {list(student_row.keys())}")
        except:
            pass
        
        conn.close()
    else:
        print("❌ No students found in database")
    
    db.close()

def test_session_data():
    """Test session-related queries"""
    db_path = os.path.join('data', 'tutor_ai.db')
    
    import sqlite3
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    print("\n🔍 Testing session data structures...")
    
    # Test topic query
    cursor = conn.cursor()
    cursor.execute("""
        SELECT mt.id, mt.topic_name, mt.color_code
        FROM main_topics mt
        ORDER BY mt.topic_name
        LIMIT 1
    """)
    
    topic = cursor.fetchone()
    if topic:
        print(f"\n📋 Topic data: id={topic['id']}, name={topic['topic_name']}")
        
        # Test subtopic query
        cursor.execute("""
            SELECT s.id, s.subtopic_name, s.difficulty_order
            FROM subtopics s
            WHERE s.main_topic_id = ?
            LIMIT 2
        """, (topic['id'],))
        
        subtopics = cursor.fetchall()
        print(f"Found {len(subtopics)} subtopics")
        for sub in subtopics:
            print(f"  - {sub['subtopic_name']} (id: {sub['id']})")
    
    conn.close()

if __name__ == "__main__":
    print("🎯 Tutor AI Session Debug Tool")
    print("=" * 40)
    
    test_student_access()
    test_session_data()
    
    print("\n✅ Debug complete!")
    print("\n💡 If you see the student name printed successfully,")
    print("   then the issue might be in a different part of the code.")
    print("   Check the Flask app logs for the exact line causing the error.")