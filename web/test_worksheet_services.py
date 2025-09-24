#!/usr/bin/env python3
"""Test worksheet services with PostgreSQL"""

import os
import sys

# Set PostgreSQL URL
DATABASE_URL = "postgresql://postgres:NAjDrYiSrjQqeIOyIqAJUbXtIJIfGkzX@tramway.proxy.rlwy.net:47230/railway"
os.environ['DATABASE_URL'] = DATABASE_URL

sys.path.append('.')
from app import app
from worksheet.services import QuestionService, WorksheetService

def test_worksheet_services():
    """Test worksheet services with PostgreSQL"""
    
    with app.app_context():
        print("🧪 Testing Worksheet Services with PostgreSQL")
        print("=" * 60)
        
        try:
            # Test 1: Get question stats
            print("📊 Test 1: Getting question statistics...")
            stats = QuestionService.get_question_stats(1)  # Try first subtopic
            print(f"Stats for subtopic 1: {stats}")
            
            # Test 2: Get questions by subtopic
            print("\n📝 Test 2: Getting questions by subtopic...")
            questions = QuestionService.get_questions_by_subtopic(1, difficulty_level=1)
            print(f"Found {len(questions)} easy questions for subtopic 1")
            if questions:
                print(f"Sample question: {questions[0]['question_text'][:50]}...")
            
            # Test 3: Get single question
            if questions:
                print("\n🔍 Test 3: Getting single question...")
                question_id = questions[0]['id']
                single_question = QuestionService.get_question(question_id)
                if single_question:
                    print(f"Retrieved question {question_id}: {single_question['question_text'][:50]}...")
                
            # Test 4: Create a test student (if not exists)
            print("\n👤 Test 4: Checking for test student...")
            from utils.db_connection import get_db
            
            with get_db() as db:
                # Check if test student exists
                result = db.execute("SELECT id FROM students WHERE name = ?", ('Test Student',)).fetchone()
                if not result:
                    # Create test student
                    db.execute("INSERT INTO students (name, age, year_group) VALUES (?, ?, ?)", 
                              ('Test Student', 8, 'Year 3'))
                    result = db.execute("SELECT id FROM students WHERE name = ?", ('Test Student',)).fetchone()
                
                if isinstance(result, dict):
                    student_id = result['id']
                else:
                    student_id = result[0]
                
                print(f"Using student ID: {student_id}")
                
                # Get admin tutor ID
                tutor_result = db.execute("SELECT id FROM tutors WHERE username = ?", ('admin',)).fetchone()
                if isinstance(tutor_result, dict):
                    tutor_id = tutor_result['id']
                else:
                    tutor_id = tutor_result[0]
                
                print(f"Using tutor ID: {tutor_id}")
            
            # Test 5: Get recommended difficulty
            print("\n🎯 Test 5: Getting recommended difficulty...")
            difficulty_level, distribution = WorksheetService.get_recommended_difficulty(student_id, 1)
            print(f"Recommended difficulty: {difficulty_level}")
            print(f"Distribution: {distribution}")
            
            # Test 6: Generate a small worksheet
            print("\n📋 Test 6: Generating worksheet...")
            worksheet_id = WorksheetService.generate_worksheet(
                student_id=student_id,
                subtopic_id=1,
                tutor_id=tutor_id,
                total_questions=3,  # Small test worksheet
                title="Test Worksheet"
            )
            print(f"Generated worksheet ID: {worksheet_id}")
            
            # Test 7: Get worksheet details
            print("\n📄 Test 7: Getting worksheet details...")
            worksheet_data = WorksheetService.get_worksheet(worksheet_id)
            if worksheet_data:
                worksheet = worksheet_data['worksheet']
                questions_list = worksheet_data['questions']
                print(f"Worksheet: {worksheet['title']}")
                print(f"Student: {worksheet['student_name']}")
                print(f"Questions: {len(questions_list)}")
                
                for i, q in enumerate(questions_list[:2], 1):  # Show first 2 questions
                    question_text = q.get('custom_question_text') or q.get('original_text', '')
                    print(f"  Q{i}: {question_text[:50]}...")
            
            print("\n🎉 All worksheet service tests completed successfully!")
            print("\n✅ Worksheet services are PostgreSQL-ready!")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
            return 1
    
    return 0

if __name__ == "__main__":
    exit(test_worksheet_services())