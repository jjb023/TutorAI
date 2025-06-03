from utils.database import get_db_connection
from datetime import datetime

class SessionService:
    @staticmethod
    def create_session(student_id, tutor_id, duration_minutes=None, topics_covered=None, notes=None):
        """Create a new session using your existing database structure."""
        with get_db_connection() as conn:
            # First, let's see what columns exist in the sessions table
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(sessions)")
            columns = [column[1] for column in cursor.fetchall()]
            print(f"Sessions table columns: {columns}")
            
            # Use your existing database structure
            conn.execute('''
                INSERT INTO sessions (student_id, tutor_id, session_date, duration_minutes, main_topics_covered, tutor_notes)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (student_id, tutor_id, datetime.now().isoformat(), duration_minutes, topics_covered, notes))
            conn.commit()
            
            # Update student's last session date
            conn.execute(
                "UPDATE students SET last_session_date = CURRENT_TIMESTAMP WHERE id = ?",
                (student_id,)
            )
            conn.commit()
            print(f"✅ Session created: Student {student_id}, Tutor {tutor_id}")
    
    @staticmethod
    def get_all_sessions():
        """Get all sessions with student and tutor names."""
        with get_db_connection() as conn:
            return conn.execute('''
                SELECT s.*, st.name as student_name, t.full_name as tutor_name
                FROM sessions s
                JOIN students st ON s.student_id = st.id
                JOIN tutors t ON s.tutor_id = t.id
                ORDER BY s.session_date DESC
            ''').fetchall()
    
    @staticmethod
    def get_sessions_by_student(student_id):
        """Get all sessions for a specific student."""
        with get_db_connection() as conn:
            return conn.execute('''
                SELECT s.*, t.full_name as tutor_name
                FROM sessions s
                JOIN tutors t ON s.tutor_id = t.id
                WHERE s.student_id = ?
                ORDER BY s.session_date DESC
            ''', (student_id,)).fetchall()
    
    @staticmethod
    def get_session_stats():
        """Get session statistics."""
        with get_db_connection() as conn:
            total_sessions = conn.execute('SELECT COUNT(*) FROM sessions').fetchone()[0]
            
            if total_sessions > 0:
                avg_duration = conn.execute('SELECT AVG(duration_minutes) FROM sessions WHERE duration_minutes IS NOT NULL').fetchone()[0]
            else:
                avg_duration = 0
            
            return {
                'total_sessions': total_sessions,
                'avg_duration': round(avg_duration, 1) if avg_duration else 0
            }