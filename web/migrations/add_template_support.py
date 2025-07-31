#!/usr/bin/env python3
"""
Add template support to questions table
"""

import sqlite3
import os

def add_template_columns():
    db_path = os.path.join('..', '..', 'data', 'tutor_ai.db')
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Add columns to existing questions table
    cursor.execute("""
        ALTER TABLE questions 
        ADD COLUMN is_template BOOLEAN DEFAULT 0
    """)
    
    cursor.execute("""
        ALTER TABLE questions 
        ADD COLUMN template_params TEXT
    """)
    
    # Template params will store JSON like:
    # {"num1": {"type": "int", "min": 1, "max": 20}, "num2": {"type": "int", "min": 1, "max": 20}}
    
    conn.commit()
    conn.close()