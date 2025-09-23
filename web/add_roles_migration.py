#!/usr/bin/env python3
"""Add roles to tutors table"""

import os
import sys

# Set PostgreSQL URL
DATABASE_URL = "postgresql://postgres:NAjDrYiSrjQqeIOyIqAJUbXtIJIfGkzX@tramway.proxy.rlwy.net:47230/railway"
os.environ['DATABASE_URL'] = DATABASE_URL

sys.path.append('.')
from app import app
from utils.db_connection import get_db

def add_role_column():
    """Add role column to tutors table"""
    
    with app.app_context():
        with get_db() as db:
            try:
                # Check if role column already exists
                if db.is_postgres:
                    result = db.execute("""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name = 'tutors' AND column_name = 'role'
                    """).fetchone()
                else:
                    # SQLite
                    result = db.execute("PRAGMA table_info(tutors)").fetchall()
                    role_exists = any('role' in str(row) for row in result)
                    result = {'column_name': 'role'} if role_exists else None
                
                if result:
                    print("✅ Role column already exists")
                else:
                    print("🔄 Adding role column to tutors table...")
                    
                    # Add role column with default value 'tutor'
                    db.execute("ALTER TABLE tutors ADD COLUMN role VARCHAR(20) DEFAULT 'tutor'")
                    
                    print("✅ Role column added successfully")
                
                # Update existing admin user to have admin role
                print("🔄 Setting admin user role...")
                db.execute("UPDATE tutors SET role = 'admin' WHERE username = 'admin'")
                
                # Verify the update
                result = db.execute("SELECT username, role FROM tutors WHERE username = 'admin'").fetchone()
                if result:
                    if isinstance(result, dict):
                        print(f"✅ Admin user role: {result['role']}")
                    else:
                        print(f"✅ Admin user role: {result[1]}")
                
                print("🎉 Role migration complete!")
                
            except Exception as e:
                print(f"❌ Migration failed: {e}")
                import traceback
                traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Adding Roles to Tutors Table")
    print("=" * 50)
    add_role_column()