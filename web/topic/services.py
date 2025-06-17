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
    def create_subtopic(main_topic_id, subtopic_name, description=None, difficulty_order=1):
        """Create a new subtopic."""
        with get_db_connection() as conn:
            conn.execute('''
                INSERT INTO subtopics (main_topic_id, subtopic_name, description, difficulty_order)
                VALUES (?, ?, ?, ?)
            ''', (main_topic_id, subtopic_name, description, difficulty_order))
            conn.commit()