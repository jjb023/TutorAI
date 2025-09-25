#!/usr/bin/env python3
"""Test student detail route logic"""

import os
import sys

# Set PostgreSQL URL
DATABASE_URL = "postgresql://postgres:NAjDrYiSrjQqeIOyIqAJUbXtIJIfGkzX@tramway.proxy.rlwy.net:47230/railway"
os.environ['DATABASE_URL'] = DATABASE_URL

sys.path.append('.')
from app import app
from student.services import StudentService

def test_student_detail_logic():
    """Test the exact logic from student detail route"""
    
    with app.app_context():
        print("🔍 Testing Student Detail Route Logic")
        print("=" * 50)
        
        try:
            # Get all students first
            students = StudentService.get_all_students()
            print(f"Found {len(students)} students")
            
            if students:
                student_id = students[0]['id']
                student_name = students[0]['name']
                print(f"\n📊 Testing detail logic for: {student_name} (ID: {student_id})")
                
                # Get student info
                student = StudentService.get_student(student_id)
                if not student:
                    print("❌ Student not found")
                    return
                
                print("✅ Student found")
                
                # Get comprehensive progress data  
                progress_data = StudentService.get_student_progress_summary(student_id)
                print(f"Progress data: {progress_data}")
                
                # Handle case where progress_data might be None or missing topic_summaries
                if not progress_data or 'topic_summaries' not in progress_data:
                    progress_data = {'topic_summaries': [], 'detailed_progress': [], 'weak_areas': [], 'ready_to_advance': []}
                    print("⚠️ Using default empty progress data")
                
                print(f"Topic summaries count: {len(progress_data['topic_summaries'])}")
                
                # Calculate overall statistics (handle None values and empty lists)
                total_subtopics = sum(topic['total_subtopics'] or 0 for topic in progress_data['topic_summaries'])
                topics_assessed = sum(topic['assessed_subtopics'] or 0 for topic in progress_data['topic_summaries'])
                
                print(f"Total subtopics: {total_subtopics}")
                print(f"Topics assessed: {topics_assessed}")
                
                overall_progress = 0
                if progress_data['topic_summaries'] and len(progress_data['topic_summaries']) > 0:
                    print("Calculating overall progress...")
                    completion_percentages = [float(topic['completion_percentage'] or 0) for topic in progress_data['topic_summaries']]
                    print(f"Completion percentages: {completion_percentages}")
                    
                    total_percentage = sum(completion_percentages)
                    num_topics = len(progress_data['topic_summaries'])
                    print(f"Total percentage: {total_percentage}, Num topics: {num_topics}")
                    
                    if num_topics > 0:
                        overall_progress = total_percentage / num_topics
                        print(f"Overall progress: {overall_progress}")
                    else:
                        print("⚠️ No topics to calculate progress from")
                else:
                    print("⚠️ No topic summaries available")
                
                # Get session count
                session_count = StudentService.get_session_count(student_id)
                print(f"Session count: {session_count}")
                
                # Get last session date
                last_session_date = student.get('last_session_date')
                print(f"Last session date: {last_session_date}")
                
                print(f"\n✅ All calculations completed successfully!")
                print(f"Final results:")
                print(f"  - Total subtopics: {total_subtopics}")
                print(f"  - Topics assessed: {topics_assessed}")  
                print(f"  - Overall progress: {round(overall_progress, 1)}%")
                print(f"  - Session count: {session_count}")
                
            else:
                print("❌ No students found to test")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_student_detail_logic()