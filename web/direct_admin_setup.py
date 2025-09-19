#!/usr/bin/env python3
"""Direct PostgreSQL admin setup script"""

import sys
import os

# Try to import psycopg2 with different approaches
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    print("✅ psycopg2 imported successfully")
except ImportError as e:
    print(f"❌ Failed to import psycopg2: {e}")
    print("🔧 Trying to install psycopg2-binary...")
    os.system("python -m pip install psycopg2-binary")
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        print("✅ psycopg2 imported after installation")
    except ImportError:
        print("❌ Still can't import psycopg2. Please install manually.")
        sys.exit(1)

from werkzeug.security import generate_password_hash

# Railway PostgreSQL connection (external URL)
DATABASE_URL = "postgresql://postgres:NAjDrYiSrjQqeIOyIqAJUbXtIJIfGkzX@tramway.proxy.rlwy.net:47230/railway"

def setup_admin_direct():
    """Setup admin user directly in PostgreSQL"""
    
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
    print(f"   Password Hash: {password_hash[:50]}...")
    
    try:
        # Connect to PostgreSQL
        print(f"\n🔌 Connecting to PostgreSQL...")
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Clear existing users
        print("🧹 Clearing existing users...")
        cursor.execute("DELETE FROM tutors")
        
        # Create admin user
        print("👤 Creating admin user...")
        cursor.execute("""
            INSERT INTO tutors (username, password_hash, full_name, email, active)
            VALUES (%s, %s, %s, %s, %s)
        """, (username, password_hash, full_name, email, True))
        
        # Commit changes
        conn.commit()
        
        # Verify creation
        cursor.execute("SELECT id, username, full_name, email, active FROM tutors WHERE username = %s", (username,))
        result = cursor.fetchone()
        
        if result:
            print(f"\n✅ Admin user created successfully:")
            print(f"   ID: {result['id']}")
            print(f"   Username: {result['username']}")
            print(f"   Full Name: {result['full_name']}")
            print(f"   Email: {result['email']}")
            print(f"   Active: {result['active']}")
            
            # Check total count
            cursor.execute("SELECT COUNT(*) as count FROM tutors")
            count_result = cursor.fetchone()
            print(f"\n📊 Total users in database: {count_result['count']}")
            
            print(f"\n🎉 SUCCESS! You can now log in with:")
            print(f"   Username: {username}")
            print(f"   Password: {password}")
            print(f"\n💡 Use the admin interface to add more users once logged in.")
        else:
            print("❌ Failed to verify admin user creation")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Direct PostgreSQL Admin Setup")
    print("=" * 50)
    setup_admin_direct()