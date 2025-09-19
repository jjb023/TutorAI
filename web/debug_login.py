#!/usr/bin/env python3
"""Debug script to check admin user credentials"""

import os
import sys
sys.path.append('.')

from app import app
from utils.db_connection import get_db
from werkzeug.security import check_password_hash

def check_admin_user():
    """Check admin user in database"""
    try:
        with get_db() as db:
            print("🔍 Checking database for admin user...")
            
            # Get admin user info
            result = db.execute("""
                SELECT id, username, full_name, email, password_hash, active 
                FROM tutors 
                WHERE username = 'admin'
            """).fetchone()
            
            if result:
                if isinstance(result, dict):
                    print(f"✅ Admin user found:")
                    print(f"   ID: {result['id']}")
                    print(f"   Username: {result['username']}")
                    print(f"   Full Name: {result['full_name']}")
                    print(f"   Email: {result['email']}")
                    print(f"   Active: {result['active']}")
                    print(f"   Password Hash: {result['password_hash'][:50]}...")
                    return result['password_hash']
                else:
                    print(f"✅ Admin user found:")
                    print(f"   ID: {result[0]}")
                    print(f"   Username: {result[1]}")
                    print(f"   Full Name: {result[2]}")
                    print(f"   Email: {result[3]}")
                    print(f"   Active: {result[5]}")
                    print(f"   Password Hash: {result[4][:50]}...")
                    return result[4]
            else:
                print("❌ Admin user not found!")
                return None
                
    except Exception as e:
        print(f"❌ Database error: {e}")
        return None

def test_password(password_hash, test_password):
    """Test if password matches hash"""
    print(f"\n🔐 Testing password: '{test_password}'")
    
    if password_hash == 'temp_password_hash':
        print("⚠️ Password is still temporary - using setup mode")
        # Check environment variables
        admin_pass = os.getenv('ADMIN_PASSWORD', 'admin123')
        setup_mode = os.getenv('SETUP_MODE', 'false').lower() == 'true'
        print(f"   Setup mode: {setup_mode}")
        print(f"   Expected password from env: {admin_pass}")
        
        if setup_mode and test_password == admin_pass:
            print("✅ Password matches environment variable")
            return True
        else:
            print("❌ Setup mode disabled or password doesn't match")
            return False
    else:
        # Test against hash
        if check_password_hash(password_hash, test_password):
            print("✅ Password matches hash")
            return True
        else:
            print("❌ Password does not match hash")
            return False

if __name__ == "__main__":
    with app.app_context():
        print("🚀 Debug Login Script")
        print("=" * 50)
        
        # Check if admin exists
        password_hash = check_admin_user()
        
        if password_hash:
            print(f"\n🔍 Environment variables:")
            print(f"   SETUP_MODE: {os.getenv('SETUP_MODE', 'false')}")
            print(f"   ADMIN_PASSWORD: {os.getenv('ADMIN_PASSWORD', 'admin123')}")
            
            # Test common passwords
            test_passwords = ['admin123', 'password', 'admin', 'tutor123']
            
            for pwd in test_passwords:
                if test_password(password_hash, pwd):
                    print(f"\n🎉 SUCCESS! Use username 'admin' with password '{pwd}'")
                    break
            else:
                print("\n❌ None of the test passwords worked")
                print("💡 Try setting SETUP_MODE=true environment variable")