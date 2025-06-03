from utils.database import get_db_connection

class StudentService:
    @staticmethod
    def get_all_students():
        """Get all students."""
        with get_db_connection() as conn:
            return conn.execute('SELECT * FROM students ORDER BY name').fetchall()
    
    @staticmethod
    def get_student(student_id):
        """Get a student by ID."""
        with get_db_connection() as conn:
            return conn.execute('SELECT * FROM students WHERE id = ?', (student_id,)).fetchone()
    
    @staticmethod
    def create_student(name, age, contact_info):
        """Create a new student."""
        with get_db_connection() as conn:
            conn.execute(
                'INSERT INTO students (name, age, contact_info) VALUES (?, ?, ?)',
                (name, age, contact_info)
            )
            conn.commit()
    
    @staticmethod
    def update_student(student_id, name, age, contact_info):
        """Update a student."""
        with get_db_connection() as conn:
            conn.execute(
                'UPDATE students SET name = ?, age = ?, contact_info = ? WHERE id = ?',
                (name, age, contact_info, student_id)
            )
            conn.commit()
    
    @staticmethod
    def delete_student(student_id):
        """Delete a student."""
        with get_db_connection() as conn:
            conn.execute('DELETE FROM students WHERE id = ?', (student_id,))
            conn.commit()
    
    @staticmethod
    def get_student_sessions(student_id):
        """Get all sessions for a student."""
        with get_db_connection() as conn:
            return conn.execute('''
                SELECT s.*, t.name as tutor_name 
                FROM sessions s
                JOIN tutors t ON s.tutor_id = t.id
                WHERE s.student_id = ?
                ORDER BY s.date DESC
            ''', (student_id,)).fetchall()