# web/student/services.py
from utils.database import get_db_connection

class StudentService:
    @staticmethod
    def get_all_students():
        """Get all students with basic info."""
        with get_db_connection() as conn:
            results = conn.execute('''
                SELECT * FROM students 
                ORDER BY name
            ''').fetchall()
            # Convert Row objects to dictionaries
            return [dict(row) for row in results]
    
    @staticmethod
    def get_student(student_id):
        """Get a student by ID."""
        with get_db_connection() as conn:
            result = conn.execute('SELECT * FROM students WHERE id = ?', (student_id,)).fetchone()
            # Convert Row to dict for consistent access
            return dict(result) if result else None
    
    @staticmethod
    def create_student(name, age, year_group, target_school=None, parent_contact=None, notes=None):
        """Create a new student."""
        with get_db_connection() as conn:
            cursor = conn.execute('''
                INSERT INTO students (name, age, year_group, target_school, parent_contact, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (name, age, year_group, target_school, parent_contact, notes))
            conn.commit()
            return cursor.lastrowid
    
    @staticmethod
    def update_student(student_id, name, age, year_group, target_school=None, parent_contact=None, notes=None):
        """Update a student."""
        with get_db_connection() as conn:
            conn.execute('''
                UPDATE students 
                SET name = ?, age = ?, year_group = ?, target_school = ?, parent_contact = ?, notes = ?
                WHERE id = ?
            ''', (name, age, year_group, target_school, parent_contact, notes, student_id))
            conn.commit()
    
    @staticmethod
    def delete_student(student_id):
        """Delete a student and all related progress."""
        with get_db_connection() as conn:
            # Delete in order due to foreign key constraints
            conn.execute('DELETE FROM subtopic_progress WHERE student_id = ?', (student_id,))
            conn.execute('DELETE FROM sessions WHERE student_id = ?', (student_id,))
            conn.execute('DELETE FROM students WHERE id = ?', (student_id,))
            conn.commit()
    
    @staticmethod
    def get_student_progress_summary(student_id):
        """Get summary of student progress across all topics."""
        with get_db_connection() as conn:
            # Get topic-level summary
            topic_summaries = conn.execute('''
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
            
            return {'topic_summaries': topic_summaries}
    
    @staticmethod
    def get_subtopic_progress(student_id, subtopic_id):
        """Get progress for a specific subtopic."""
        with get_db_connection() as conn:
            result = conn.execute('''
                SELECT * FROM subtopic_progress
                WHERE student_id = ? AND subtopic_id = ?
            ''', (student_id, subtopic_id)).fetchone()
            
            # Return as a dictionary for consistent access
            if result:
                return dict(result)
            return None
    
    @staticmethod
    def get_session_count(student_id):
        """Get total number of sessions for a student."""
        with get_db_connection() as conn:
            result = conn.execute('''
                SELECT COUNT(*) FROM sessions WHERE student_id = ?
            ''', (student_id,)).fetchone()
            return result[0] if result else 0
    
    @staticmethod
    def get_recent_activity(student_id, days=30):
        """Get recent activity for a student."""
        with get_db_connection() as conn:
            return conn.execute('''
                SELECT 
                    sp.last_assessed as date,
                    s.subtopic_name,
                    mt.topic_name,
                    sp.mastery_level
                FROM subtopic_progress sp
                JOIN subtopics s ON sp.subtopic_id = s.id
                JOIN main_topics mt ON s.main_topic_id = mt.id
                WHERE sp.student_id = ? 
                    AND date(sp.last_assessed) >= date('now', '-' || ? || ' days')
                ORDER BY sp.last_assessed DESC
            ''', (student_id, days)).fetchall()
    
    @staticmethod
    def get_mastery_distribution(student_id):
        """Get distribution of mastery levels for visualization."""
        with get_db_connection() as conn:
            return conn.execute('''
                SELECT 
                    CASE 
                        WHEN mastery_level >= 8 THEN 'Excellent (8-10)'
                        WHEN mastery_level >= 5 THEN 'Good (5-7)'
                        WHEN mastery_level >= 3 THEN 'Developing (3-4)'
                        ELSE 'Beginning (1-2)'
                    END as level_group,
                    COUNT(*) as count
                FROM subtopic_progress
                WHERE student_id = ? AND mastery_level > 0
                GROUP BY level_group
                ORDER BY mastery_level DESC
            ''', (student_id,)).fetchall()