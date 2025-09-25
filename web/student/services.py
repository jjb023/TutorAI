# web/student/services.py
from utils.db_connection import get_db

class StudentService:
    @staticmethod
    def get_all_students():
        """Get all students with basic info."""
        with get_db() as db:
            result = db.execute('''
                SELECT * FROM students 
                ORDER BY name
            ''')
            results = result.fetchall()
            
            # Convert to list of dictionaries
            if results and isinstance(results[0], dict):
                return results
            else:
                return [dict(row) for row in results]
    
    @staticmethod
    def get_student(student_id):
        """Get a student by ID."""
        with get_db() as db:
            result_query = db.execute('SELECT * FROM students WHERE id = ?', (student_id,))
            result = result_query.fetchone()
            
            if result:
                return dict(result) if isinstance(result, dict) else dict(result)
            return None
    
    @staticmethod
    def create_student(name, age, year_group, target_school=None, parent_contact=None, notes=None):
        """Create a new student."""
        with get_db() as db:
            db.execute('''
                INSERT INTO students (name, age, year_group, target_school, parent_contact, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (name, age, year_group, target_school, parent_contact, notes))
            
            # Get the inserted ID
            result = db.execute("SELECT id FROM students WHERE name = ? AND age = ? ORDER BY id DESC LIMIT 1", 
                              (name, age)).fetchone()
            if isinstance(result, dict):
                return result['id']
            else:
                return result[0] if result else None
    
    @staticmethod
    def update_student(student_id, name, age, year_group, target_school=None, parent_contact=None, notes=None):
        """Update a student."""
        with get_db() as db:
            db.execute('''
                UPDATE students 
                SET name = ?, age = ?, year_group = ?, target_school = ?, parent_contact = ?, notes = ?
                WHERE id = ?
            ''', (name, age, year_group, target_school, parent_contact, notes, student_id))
    
    @staticmethod
    def delete_student(student_id):
        """Delete a student and all related progress."""
        with get_db() as db:
            # Delete in order due to foreign key constraints
            db.execute('DELETE FROM subtopic_progress WHERE student_id = ?', (student_id,))
            db.execute('DELETE FROM sessions WHERE student_id = ?', (student_id,))
            db.execute('DELETE FROM students WHERE id = ?', (student_id,))
    
    @staticmethod
    def get_student_progress_summary(student_id):
        """Get summary of student progress across all topics."""
        with get_db() as db:
            # Get topic-level summary
            result = db.execute('''
                SELECT 
                    mt.topic_name,
                    mt.color_code,
                    COUNT(s.id) as total_subtopics,
                    COUNT(sp.id) as assessed_subtopics,
                    ROUND(AVG(CASE WHEN sp.mastery_level IS NOT NULL THEN sp.mastery_level ELSE 0 END), 1) as avg_mastery,
                    ROUND(CASE 
                        WHEN COUNT(s.id) > 0 THEN (COUNT(sp.id) * 100.0 / COUNT(s.id))
                        ELSE 0.0 
                    END, 1) as completion_percentage
                FROM main_topics mt
                LEFT JOIN subtopics s ON mt.id = s.main_topic_id
                LEFT JOIN subtopic_progress sp ON s.id = sp.subtopic_id AND sp.student_id = ?
                GROUP BY mt.id, mt.topic_name
                ORDER BY mt.topic_name
            ''', (student_id,))
            topic_summaries = result.fetchall()
            
            # Convert to consistent format
            if topic_summaries and isinstance(topic_summaries[0], dict):
                return {'topic_summaries': topic_summaries}
            else:
                return {'topic_summaries': [dict(row) for row in topic_summaries]}
    
    @staticmethod
    def get_subtopic_progress(student_id, subtopic_id):
        """Get progress for a specific subtopic."""
        with get_db() as db:
            result = db.execute('''
                SELECT * FROM subtopic_progress
                WHERE student_id = ? AND subtopic_id = ?
            ''', (student_id, subtopic_id)).fetchone()
            
            # Return as a dictionary for consistent access
            if result:
                return dict(result) if isinstance(result, dict) else dict(result)
            return None
    
    @staticmethod
    def get_session_count(student_id):
        """Get total number of sessions for a student."""
        with get_db() as db:
            result = db.execute('''
                SELECT COUNT(*) FROM sessions WHERE student_id = ?
            ''', (student_id,)).fetchone()
            
            if isinstance(result, dict):
                return list(result.values())[0] if result else 0
            else:
                return result[0] if result else 0
    
    @staticmethod
    def get_recent_activity(student_id, days=30):
        """Get recent activity for a student."""
        with get_db() as db:
            result = db.execute('''
                SELECT 
                    sp.last_assessed as date,
                    s.subtopic_name,
                    mt.topic_name,
                    sp.mastery_level
                FROM subtopic_progress sp
                JOIN subtopics s ON sp.subtopic_id = s.id
                JOIN main_topics mt ON s.main_topic_id = mt.id
                WHERE sp.student_id = ? 
                    AND sp.last_assessed >= (CURRENT_DATE - ? * INTERVAL '1 day')
                ORDER BY sp.last_assessed DESC
            ''', (student_id, days))
            activities = result.fetchall()
            
            # Convert to consistent format
            if activities and isinstance(activities[0], dict):
                return activities
            else:
                return [dict(row) for row in activities]
    
    @staticmethod
    def get_mastery_distribution(student_id):
        """Get distribution of mastery levels for visualization."""
        with get_db() as db:
            result = db.execute('''
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
                GROUP BY CASE 
                    WHEN mastery_level >= 8 THEN 'Excellent (8-10)'
                    WHEN mastery_level >= 5 THEN 'Good (5-7)'
                    WHEN mastery_level >= 3 THEN 'Developing (3-4)'
                    ELSE 'Beginning (1-2)'
                END
                ORDER BY MIN(mastery_level) DESC
            ''', (student_id,))
            distributions = result.fetchall()
            
            # Convert to consistent format
            if distributions and isinstance(distributions[0], dict):
                return distributions
            else:
                return [dict(row) for row in distributions]