import sqlite3
import os
from flask import current_app, g
from contextlib import contextmanager

def get_db_path():
    """Get the absolute path to the database."""
    # Get current working directory (should be web/)
    current_dir = os.getcwd()
    # Go up one level to project root, then to data/
    db_path = os.path.join(os.path.dirname(current_dir), 'data', 'tutor_ai.db')
    return os.path.abspath(db_path)

def get_db():
    """Get database connection."""
    if 'db' not in g:
        db_path = get_db_path()
        print(f"Database path: {db_path}")
        print(f"Database exists: {os.path.exists(db_path)}")
        
        g.db = sqlite3.connect(db_path)
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    """Close database connection."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

@contextmanager
def get_db_connection():
    """Context manager for database connections."""
    db_path = get_db_path()
    
    print(f"Connecting to database at: {db_path}")
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_app(app):
    """Initialize database with Flask app."""
    app.teardown_appcontext(close_db)