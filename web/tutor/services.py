from utils.database import get_db_connection

class TutorService:
    @staticmethod
    def get_all_tutors():
        """Get all tutors using your existing database structure."""
        with get_db_connection() as conn:
            # First, let's see what columns exist in the tutors table
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(tutors)")
            columns = [column[1] for column in cursor.fetchall()]
            print(f"Tutors table columns: {columns}")
            
            # Use the correct column names from your existing database
            return conn.execute('SELECT * FROM tutors WHERE active = 1 ORDER BY full_name').fetchall()
    
    @staticmethod
    def get_tutor(tutor_id):
        """Get a tutor by ID."""
        with get_db_connection() as conn:
            return conn.execute('SELECT * FROM tutors WHERE id = ?', (tutor_id,)).fetchone()
    
    @staticmethod
    def create_tutor(username, full_name, email=None):
        """Create a new tutor using your existing database structure."""
        with get_db_connection() as conn:
            conn.execute(
                'INSERT INTO tutors (username, password_hash, full_name, email, active) VALUES (?, ?, ?, ?, ?)',
                (username, 'password_hash', full_name, email, 1)
            )
            conn.commit()
    
    @staticmethod
    def update_tutor(tutor_id, username, full_name, email=None):
        """Update a tutor."""
        with get_db_connection() as conn:
            conn.execute(
                'UPDATE tutors SET username = ?, full_name = ?, email = ? WHERE id = ?',
                (username, full_name, email, tutor_id)
            )
            conn.commit()
    
    @staticmethod
    def delete_tutor(tutor_id):
        """Delete a tutor (set inactive)."""
        with get_db_connection() as conn:
            conn.execute('UPDATE tutors SET active = 0 WHERE id = ?', (tutor_id,))
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
                ORDER BY s.session_date DESC
            ''', (tutor_id,)).fetchall()