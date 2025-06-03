from utils.database import get_db_connection
from datetime import datetime

class SessionService:
    @staticmethod
    def create_session(student_id, tutor_id, duration, progress_score, notes=None):
        """Create a new session."""
        with get_db_connection() as conn:
            conn.execute('''
                INSERT INTO sessions (student_id, tutor_id, date, duration, progress_score, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (student_id, tutor_id, datetime.now(), duration, progress_score, notes))
            conn.commit()
    
    @staticmethod
    def get_all_sessions():
        """Get all sessions with student and tutor names."""
        with get_db_connection() as conn:
            return conn.execute('''
                SELECT s.*, st.name as student_name, t.name as tutor_name
                FROM sessions s
                JOIN students st ON s.student_id = st.id
                JOIN tutors t ON s.tutor_id = t.id
                ORDER BY s.date DESC
            ''').fetchall()
    
    @staticmethod
    def get_sessions_by_student(student_id):
        """Get all sessions for a specific student."""
        with get_db_connection() as conn:
            return conn.execute('''
                SELECT s.*, t.name as tutor_name
                FROM sessions s
                JOIN tutors t ON s.tutor_id = t.id
                WHERE s.student_id = ?
                ORDER BY s.date DESC
            ''', (student_id,)).fetchall()
    
    @staticmethod
    def get_session_stats():
        """Get session statistics."""
        with get_db_connection() as conn:
            total_sessions = conn.execute('SELECT COUNT(*) FROM sessions').fetchone()[0]
            
            if total_sessions > 0:
                avg_score = conn.execute('SELECT AVG(progress_score) FROM sessions').fetchone()[0]
                avg_duration = conn.execute('SELECT AVG(duration) FROM sessions').fetchone()[0]
            else:
                avg_score = 0
                avg_duration = 0
            
            return {
                'total_sessions': total_sessions,
                'avg_score': round(avg_score, 1) if avg_score else 0,
                'avg_duration': round(avg_duration, 1) if avg_duration else 0
            }