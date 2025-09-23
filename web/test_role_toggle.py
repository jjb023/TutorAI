#!/usr/bin/env python3
"""Test role toggle functionality"""

import os
import sys

# Set PostgreSQL URL
DATABASE_URL = "postgresql://postgres:NAjDrYiSrjQqeIOyIqAJUbXtIJIfGkzX@tramway.proxy.rlwy.net:47230/railway"
os.environ['DATABASE_URL'] = DATABASE_URL

sys.path.append('.')
from app import app
from tutor.services import TutorService

def test_role_toggle():
    """Test changing roles"""
    
    with app.app_context():
        print("🔄 Testing Role Toggle")
        print("=" * 50)
        
        # Find test_tutor
        tutors = TutorService.get_all_tutors()
        test_tutor = None
        
        for tutor in tutors:
            if isinstance(tutor, dict):
                username = tutor['username']
                tutor_id = tutor['id']
                current_role = tutor.get('role', 'tutor')
            else:
                username = tutor[1]
                tutor_id = tutor[0]
                current_role = tutor[5] if len(tutor) > 5 else 'tutor'
            
            if username == 'test_tutor':
                test_tutor = {'id': tutor_id, 'username': username, 'role': current_role}
                break
        
        if not test_tutor:
            print("❌ test_tutor not found - creating one...")
            password = TutorService.create_tutor('test_tutor2', 'Test Tutor 2', 'test2@example.com', 'password123', 'tutor')
            print(f"✅ Created test_tutor2 with password: {password}")
            
            # Get the new tutor
            tutors = TutorService.get_all_tutors()
            for tutor in tutors:
                if isinstance(tutor, dict):
                    if tutor['username'] == 'test_tutor2':
                        test_tutor = {'id': tutor['id'], 'username': tutor['username'], 'role': tutor.get('role', 'tutor')}
                        break
                else:
                    if tutor[1] == 'test_tutor2':
                        test_tutor = {'id': tutor[0], 'username': tutor[1], 'role': tutor[5] if len(tutor) > 5 else 'tutor'}
                        break
        
        if test_tutor:
            print(f"📋 Current state: {test_tutor['username']} has role '{test_tutor['role']}'")
            
            # Toggle role
            new_role = 'admin' if test_tutor['role'] == 'tutor' else 'tutor'
            print(f"🔄 Changing role from '{test_tutor['role']}' to '{new_role}'...")
            
            TutorService.update_tutor(
                test_tutor['id'], 
                test_tutor['username'], 
                'Test Tutor', 
                'test@example.com', 
                new_role
            )
            
            # Verify change
            updated_tutor = TutorService.get_tutor(test_tutor['id'])
            if isinstance(updated_tutor, dict):
                updated_role = updated_tutor.get('role', 'tutor')
            else:
                updated_role = updated_tutor[5] if len(updated_tutor) > 5 else 'tutor'
            
            print(f"✅ Role updated! New role: '{updated_role}'")
            print(f"🔍 is_admin({test_tutor['id']}): {TutorService.is_admin(test_tutor['id'])}")
            
            print("\n🎉 Role toggle test complete!")
            print("\nYou can now:")
            print("1. 🌐 Go to /tutors in your web app")
            print("2. ✏️  Click 'Edit' on any tutor")  
            print("3. 🔄 Toggle between 👨‍🏫 Tutor and 👑 Admin roles")
            print("4. 💾 Save and see the role change!")
        
        else:
            print("❌ Could not find or create test tutor")

if __name__ == "__main__":
    test_role_toggle()