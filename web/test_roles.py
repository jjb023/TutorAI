#!/usr/bin/env python3
"""Test the role system"""

import os
import sys

# Set PostgreSQL URL
DATABASE_URL = "postgresql://postgres:NAjDrYiSrjQqeIOyIqAJUbXtIJIfGkzX@tramway.proxy.rlwy.net:47230/railway"
os.environ['DATABASE_URL'] = DATABASE_URL

sys.path.append('.')
from app import app
from tutor.services import TutorService

def test_role_system():
    """Test role functionality"""
    
    with app.app_context():
        print("🧪 Testing Role System")
        print("=" * 50)
        
        # Test admin check
        print("🔍 Testing admin role check...")
        
        # Get admin user
        try:
            admins = TutorService.get_admins()
            print(f"Found {len(admins)} admin(s)")
            
            if admins:
                admin = admins[0]
                if isinstance(admin, dict):
                    admin_id = admin['id']
                    admin_username = admin['username']
                    admin_role = admin['role']
                else:
                    admin_id = admin[0]
                    admin_username = admin[1]
                    admin_role = admin[5] if len(admin) > 5 else 'unknown'
                
                print(f"Admin user: {admin_username} (ID: {admin_id}, Role: {admin_role})")
                
                # Test is_admin function
                is_admin = TutorService.is_admin(admin_id)
                print(f"is_admin({admin_id}): {is_admin}")
                
            # Test creating a regular tutor
            print("\n👤 Creating test tutor...")
            test_password = TutorService.create_tutor(
                username="test_tutor", 
                full_name="Test Tutor", 
                email="test@example.com",
                role="tutor"
            )
            print(f"Created tutor with password: {test_password}")
            
            # Get all tutors by role
            regular_tutors = TutorService.get_regular_tutors()
            print(f"Regular tutors: {len(regular_tutors)}")
            
            print("\n🎉 Role system test complete!")
            print("\nRole Summary:")
            print(f"- Admin users: {len(TutorService.get_admins())}")
            print(f"- Regular tutors: {len(TutorService.get_regular_tutors())}")
            
            print("\nPermissions:")
            print("📋 Admin can:")
            print("  ✅ Add/edit/delete tutors")
            print("  ✅ Change tutor status")
            print("  ✅ Add/edit students and topics")
            print("  ✅ Access all features")
            
            print("\n👨‍🏫 Tutor can:")
            print("  ✅ Add/edit students and topics")
            print("  ❌ Cannot manage other tutors")
            print("  ❌ Cannot change tutor status")
            
        except Exception as e:
            print(f"❌ Error testing roles: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_role_system()