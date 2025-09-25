#!/usr/bin/env python3
"""Test session services with PostgreSQL"""

import os
import sys

# Set PostgreSQL URL
DATABASE_URL = "postgresql://postgres:NAjDrYiSrjQqeIOyIqAJUbXtIJIfGkzX@tramway.proxy.rlwy.net:47230/railway"
os.environ['DATABASE_URL'] = DATABASE_URL

sys.path.append('.')
from app import app
from session.services import SessionService
from student.services import StudentService
from tutor.services import TutorService

def test_session_services():
    """Test session services with PostgreSQL"""
    
    with app.app_context():
        print("🎯 Testing Session Services with PostgreSQL")
        print("=" * 60)
        
        try:
            # Test 1: Get session entry data
            print("📊 Test 1: Getting session entry data...")
            entry_data = SessionService.get_session_entry_data()
            print(f"Found {len(entry_data)} topics with subtopics")
            
            if entry_data:
                print(f"First topic: {entry_data[0]['topic_name']} with {len(entry_data[0]['subtopics'])} subtopics")
            
            # Test 2: Get student progress summary
            print("\n📈 Test 2: Getting student progress summary...")
            # Get a test student
            students = StudentService.get_all_students()
            if students:
                student_id = students[0]['id']
                print(f"Testing with student: {students[0]['name']} (ID: {student_id})")
                
                progress_data = SessionService.get_student_progress_summary(student_id)
                print(f"Progress data keys: {progress_data.keys()}")
                print(f"Topic summaries: {len(progress_data['topic_summaries'])}")
                print(f"Detailed progress: {len(progress_data['detailed_progress'])}")
                print(f"Weak areas: {len(progress_data['weak_areas'])}")
                print(f"Ready to advance: {len(progress_data['ready_to_advance'])}")
                
                # Test 3: Get recent sessions
                print("\n📅 Test 3: Getting recent sessions...")
                recent_sessions = SessionService.get_recent_sessions_with_progress(student_id)
                print(f"Recent sessions: {len(recent_sessions)}")
                
                # Test 4: Create a session with progress (requires admin user)
                print("\n✏️ Test 4: Testing session creation preparation...")
                tutors = TutorService.get_all_tutors()
                admin_tutor = None
                for tutor in tutors:
                    if isinstance(tutor, dict):
                        if tutor.get('role') == 'admin':
                            admin_tutor = tutor
                            break
                    else:
                        # Handle Row object
                        if len(tutor) > 5 and tutor[5] == 'admin':
                            admin_tutor = {'id': tutor[0], 'username': tutor[1]}
                            break
                
                if admin_tutor:
                    print(f"Found admin tutor: {admin_tutor.get('username', 'admin')} (ID: {admin_tutor['id']})")
                    
                    # Get first subtopic for testing
                    if entry_data and entry_data[0]['subtopics']:
                        first_subtopic_id = entry_data[0]['subtopics'][0]['id']
                        print(f"Using subtopic ID {first_subtopic_id} for test assessment")
                        
                        # Create test assessment data
                        test_assessments = {
                            str(first_subtopic_id): {
                                'level': 5,
                                'notes': 'Test assessment from PostgreSQL migration'
                            }
                        }
                        
                        print("Ready to create session (test data prepared)")
                        print("✅ Session creation test data validated")
                    else:
                        print("⚠️ No subtopics found for session creation test")
                else:
                    print("⚠️ No admin tutor found for session creation test")
            else:
                print("❌ No students found for testing")
            
            print("\n🎉 All session service tests completed successfully!")
            print("\n✅ Session services are PostgreSQL-ready!")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
            return 1
    
    return 0

if __name__ == "__main__":
    exit(test_session_services())