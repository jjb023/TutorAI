#!/usr/bin/env python3
"""Test student routes to debug None value issues"""

import os
import sys

# Set PostgreSQL URL
DATABASE_URL = "postgresql://postgres:NAjDrYiSrjQqeIOyIqAJUbXtIJIfGkzX@tramway.proxy.rlwy.net:47230/railway"
os.environ['DATABASE_URL'] = DATABASE_URL

sys.path.append('.')
from app import app
from student.services import StudentService

def test_progress_summary():
    """Test what the progress summary returns"""
    
    with app.app_context():
        print("🔍 Testing Student Progress Summary")
        print("=" * 50)
        
        try:
            # Get all students first
            students = StudentService.get_all_students()
            print(f"Found {len(students)} students")
            
            if students:
                student_id = students[0]['id']
                student_name = students[0]['name']
                print(f"\n📊 Testing progress for: {student_name} (ID: {student_id})")
                
                # Get progress data
                progress_data = StudentService.get_student_progress_summary(student_id)
                print(f"Progress data keys: {progress_data.keys()}")
                
                print(f"\nTopic summaries: {len(progress_data['topic_summaries'])}")
                
                # Check each topic summary for None values
                for i, topic in enumerate(progress_data['topic_summaries']):
                    print(f"\nTopic {i+1}:")
                    print(f"  topic_name: {topic.get('topic_name')}")
                    print(f"  total_subtopics: {topic.get('total_subtopics')} (type: {type(topic.get('total_subtopics'))})")
                    print(f"  assessed_subtopics: {topic.get('assessed_subtopics')} (type: {type(topic.get('assessed_subtopics'))})")
                    print(f"  completion_percentage: {topic.get('completion_percentage')} (type: {type(topic.get('completion_percentage'))})")
                    
                    # Test the problematic sum operations
                    total = topic.get('total_subtopics') or 0
                    assessed = topic.get('assessed_subtopics') or 0 
                    percentage = topic.get('completion_percentage') or 0
                    print(f"  Safe values: total={total}, assessed={assessed}, percentage={percentage}")
                
                # Test the sum operations that were failing
                print(f"\n🧮 Testing sum operations:")
                total_subtopics = sum(topic['total_subtopics'] or 0 for topic in progress_data['topic_summaries'])
                topics_assessed = sum(topic['assessed_subtopics'] or 0 for topic in progress_data['topic_summaries'])
                
                print(f"Total subtopics: {total_subtopics}")
                print(f"Topics assessed: {topics_assessed}")
                
                if len(progress_data['topic_summaries']) > 0:
                    overall_progress = sum(topic['completion_percentage'] or 0 for topic in progress_data['topic_summaries']) / len(progress_data['topic_summaries'])
                    print(f"Overall progress: {overall_progress}")
                else:
                    print("No topics found")
                
                print("\n✅ All operations completed without errors!")
            else:
                print("❌ No students found to test")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_progress_summary()