#!/usr/bin/env python3
"""Setup initial admin user in PostgreSQL database"""

import os
import sys
from werkzeug.security import generate_password_hash

# Your PostgreSQL connection string
DATABASE_URL = "postgresql://postgres:NAjDrYiSrjQqeIOyIqAJUbXtIJIfGkzX@postgres.railway.internal:5432/railway"

# Set environment variable
os.environ['DATABASE_URL'] = DATABASE_URL

# Import app components
sys.path.append('.')
from app import app
from utils.db_connection import get_db

def setup_admin():
    """Create the initial admin user"""
    
    # Admin credentials
    username = "admin"
    password = "JoshBeal"
    full_name = "Josh Beal"
    email = "josh@tutorai.com"
    
    print(f"🔐 Setting up admin user:")
    print(f"   Username: {username}")
    print(f"   Password: {password}")
    print(f"   Full Name: {full_name}")
    print(f"   Email: {email}")
    
    # Hash the password
    password_hash = generate_password_hash(password)
    
    with app.app_context():
        try:
            with get_db() as db:
                # First, clear any existing users to ensure clean start
                print("\n🧹 Clearing existing users...")
                db.execute("DELETE FROM tutors")
                
                # Create the admin user
                print("👤 Creating admin user...")
                db.execute("""
                    INSERT INTO tutors (username, password_hash, full_name, email, active)
                    VALUES (%s, %s, %s, %s, %s)
                """, (username, password_hash, full_name, email, True))
                
                # Verify creation
                result = db.execute(
                    "SELECT id, username, full_name, email, active FROM tutors WHERE username = %s",
                    (username,)
                ).fetchone()
                
                if result:
                    if isinstance(result, dict):
                        print(f"\n✅ Admin user created successfully:")
                        print(f"   ID: {result['id']}")
                        print(f"   Username: {result['username']}")
                        print(f"   Full Name: {result['full_name']}")
                        print(f"   Email: {result['email']}")
                        print(f"   Active: {result['active']}")
                    else:
                        print(f"\n✅ Admin user created successfully:")
                        print(f"   ID: {result[0]}")
                        print(f"   Username: {result[1]}")
                        print(f"   Full Name: {result[2]}")
                        print(f"   Email: {result[3]}")
                        print(f"   Active: {result[4]}")
                    
                    # Check total user count
                    count_result = db.execute("SELECT COUNT(*) FROM tutors").fetchone()
                    if isinstance(count_result, dict):
                        count = count_result['count']
                    else:
                        count = count_result[0]
                    
                    print(f"\n📊 Total users in database: {count}")
                    print(f"\n🎉 SUCCESS! You can now log in with:")
                    print(f"   Username: {username}")
                    print(f"   Password: {password}")
                    print(f"\n💡 Use the admin interface to add more users once logged in.")
                else:
                    print("❌ Failed to verify admin user creation")
                    
        except Exception as e:
            print(f"❌ Error setting up admin: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    print("🚀 TutorAI Admin Setup")
    print("=" * 50)
    setup_admin()