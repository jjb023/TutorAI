#!/usr/bin/env python3
"""
One-time script to hash all existing passwords
Run this ONCE to migrate from plain text to hashed passwords
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from werkzeug.security import generate_password_hash
from database import TutorAIDatabase
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def migrate_passwords():
    """Hash all existing passwords"""
    db_path = os.path.join('..', '..', 'data', 'tutor_ai.db')
    db = TutorAIDatabase(db_path)
    
    # Get all tutors
    db.cursor.execute("SELECT id, username FROM tutors")
    tutors = db.cursor.fetchall()
    
    for tutor_id, username in tutors:
        # Get password from environment or use default
        if username == 'admin':
            password = os.getenv('ADMIN_PASSWORD', 'admin123')
        elif username == 'tutor1':
            password = os.getenv('TUTOR1_PASSWORD', 'password')
        elif username == 'tutor2':
            password = os.getenv('TUTOR2_PASSWORD', 'password')
        else:
            password = os.getenv('DEFAULT_TUTOR_PASSWORD', 'password')
        
        # Generate hash
        hashed = generate_password_hash(password)
        
        # Update database
        db.cursor.execute(
            "UPDATE tutors SET password_hash = ? WHERE id = ?",
            (hashed, tutor_id)
        )
        
        print(f"✅ Updated password for {username}")
    
    db.connection.commit()
    db.close()
    print("\n🔐 All passwords have been secured!")
    print("⚠️  Remember to set SETUP_MODE=false in production!")

if __name__ == "__main__":
    migrate_passwords()