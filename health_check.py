#!/usr/bin/env python3
"""
Health check script for Tutor AI
Identifies common issues and data inconsistencies
"""

import sqlite3
import os
from datetime import datetime, timedelta

class HealthCheck:
    def __init__(self):
        self.db_path = os.path.join('data', 'tutor_ai.db')
        self.issues = []
        self.warnings = []
        self.info = []
    
    def run(self):
        """Run all health checks"""
        print("🏥 Tutor AI System Health Check")
        print("=" * 50)
        print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📁 Database: {self.db_path}")
        print("=" * 50)
        
        if not os.path.exists(self.db_path):
            print("❌ CRITICAL: Database file not found!")
            return
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Run checks
        self.check_database_integrity(cursor)
        self.check_orphaned_records(cursor)
        self.check_data_consistency(cursor)
        self.check_performance_indicators(cursor)
        self.check_usage_patterns(cursor)
        
        conn.close()
        
        # Print results
        self.print_results()
    
    def check_database_integrity(self, cursor):
        """Check basic database integrity"""
        print("\n🔍 Checking Database Integrity...")
        
        # Check tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row['name'] for row in cursor.fetchall()]
        
        required_tables = ['students', 'tutors', 'main_topics', 'subtopics', 
                          'sessions', 'subtopic_progress']
        
        for table in required_tables:
            if table not in tables:
                self.issues.append(f"Missing required table: {table}")
        
        # Check for indexes
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
        indexes = [row['name'] for row in cursor.fetchall()]
        
        if len(indexes) < 3:
            self.warnings.append("Few indexes found - may impact performance")
        
        self.info.append(f"Found {len(tables)} tables and {len(indexes)} indexes")
    
    def check_orphaned_records(self, cursor):
        """Check for orphaned records"""
        print("\n🔍 Checking for Orphaned Records...")
        
        # Orphaned progress records
        cursor.execute("""
            SELECT COUNT(*) FROM subtopic_progress sp
            WHERE NOT EXISTS (SELECT 1 FROM students s WHERE s.id = sp.student_id)
        """)
        orphaned_progress = cursor.fetchone()[0]
        if orphaned_progress > 0:
            self.issues.append(f"Found {orphaned_progress} orphaned progress records")
        
        # Orphaned sessions
        cursor.execute("""
            SELECT COUNT(*) FROM sessions s
            WHERE NOT EXISTS (SELECT 1 FROM students st WHERE st.id = s.student_id)
               OR NOT EXISTS (SELECT 1 FROM tutors t WHERE t.id = s.tutor_id)
        """)
        orphaned_sessions = cursor.fetchone()[0]
        if orphaned_sessions > 0:
            self.issues.append(f"Found {orphaned_sessions} orphaned session records")
        
        # Subtopics without main topics
        cursor.execute("""
            SELECT COUNT(*) FROM subtopics s
            WHERE NOT EXISTS (SELECT 1 FROM main_topics mt WHERE mt.id = s.main_topic_id)
        """)
        orphaned_subtopics = cursor.fetchone()[0]
        if orphaned_subtopics > 0:
            self.issues.append(f"Found {orphaned_subtopics} subtopics without main topics")
    
    def check_data_consistency(self, cursor):
        """Check data consistency"""
        print("\n🔍 Checking Data Consistency...")
        
        # Check mastery levels are in range
        cursor.execute("""
            SELECT COUNT(*) FROM subtopic_progress
            WHERE mastery_level < 1 OR mastery_level > 10
        """)
        invalid_mastery = cursor.fetchone()[0]
        if invalid_mastery > 0:
            self.issues.append(f"Found {invalid_mastery} invalid mastery levels (outside 1-10)")
        
        # Check for duplicate progress records
        cursor.execute("""
            SELECT student_id, subtopic_id, COUNT(*) as count
            FROM subtopic_progress
            GROUP BY student_id, subtopic_id
            HAVING count > 1
        """)
        duplicates = cursor.fetchall()
        if duplicates:
            self.issues.append(f"Found {len(duplicates)} duplicate progress records")
        
        # Check session durations
        cursor.execute("""
            SELECT COUNT(*) FROM sessions
            WHERE duration_minutes < 15 OR duration_minutes > 180
        """)
        invalid_durations = cursor.fetchone()[0]
        if invalid_durations > 0:
            self.warnings.append(f"Found {invalid_durations} sessions with unusual durations")
        
        # Check student ages
        cursor.execute("""
            SELECT COUNT(*) FROM students
            WHERE age < 4 OR age > 18
        """)
        invalid_ages = cursor.fetchone()[0]
        if invalid_ages > 0:
            self.warnings.append(f"Found {invalid_ages} students with ages outside typical range")
    
    def check_performance_indicators(self, cursor):
        """Check performance indicators"""
        print("\n🔍 Checking Performance Indicators...")
        
        # Large tables
        for table in ['students', 'sessions', 'subtopic_progress']:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            if count > 10000:
                self.warnings.append(f"Table '{table}' has {count} records - consider archiving")
            self.info.append(f"Table '{table}': {count} records")
        
        # Unassessed subtopics
        cursor.execute("""
            SELECT COUNT(DISTINCT s.id) FROM subtopics s
            WHERE NOT EXISTS (
                SELECT 1 FROM subtopic_progress sp WHERE sp.subtopic_id = s.id
            )
        """)
        unassessed = cursor.fetchone()[0]
        if unassessed > 0:
            self.info.append(f"{unassessed} subtopics have never been assessed")
    
    def check_usage_patterns(self, cursor):
        """Check usage patterns"""
        print("\n🔍 Checking Usage Patterns...")
        
        # Inactive students
        thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
        cursor.execute("""
            SELECT COUNT(*) FROM students
            WHERE last_session_date IS NULL 
               OR last_session_date < ?
        """, (thirty_days_ago,))
        inactive = cursor.fetchone()[0]
        if inactive > 0:
            self.info.append(f"{inactive} students haven't had sessions in 30+ days")
        
        # Tutors who haven't logged in
        cursor.execute("""
            SELECT COUNT(*) FROM tutors
            WHERE last_login IS NULL AND username != 'admin'
        """)
        never_logged = cursor.fetchone()[0]
        if never_logged > 0:
            self.warnings.append(f"{never_logged} tutors have never logged in")
        
        # Average sessions per student
        cursor.execute("""
            SELECT AVG(session_count) FROM (
                SELECT COUNT(*) as session_count 
                FROM sessions 
                GROUP BY student_id
            )
        """)
        avg_sessions = cursor.fetchone()[0]
        if avg_sessions:
            self.info.append(f"Average sessions per student: {avg_sessions:.1f}")
        
        # Topics with no subtopics
        cursor.execute("""
            SELECT mt.topic_name FROM main_topics mt
            WHERE NOT EXISTS (
                SELECT 1 FROM subtopics s WHERE s.main_topic_id = mt.id
            )
        """)
        empty_topics = cursor.fetchall()
        if empty_topics:
            topic_names = [row['topic_name'] for row in empty_topics]
            self.warnings.append(f"Topics with no subtopics: {', '.join(topic_names)}")
    
    def print_results(self):
        """Print health check results"""
        print("\n" + "=" * 50)
        print("📊 HEALTH CHECK RESULTS")
        print("=" * 50)
        
        if self.issues:
            print(f"\n❌ ISSUES ({len(self.issues)}):")
            for issue in self.issues:
                print(f"   • {issue}")
        else:
            print("\n✅ No critical issues found!")
        
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"   • {warning}")
        
        if self.info:
            print(f"\nℹ️  INFORMATION ({len(self.info)}):")
            for info in self.info:
                print(f"   • {info}")
        
        print("\n" + "=" * 50)
        print("💡 RECOMMENDATIONS:")
        print("=" * 50)
        
        # Generate recommendations based on findings
        if self.issues:
            print("1. ❗ Fix critical issues immediately:")
            if any("orphaned" in issue for issue in self.issues):
                print("   - Run database cleanup to remove orphaned records")
            if any("Missing required table" in issue for issue in self.issues):
                print("   - Run migration script to create missing tables")
        
        if any("Few indexes" in warning for warning in self.warnings):
            print("2. 🚀 Add database indexes for better performance")
        
        if any("never logged in" in warning for warning in self.warnings):
            print("3. 👥 Reach out to tutors who haven't logged in")
        
        if any("30+ days" in info for info in self.info):
            print("4. 📞 Follow up with inactive students")
        
        print("\n✅ Health check complete!")

def quick_fix_issues():
    """Attempt to fix common issues automatically"""
    print("\n🔧 Attempting Quick Fixes...")
    
    db_path = os.path.join('data', 'tutor_ai.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Fix 1: Remove orphaned progress records
        cursor.execute("""
            DELETE FROM subtopic_progress 
            WHERE student_id NOT IN (SELECT id FROM students)
        """)
        orphaned_deleted = cursor.rowcount
        if orphaned_deleted > 0:
            print(f"✅ Removed {orphaned_deleted} orphaned progress records")
        
        # Fix 2: Remove orphaned sessions
        cursor.execute("""
            DELETE FROM sessions 
            WHERE student_id NOT IN (SELECT id FROM students)
               OR tutor_id NOT IN (SELECT id FROM tutors)
        """)
        sessions_deleted = cursor.rowcount
        if sessions_deleted > 0:
            print(f"✅ Removed {sessions_deleted} orphaned sessions")
        
        # Fix 3: Ensure admin account exists
        cursor.execute("SELECT id FROM tutors WHERE username = 'admin'")
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO tutors (username, password_hash, full_name, email, active)
                VALUES ('admin', 'temp_hash', 'Administrator', 'admin@tutorai.local', 1)
            """)
            print("✅ Created missing admin account")
        
        # Fix 4: Add missing indexes
        indexes_to_create = [
            ("idx_subtopic_progress_student", "subtopic_progress(student_id)"),
            ("idx_sessions_student", "sessions(student_id)"),
            ("idx_subtopics_main_topic", "subtopics(main_topic_id)")
        ]
        
        for index_name, index_def in indexes_to_create:
            try:
                cursor.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON {index_def}")
                print(f"✅ Created index: {index_name}")
            except sqlite3.Error:
                pass  # Index might already exist
        
        conn.commit()
        print("✅ Quick fixes applied successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error applying fixes: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    # Run health check
    checker = HealthCheck()
    checker.run()
    
    # Ask if user wants to apply fixes
    if checker.issues:
        print("\n" + "=" * 50)
        response = input("Would you like to attempt automatic fixes? (yes/no): ").strip().lower()
        if response == 'yes':
            quick_fix_issues()
            print("\n🔄 Running health check again...")
            checker = HealthCheck()
            checker.run()