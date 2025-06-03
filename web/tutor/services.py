from utils.database import get_db_connection

class TutorService:
    @staticmethod
    def get_all_tutors():
        """Get all tutors."""
        with get_db_connection() as conn:
            return conn.execute('SELECT * FROM tutors ORDER BY name').fetchall()
    
    @staticmethod
    def get_tutor(tutor_id):
        """Get a tutor by ID."""
        with get_db_connection() as conn:
            return conn.execute('SELECT * FROM tutors WHERE id = ?', (tutor_id,)).fetchone()
    
    @staticmethod
    def create_tutor(name, subject, experience=None, hourly_rate=None):
        """Create a new tutor."""
        with get_db_connection() as conn:
            conn.execute(
                'INSERT INTO tutors (name, subject, experience, hourly_rate) VALUES (?, ?, ?, ?)',
                (name, subject, experience, hourly_rate)
            )
            conn.commit()
    
    @staticmethod
    def update_tutor(tutor_id, name, subject, experience=None, hourly_rate=None):
        """Update a tutor."""
        with get_db_connection() as conn:
            conn.execute(
                'UPDATE tutors SET name = ?, subject = ?, experience = ?, hourly_rate = ? WHERE id = ?',
                (name, subject, experience, hourly_rate, tutor_id)
            )
            conn.commit()
    
    @staticmethod
    def delete_tutor(tutor_id):
        """Delete a tutor."""
        with get_db_connection() as conn:
            conn.execute('DELETE FROM tutors WHERE id = ?', (tutor_id,))
            conn.commit()
    
    @staticmethod
    def get_tutor_sessions(tutor_id):
        """Get all sessions for a tutor."""
        with get_db_connection() as conn:
            return conn.execute('''
                SELECT s.*, st.name as student_name 
                FROM sessions s
                JOIN students st ON s.student_id = st.id
                WHERE s.tutor_id = ?
                ORDER BY s.date DESC
            ''', (tutor_id,)).fetchall()