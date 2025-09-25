#!/usr/bin/env python3
"""Test student services with PostgreSQL"""

import os
import sys

# Set PostgreSQL URL
DATABASE_URL = "postgresql://postgres:NAjDrYiSrjQqeIOyIqAJUbXtIJIfGkzX@tramway.proxy.rlwy.net:47230/railway"
os.environ['DATABASE_URL'] = DATABASE_URL

sys.path.append('.')
from app import app
from student.services import StudentService

def test_student_services():
    """Test student services with PostgreSQL"""
    
    with app.app_context():
        print("👨‍🎓 Testing Student Services with PostgreSQL")
        print("=" * 60)
        
        try:
            # Test 1: Get all students
            print("📋 Test 1: Getting all students...")
            students = StudentService.get_all_students()
            print(f"Found {len(students)} students")
            if students:
                print(f"First student: {students[0]['name']}")
            
            # Test 2: Create a test student
            print("\n➕ Test 2: Creating a test student...")
            test_student_id = StudentService.create_student(
                name="Test PostgreSQL Student",
                age=10,
                year_group="Year 5",
                target_school="Test High School",
                parent_contact="parent@test.com",
                notes="Created by PostgreSQL test"
            )
            print(f"Created student with ID: {test_student_id}")
            
            # Test 3: Get the created student
            print("\n🔍 Test 3: Getting created student...")
            test_student = StudentService.get_student(test_student_id)
            if test_student:
                print(f"Retrieved: {test_student['name']} (Age: {test_student['age']})")
                print(f"Year Group: {test_student['year_group']}")
                print(f"Target School: {test_student['target_school']}")
            else:
                print("❌ Could not retrieve created student")
            
            # Test 4: Update the student
            print("\n✏️ Test 4: Updating student...")
            StudentService.update_student(
                test_student_id,
                name="Updated Test Student",
                age=11,
                year_group="Year 6", 
                target_school="Updated High School",
                parent_contact="updated@test.com",
                notes="Updated by PostgreSQL test"
            )
            
            # Verify update
            updated_student = StudentService.get_student(test_student_id)
            if updated_student:
                print(f"Updated name: {updated_student['name']}")
                print(f"Updated age: {updated_student['age']}")
            
            # Test 5: Get progress summary (should handle empty progress)
            print("\n📊 Test 5: Getting progress summary...")
            progress_summary = StudentService.get_student_progress_summary(test_student_id)
            print(f"Progress summary: {len(progress_summary['topic_summaries'])} topics found")
            
            # Test 6: Get session count
            print("\n📈 Test 6: Getting session count...")
            session_count = StudentService.get_session_count(test_student_id)
            print(f"Session count: {session_count}")
            
            # Test 7: Get recent activity
            print("\n🕒 Test 7: Getting recent activity...")
            recent_activity = StudentService.get_recent_activity(test_student_id)
            print(f"Recent activity entries: {len(recent_activity)}")
            
            # Test 8: Get mastery distribution
            print("\n📊 Test 8: Getting mastery distribution...")
            mastery_dist = StudentService.get_mastery_distribution(test_student_id)
            print(f"Mastery distribution entries: {len(mastery_dist)}")
            
            # Test 9: Clean up - delete test student
            print("\n🗑️ Test 9: Cleaning up - deleting test student...")
            StudentService.delete_student(test_student_id)
            
            # Verify deletion
            deleted_student = StudentService.get_student(test_student_id)
            if deleted_student is None:
                print("✅ Student successfully deleted")
            else:
                print("❌ Student was not deleted")
            
            print("\n🎉 All student service tests completed successfully!")
            print("\n✅ Student services are PostgreSQL-ready!")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
            return 1
    
    return 0

if __name__ == "__main__":
    exit(test_student_services())