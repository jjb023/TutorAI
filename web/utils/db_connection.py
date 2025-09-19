import os
import sqlite3
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
except ImportError:
    psycopg2 = None

class DatabaseConnection:
    """Database connection wrapper that works with both SQLite and PostgreSQL"""
    
    def __init__(self):
        self.database_url = os.environ.get('DATABASE_URL')
        self.connection = None
        self.cursor = None
        self.is_postgres = False
        
    def connect(self):
        """Connect to database (PostgreSQL or SQLite)"""
        if self.database_url:
            # PostgreSQL for production
            if not psycopg2:
                raise ImportError("psycopg2 required for PostgreSQL")
            
            # Fix Railway's postgres:// URL
            if self.database_url.startswith('postgres://'):
                self.database_url = self.database_url.replace('postgres://', 'postgresql://', 1)
            
            self.connection = psycopg2.connect(self.database_url)
            self.cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            self.is_postgres = True
        else:
            # SQLite for development
            from flask import current_app
            db_path = current_app.config.get('DATABASE_PATH', '../data/tutor_ai.db')
            
            if not os.path.isabs(db_path):
                project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                db_path = os.path.join(project_root, db_path)
            
            self.connection = sqlite3.connect(db_path)
            self.connection.row_factory = sqlite3.Row
            self.cursor = self.connection.cursor()
            self.is_postgres = False
        
        return self
    
    def execute(self, query, params=None):
        """Execute query with proper parameter formatting"""
        if self.is_postgres:
            # PostgreSQL uses %s for parameters
            if params and '?' in query:
                query = query.replace('?', '%s')
            self.cursor.execute(query, params or ())
        else:
            # SQLite uses ? for parameters
            self.cursor.execute(query, params or ())
        return self.cursor
    
    def fetchone(self):
        """Fetch one result"""
        result = self.cursor.fetchone()
        if result and self.is_postgres:
            # Convert to dict if PostgreSQL
            return dict(result) if result else None
        return result
    
    def fetchall(self):
        """Fetch all results"""
        results = self.cursor.fetchall()
        if results and self.is_postgres:
            # Convert to list of dicts if PostgreSQL
            return [dict(row) for row in results]
        return results
    
    def commit(self):
        """Commit transaction"""
        self.connection.commit()
    
    def rollback(self):
        """Rollback transaction"""
        self.connection.rollback()
    
    def close(self):
        """Close connection"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if exc_type:
            self.rollback()
        else:
            self.commit()
        self.close()

def get_db():
    """Get database connection for Flask app"""
    return DatabaseConnection()