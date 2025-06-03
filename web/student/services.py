from utils.database import get_db_connection

class StudentService:
    @staticmethod
    def get_all_students():
        """Get all students using your existing database structure."""
        with get_db_connection() as conn:
            return conn.execute('SELECT * FROM students ORDER BY name').fetchall()
    
    @staticmethod
    def get_student(student_id):
        """Get a student by ID."""
        with get_db_connection() as conn:
            return conn.execute('SELECT * FROM students WHERE id = ?', (student_id,)).fetchone()
    
    @staticmethod
    def create_student(name, age, year_group, target_school=None, parent_contact=None, notes=None):
        """Create a new student using your existing database structure."""
        with get_db_connection() as conn:
            conn.execute(
                'INSERT INTO students (name, age, year_group, target_school, parent_contact, notes) VALUES (?, ?, ?, ?, ?, ?)',
                (name, age, year_group, target_school, parent_contact, notes)
            )
            conn.commit()
    
    @staticmethod
    def update_student(student_id, name, age, year_group, target_school=None, parent_contact=None, notes=None):
        """Update a student."""
        with get_db_connection() as conn:
            conn.execute(
                'UPDATE students SET name = ?, age = ?, year_group = ?, target_school = ?, parent_contact = ?, notes = ? WHERE id = ?',
                (name, age, year_group, target_school, parent_contact, notes, student_id)
            )
            conn.commit()
    
    @staticmethod
    def delete_student(student_id):
        """Delete a student and all related progress."""
        with get_db_connection() as conn:
            # Delete progress first (foreign key constraint)
            conn.execute('DELETE FROM subtopic_progress WHERE student_id = ?', (student_id,))
            # Delete sessions
            conn.execute('DELETE FROM sessions WHERE student_id = ?', (student_id,))
            # Delete student
            conn.execute('DELETE FROM students WHERE id = ?', (student_id,))
            conn.commit()
    
    @staticmethod
    def get_student_sessions(student_id):
        """Get all sessions for a student."""
        with get_db_connection() as conn:
            return conn.execute('''
                SELECT s.*, 'Tutor' as tutor_name 
                FROM sessions s
                WHERE s.student_id = ?
                ORDER BY s.session_date DESC
            ''', (student_id,)).fetchall()
    
    @staticmethod
    def get_student_progress_summary(student_id):
        """Get progress summary for a student using your existing structure."""
        with get_db_connection() as conn:
            # Get main topic summary using your existing database structure
            summary = conn.execute('''
                SELECT 
                    mt.topic_name,
                    mt.color_code,
                    COUNT(s.id) as total_subtopics,
                    COUNT(sp.id) as assessed_subtopics,
                    ROUND(AVG(CASE WHEN sp.mastery_level IS NOT NULL THEN sp.mastery_level ELSE 0 END), 1) as avg_mastery,
                    ROUND((COUNT(sp.id) * 100.0 / COUNT(s.id)), 1) as completion_percentage
                FROM main_topics mt
                LEFT JOIN subtopics s ON mt.id = s.main_topic_id
                LEFT JOIN subtopic_progress sp ON s.id = sp.subtopic_id AND sp.student_id = ?
                GROUP BY mt.id, mt.topic_name
                ORDER BY mt.topic_name
            ''', (student_id,)).fetchall()
            
            return summary