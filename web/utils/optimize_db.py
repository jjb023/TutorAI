# web/utils/optimize_db.py
"""
Database performance optimization script for Tutor AI.
Adds indexes, analyzes queries, and optimizes database structure.

Author: Josh Beal
Date: 2025

Usage:
    python optimize_db.py [--analyze] [--add-indexes] [--vacuum]
"""

import sqlite3
import os
import sys
import time
import argparse
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))


class DatabaseOptimizer:
    """Database optimization utilities for Tutor AI."""
    
    def __init__(self, db_path='../../data/tutor_ai.db'):
        """Initialize optimizer with database path."""
        self.db_path = db_path
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Database not found: {self.db_path}")
        
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        
        # Enable query execution time tracking
        self.conn.set_trace_callback(self._trace_callback)
        self.query_times = []
    
    def _trace_callback(self, statement):
        """Callback to track query execution."""
        # Store query for analysis (in production, be more selective)
        pass
    
    def analyze_current_indexes(self):
        """Analyze existing indexes in the database."""
        print("\n📊 Current Database Indexes:")
        print("-" * 50)
        
        # Get all indexes
        self.cursor.execute("""
            SELECT name, tbl_name, sql 
            FROM sqlite_master 
            WHERE type = 'index' 
            ORDER BY tbl_name, name
        """)
        
        indexes = self.cursor.fetchall()
        
        current_table = None
        for index_name, table_name, sql in indexes:
            if current_table != table_name:
                print(f"\n📁 Table: {table_name}")
                current_table = table_name
            
            # Skip automatic indexes
            if sql:
                print(f"  ✓ {index_name}")
            else:
                print(f"  • {index_name} (automatic)")
        
        print(f"\n📈 Total indexes: {len(indexes)}")
    
    def add_performance_indexes(self):
        """Add indexes to improve query performance."""
        print("\n🔧 Adding Performance Indexes...")
        print("-" * 50)
        
        indexes_to_add = [
            # Sessions table - frequently queried by student and date
            ("idx_sessions_student_id", 
             "CREATE INDEX IF NOT EXISTS idx_sessions_student_id ON sessions(student_id)"),
            
            ("idx_sessions_tutor_id", 
             "CREATE INDEX IF NOT EXISTS idx_sessions_tutor_id ON sessions(tutor_id)"),
            
            ("idx_sessions_date", 
             "CREATE INDEX IF NOT EXISTS idx_sessions_date ON sessions(session_date DESC)"),
            
            ("idx_sessions_student_date", 
             "CREATE INDEX IF NOT EXISTS idx_sessions_student_date ON sessions(student_id, session_date DESC)"),
            
            # Subtopic progress - critical for performance views
            ("idx_subtopic_progress_student", 
             "CREATE INDEX IF NOT EXISTS idx_subtopic_progress_student ON subtopic_progress(student_id)"),
            
            ("idx_subtopic_progress_subtopic", 
             "CREATE INDEX IF NOT EXISTS idx_subtopic_progress_subtopic ON subtopic_progress(subtopic_id)"),
            
            ("idx_subtopic_progress_combined", 
             "CREATE INDEX IF NOT EXISTS idx_subtopic_progress_combined ON subtopic_progress(student_id, subtopic_id)"),
            
            # Questions table - for worksheet generation
            ("idx_questions_subtopic", 
             "CREATE INDEX IF NOT EXISTS idx_questions_subtopic ON questions(subtopic_id, difficulty_level)"),
            
            ("idx_questions_active", 
             "CREATE INDEX IF NOT EXISTS idx_questions_active ON questions(active, subtopic_id)"),
            
            # Worksheets table
            ("idx_worksheets_student", 
             "CREATE INDEX IF NOT EXISTS idx_worksheets_student ON worksheets(student_id, generated_date DESC)"),
            
            ("idx_worksheets_status", 
             "CREATE INDEX IF NOT EXISTS idx_worksheets_status ON worksheets(status)"),
            
            # Subtopics - for topic lookups
            ("idx_subtopics_main_topic", 
             "CREATE INDEX IF NOT EXISTS idx_subtopics_main_topic ON subtopics(main_topic_id, difficulty_order)"),
            
            # Students - for search
            ("idx_students_active", 
             "CREATE INDEX IF NOT EXISTS idx_students_active ON students(active)"),
            
            # Tutors - for login
            ("idx_tutors_username", 
             "CREATE INDEX IF NOT EXISTS idx_tutors_username ON tutors(username)"),
            
            ("idx_tutors_active", 
             "CREATE INDEX IF NOT EXISTS idx_tutors_active ON tutors(active)")
        ]
        
        for index_name, create_sql in indexes_to_add:
            try:
                self.cursor.execute(create_sql)
                print(f"  ✅ Added: {index_name}")
            except sqlite3.Error as e:
                print(f"  ⚠️  Failed to add {index_name}: {e}")
        
        self.conn.commit()
        print(f"\n✨ Index creation complete!")
    
    def analyze_slow_queries(self):
        """Identify potentially slow queries based on table scans."""
        print("\n🔍 Analyzing Query Performance...")
        print("-" * 50)
        
        # Sample queries that are commonly used in the application
        test_queries = [
            ("Student Progress", """
                SELECT sp.*, s.subtopic_name 
                FROM subtopic_progress sp
                JOIN subtopics s ON sp.subtopic_id = s.id
                WHERE sp.student_id = 1
            """),
            
            ("Recent Sessions", """
                SELECT * FROM sessions 
                WHERE student_id = 1 
                ORDER BY session_date DESC 
                LIMIT 10
            """),
            
            ("Topic Mastery", """
                SELECT 
                    mt.topic_name,
                    AVG(sp.current_level) as avg_mastery
                FROM subtopic_progress sp
                JOIN subtopics s ON sp.subtopic_id = s.id
                JOIN main_topics mt ON s.main_topic_id = mt.id
                WHERE sp.student_id = 1
                GROUP BY mt.id
            """),
            
            ("Worksheet Questions", """
                SELECT * FROM questions 
                WHERE subtopic_id = 1 
                AND difficulty_level = 2 
                AND active = 1
            """)
        ]
        
        for query_name, query in test_queries:
            print(f"\n📝 {query_name}:")
            
            # Use EXPLAIN QUERY PLAN to understand how SQLite will execute
            explain_query = f"EXPLAIN QUERY PLAN {query}"
            
            try:
                self.cursor.execute(explain_query)
                plan = self.cursor.fetchall()
                
                uses_index = False
                for row in plan:
                    plan_text = str(row)
                    if "USING INDEX" in plan_text:
                        uses_index = True
                        print(f"  ✅ Uses index efficiently")
                    elif "SCAN TABLE" in plan_text and "USING INDEX" not in plan_text:
                        print(f"  ⚠️  Full table scan detected!")
                
                # Time the actual query
                start_time = time.time()
                self.cursor.execute(query)
                self.cursor.fetchall()
                execution_time = time.time() - start_time
                
                print(f"  ⏱️  Execution time: {execution_time*1000:.2f}ms")
                
            except sqlite3.Error as e:
                print(f"  ❌ Error analyzing query: {e}")
    
    def vacuum_database(self):
        """Vacuum database to reclaim space and optimize structure."""
        print("\n🧹 Vacuuming Database...")
        print("-" * 50)
        
        # Get size before vacuum
        size_before = os.path.getsize(self.db_path)
        
        try:
            self.conn.execute("VACUUM")
            self.conn.commit()
            
            # Get size after vacuum
            size_after = os.path.getsize(self.db_path)
            
            size_reduction = size_before - size_after
            percent_reduction = (size_reduction / size_before) * 100 if size_before > 0 else 0
            
            print(f"  ✅ Vacuum complete!")
            print(f"  📊 Size before: {size_before / 1024:.1f} KB")
            print(f"  📊 Size after: {size_after / 1024:.1f} KB")
            print(f"  💾 Space saved: {size_reduction / 1024:.1f} KB ({percent_reduction:.1f}%)")
            
        except sqlite3.Error as e:
            print(f"  ❌ Vacuum failed: {e}")
    
    def analyze_tables(self):
        """Run ANALYZE to update SQLite's internal statistics."""
        print("\n📈 Analyzing Table Statistics...")
        print("-" * 50)
        
        try:
            self.conn.execute("ANALYZE")
            self.conn.commit()
            print("  ✅ Table statistics updated!")
            
            # Show table sizes
            self.cursor.execute("""
                SELECT 
                    name as table_name,
                    (SELECT COUNT(*) FROM sqlite_master 
                     WHERE type='index' AND tbl_name=m.name) as index_count
                FROM sqlite_master m
                WHERE type='table' 
                AND name NOT LIKE 'sqlite_%'
                ORDER BY name
            """)
            
            print("\n  📊 Table Information:")
            for table_name, index_count in self.cursor.fetchall():
                # Get row count for each table
                self.cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                row_count = self.cursor.fetchone()[0]
                print(f"    • {table_name}: {row_count} rows, {index_count} indexes")
                
        except sqlite3.Error as e:
            print(f"  ❌ Analysis failed: {e}")
    
    def create_performance_views(self):
        """Create optimized views for common queries."""
        print("\n👁️ Creating Performance Views...")
        print("-" * 50)
        
        views = [
            ("student_progress_summary", """
                CREATE VIEW IF NOT EXISTS student_progress_summary AS
                SELECT 
                    s.id as student_id,
                    s.name as student_name,
                    mt.id as topic_id,
                    mt.topic_name,
                    COUNT(sp.id) as subtopics_assessed,
                    AVG(sp.current_level) as avg_mastery,
                    MAX(sp.last_reviewed) as last_reviewed
                FROM students s
                CROSS JOIN main_topics mt
                LEFT JOIN subtopics st ON mt.id = st.main_topic_id
                LEFT JOIN subtopic_progress sp ON sp.student_id = s.id AND sp.subtopic_id = st.id
                WHERE s.active = 1
                GROUP BY s.id, mt.id
            """),
            
            ("recent_session_summary", """
                CREATE VIEW IF NOT EXISTS recent_session_summary AS
                SELECT 
                    s.*,
                    st.name as student_name,
                    t.full_name as tutor_name
                FROM sessions s
                JOIN students st ON s.student_id = st.id
                JOIN tutors t ON s.tutor_id = t.id
                WHERE s.session_date >= date('now', '-30 days')
                ORDER BY s.session_date DESC
            """)
        ]
        
        for view_name, create_sql in views:
            try:
                # Drop existing view if it exists
                self.cursor.execute(f"DROP VIEW IF EXISTS {view_name}")
                
                # Create new view
                self.cursor.execute(create_sql)
                print(f"  ✅ Created view: {view_name}")
                
            except sqlite3.Error as e:
                print(f"  ⚠️  Failed to create view {view_name}: {e}")
        
        self.conn.commit()
    
    def generate_optimization_report(self):
        """Generate a comprehensive optimization report."""
        print("\n📋 Optimization Report")
        print("=" * 50)
        
        report_file = f"optimization_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(report_file, 'w') as f:
            f.write("Tutor AI Database Optimization Report\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 50 + "\n\n")
            
            # Database info
            f.write("Database Information:\n")
            f.write(f"Path: {self.db_path}\n")
            f.write(f"Size: {os.path.getsize(self.db_path) / 1024:.1f} KB\n\n")
            
            # Table statistics
            f.write("Table Statistics:\n")
            self.cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
            """)
            
            for table in self.cursor.fetchall():
                table_name = table[0]
                self.cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = self.cursor.fetchone()[0]
                f.write(f"  {table_name}: {count} rows\n")
            
            f.write("\nOptimization Recommendations:\n")
            f.write("1. Run optimization monthly or after bulk data imports\n")
            f.write("2. Monitor slow queries in production logs\n")
            f.write("3. Consider partitioning large tables if they exceed 100k rows\n")
            f.write("4. Regularly backup before optimization\n")
        
        print(f"  ✅ Report saved to: {report_file}")
    
    def close(self):
        """Close database connection."""
        self.conn.close()


def main():
    """Main function to run optimization tasks."""
    parser = argparse.ArgumentParser(description='Optimize Tutor AI database')
    parser.add_argument('--analyze', action='store_true', help='Analyze current indexes and queries')
    parser.add_argument('--add-indexes', action='store_true', help='Add performance indexes')
    parser.add_argument('--vacuum', action='store_true', help='Vacuum database')
    parser.add_argument('--all', action='store_true', help='Run all optimizations')
    parser.add_argument('--report', action='store_true', help='Generate optimization report')
    
    args = parser.parse_args()
    
    # Default to showing analysis if no args
    if not any(vars(args).values()):
        args.analyze = True
    
    try:
        optimizer = DatabaseOptimizer()
        
        print("🚀 Tutor AI Database Optimizer")
        print("=" * 50)
        
        if args.all:
            args.analyze = args.add_indexes = args.vacuum = args.report = True
        
        if args.analyze:
            optimizer.analyze_current_indexes()
            optimizer.analyze_slow_queries()
            optimizer.analyze_tables()
        
        if args.add_indexes:
            optimizer.add_performance_indexes()
            optimizer.create_performance_views()
        
        if args.vacuum:
            optimizer.vacuum_database()
        
        if args.report:
            optimizer.generate_optimization_report()
        
        optimizer.close()
        
        print("\n✨ Optimization complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())