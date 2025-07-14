from utils.database import get_db_connection

class TopicService:
    @staticmethod
    def get_all_main_topics():
        """Get all main topics."""
        with get_db_connection() as conn:
            return conn.execute('''
                SELECT id, topic_name, description, target_year_groups, color_code
                FROM main_topics
                ORDER BY topic_name
            ''').fetchall()
    
    @staticmethod
    def get_main_topic(topic_id):
        """Get a main topic by ID."""
        with get_db_connection() as conn:
            return conn.execute(
                'SELECT * FROM main_topics WHERE id = ?', 
                (topic_id,)
            ).fetchone()
    
    @staticmethod
    def create_main_topic(topic_name, description=None, target_year_groups=None, color_code=None):
        """Create a new main topic."""
        with get_db_connection() as conn:
            conn.execute('''
                INSERT INTO main_topics (topic_name, description, target_year_groups, color_code)
                VALUES (?, ?, ?, ?)
            ''', (topic_name, description, target_year_groups, color_code))
            conn.commit()
    
    @staticmethod
    def get_subtopics_by_main_topic(main_topic_id):
        """Get all subtopics for a main topic."""
        with get_db_connection() as conn:
            return conn.execute('''
                SELECT id, subtopic_name, description, difficulty_order
                FROM subtopics
                WHERE main_topic_id = ?
                ORDER BY difficulty_order
            ''', (main_topic_id,)).fetchall()
    
    @staticmethod
    def get_subtopic(subtopic_id):
        """Get a specific subtopic by ID."""
        with get_db_connection() as conn:
            result = conn.execute('''
                SELECT s.*, mt.topic_name, mt.color_code 
                FROM subtopics s
                JOIN main_topics mt ON s.main_topic_id = mt.id
                WHERE s.id = ?
            ''', (subtopic_id,)).fetchone()
            
            return dict(result) if result else None
    
    @staticmethod
    def create_subtopic(main_topic_id, subtopic_name, description=None, difficulty_order=1):
        """Create a new subtopic."""
        with get_db_connection() as conn:
            conn.execute('''
                INSERT INTO subtopics (main_topic_id, subtopic_name, description, difficulty_order)
                VALUES (?, ?, ?, ?)
            ''', (main_topic_id, subtopic_name, description, difficulty_order))
            conn.commit()
    
    @staticmethod
    def update_main_topic(topic_id, topic_name, description=None, target_year_groups=None, color_code=None):
        """Update a main topic."""
        with get_db_connection() as conn:
            conn.execute('''
                UPDATE main_topics 
                SET topic_name = ?, description = ?, target_year_groups = ?, color_code = ?
                WHERE id = ?
            ''', (topic_name, description, target_year_groups, color_code, topic_id))
            conn.commit()
    
    @staticmethod
    def delete_main_topic(topic_id):
        """Delete a main topic and all its subtopics."""
        with get_db_connection() as conn:
            # First delete all subtopics
            conn.execute("DELETE FROM subtopics WHERE main_topic_id = ?", (topic_id,))
            # Then delete the main topic
            conn.execute("DELETE FROM main_topics WHERE id = ?", (topic_id,))
            conn.commit()
    
    @staticmethod
    def update_subtopic(subtopic_id, subtopic_name, description=None, difficulty_order=1):
        """Update a subtopic."""
        with get_db_connection() as conn:
            conn.execute('''
                UPDATE subtopics 
                SET subtopic_name = ?, description = ?, difficulty_order = ?
                WHERE id = ?
            ''', (subtopic_name, description, difficulty_order, subtopic_id))
            conn.commit()
    
    @staticmethod
    def delete_subtopic(subtopic_id):
        """Delete a subtopic."""
        with get_db_connection() as conn:
            # First delete any progress records for this subtopic
            conn.execute("DELETE FROM subtopic_progress WHERE subtopic_id = ?", (subtopic_id,))
            # Then delete the subtopic
            conn.execute("DELETE FROM subtopics WHERE id = ?", (subtopic_id,))
            conn.commit()