import sqlite3
import os
from datetime import datetime

class TutorAIDatabase:
    def __init__(self, db_path="tutor_ai.db"):
        """Initialize database connection and create tables if they don't exist"""
        self.db_path = db_path
        self.connection = sqlite3.connect(db_path)
        self.cursor = self.connection.cursor()
        self.create_tables()
        
    def create_tables(self):
        """Create all necessary tables"""
        
        # Students table - our foundation
        students_table = """
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER,
            year_group TEXT,
            target_school TEXT,
            parent_contact TEXT,
            notes TEXT,
            created_date TEXT DEFAULT CURRENT_TIMESTAMP,
            last_session_date TEXT
        );
        """
        
        # Main Topics table (Number, Algebra, Geometry, etc.)
        main_topics_table = """
        CREATE TABLE IF NOT EXISTS main_topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic_name TEXT NOT NULL UNIQUE,
            description TEXT,
            target_year_groups TEXT,
            color_code TEXT
        );
        """
        
        # Subtopics table (Adding Fractions, Multiplying Decimals, etc.)
        subtopics_table = """
        CREATE TABLE IF NOT EXISTS subtopics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            main_topic_id INTEGER,
            subtopic_name TEXT NOT NULL,
            description TEXT,
            difficulty_order INTEGER,
            prerequisite_subtopic_id INTEGER,
            FOREIGN KEY (main_topic_id) REFERENCES main_topics(id),
            FOREIGN KEY (prerequisite_subtopic_id) REFERENCES subtopics(id)
        );
        """
        
        # Student Progress - tracks mastery levels for each subtopic
        subtopic_progress_table = """
        CREATE TABLE IF NOT EXISTS subtopic_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            subtopic_id INTEGER,
            mastery_level INTEGER DEFAULT 1,
            last_assessed TEXT,
            questions_attempted INTEGER DEFAULT 0,
            questions_correct INTEGER DEFAULT 0,
            notes TEXT,
            FOREIGN KEY (student_id) REFERENCES students(id),
            FOREIGN KEY (subtopic_id) REFERENCES subtopics(id),
            UNIQUE(student_id, subtopic_id)
        );
        """
        
        # Sessions table for tracking when assessments happened
        sessions_table = """
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            session_date TEXT DEFAULT CURRENT_TIMESTAMP,
            duration_minutes INTEGER,
            main_topics_covered TEXT,
            tutor_notes TEXT,
            homework_set TEXT,
            FOREIGN KEY (student_id) REFERENCES students(id)
        );
        """
        
        # Execute table creation
        tables = [students_table, main_topics_table, subtopics_table, 
                 subtopic_progress_table, sessions_table]
        
        for table in tables:
            self.cursor.execute(table)
        
        self.connection.commit()
        print("✅ Database tables created successfully!")
        
        # Add some default curriculum structure
        self._add_default_curriculum()
    
    def _add_default_curriculum(self):
        """Add basic UK curriculum structure if tables are empty"""
        # Check if we already have main topics
        self.cursor.execute("SELECT COUNT(*) FROM main_topics")
        if self.cursor.fetchone()[0] > 0:
            return  # Already populated
        
        # Add main topics
        main_topics = [
            ("Number", "Basic arithmetic, fractions, decimals, percentages", "Year 1-6", "#FF6B6B"),
            ("Algebra", "Patterns, equations, expressions", "Year 4-6", "#4ECDC4"),
            ("Geometry", "Shapes, angles, measurements", "Year 1-6", "#45B7D1"),
            ("Statistics", "Data handling, graphs, probability", "Year 3-6", "#96CEB4"),
            ("Measurement", "Length, weight, time, money", "Year 1-6", "#FFEAA7")
        ]
        
        topic_ids = {}
        for topic_name, desc, years, color in main_topics:
            topic_id = self.add_main_topic(topic_name, desc, years, color)
            topic_ids[topic_name] = topic_id
        
        # Add subtopics for Number (example)
        if "Number" in topic_ids:
            number_subtopics = [
                ("Counting and Place Value", "Understanding number values and counting", 1),
                ("Addition", "Adding whole numbers", 2),
                ("Subtraction", "Subtracting whole numbers", 3),
                ("Multiplication", "Times tables and multiplication", 4),
                ("Division", "Dividing whole numbers", 5),
                ("Fractions - Recognition", "Identifying and understanding fractions", 6),
                ("Fractions - Addition", "Adding fractions with same denominator", 7),
                ("Fractions - Subtraction", "Subtracting fractions", 8),
                ("Decimals - Recognition", "Understanding decimal notation", 9),
                ("Decimals - Addition", "Adding decimal numbers", 10),
                ("Percentages", "Understanding percentages", 11)
            ]
            
            for subtopic_name, desc, order in number_subtopics:
                self.add_subtopic(topic_ids["Number"], subtopic_name, desc, order)
    
    def add_main_topic(self, topic_name, description=None, target_year_groups=None, color_code=None):
        """Add a main curriculum topic"""
        query = """
        INSERT OR IGNORE INTO main_topics (topic_name, description, target_year_groups, color_code)
        VALUES (?, ?, ?, ?)
        """
        
        try:
            self.cursor.execute(query, (topic_name, description, target_year_groups, color_code))
            self.connection.commit()
            topic_id = self.cursor.lastrowid
            if topic_id:
                print(f"✅ Added main topic: {topic_name} (ID: {topic_id})")
            return topic_id
        except sqlite3.Error as e:
            print(f"❌ Error adding main topic: {e}")
            return None
    
    def add_subtopic(self, main_topic_id, subtopic_name, description=None, difficulty_order=1, prerequisite_id=None):
        """Add a subtopic under a main topic"""
        query = """
        INSERT INTO subtopics (main_topic_id, subtopic_name, description, difficulty_order, prerequisite_subtopic_id)
        VALUES (?, ?, ?, ?, ?)
        """
        
        try:
            self.cursor.execute(query, (main_topic_id, subtopic_name, description, difficulty_order, prerequisite_id))
            self.connection.commit()
            subtopic_id = self.cursor.lastrowid
            print(f"✅ Added subtopic: {subtopic_name} (ID: {subtopic_id})")
            return subtopic_id
        except sqlite3.Error as e:
            print(f"❌ Error adding subtopic: {e}")
            return None
    
    def add_student(self, name, age, year_group, target_school=None, parent_contact=None, notes=None):
        """Add a new student to the database"""
        query = """
        INSERT INTO students (name, age, year_group, target_school, parent_contact, notes)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        
        try:
            self.cursor.execute(query, (name, age, year_group, target_school, parent_contact, notes))
            self.connection.commit()
            student_id = self.cursor.lastrowid
            print(f"✅ Added student: {name} (ID: {student_id})")
            return student_id
        except sqlite3.Error as e:
            print(f"❌ Error adding student: {e}")
            return None
    
    def update_subtopic_progress(self, student_id, subtopic_id, mastery_level, questions_attempted=0, questions_correct=0, notes=None):
        """Update or insert student progress for a specific subtopic"""
        current_time = datetime.now().isoformat()
        
        query = """
        INSERT OR REPLACE INTO subtopic_progress 
        (student_id, subtopic_id, mastery_level, last_assessed, questions_attempted, questions_correct, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        
        try:
            self.cursor.execute(query, (student_id, subtopic_id, mastery_level, current_time, questions_attempted, questions_correct, notes))
            self.connection.commit()
            print(f"✅ Updated subtopic progress: Student {student_id}, Subtopic {subtopic_id}, Level {mastery_level}/10")
        except sqlite3.Error as e:
            print(f"❌ Error updating progress: {e}")

    def find_subtopic_by_name(self, search_term):
        """Find subtopic by name (case-insensitive, partial match)"""
        query = """
        SELECT s.id, s.subtopic_name, mt.topic_name
        FROM subtopics s
        JOIN main_topics mt ON s.main_topic_id = mt.id
        WHERE LOWER(s.subtopic_name) LIKE LOWER(?)
        ORDER BY s.subtopic_name
        """
        
        try:
            self.cursor.execute(query, (f"%{search_term}%",))
            results = self.cursor.fetchall()
            return results
        except sqlite3.Error as e:
            print(f"❌ Error searching subtopics: {e}")
            return []
    
    def get_student_main_topic_summary(self, student_id):
        """Get completion percentage for each main topic"""
        query = """
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
        """
        
        try:
            self.cursor.execute(query, (student_id,))
            results = self.cursor.fetchall()
            return results
        except sqlite3.Error as e:
            print(f"❌ Error getting topic summary: {e}")
            return []
    
    def get_student_subtopic_details(self, student_id, main_topic_name):
        """Get detailed subtopic progress for a specific main topic"""
        query = """
        SELECT 
            s.subtopic_name,
            s.difficulty_order,
            COALESCE(sp.mastery_level, 0) as mastery_level,
            sp.last_assessed,
            sp.questions_attempted,
            sp.questions_correct,
            sp.notes
        FROM subtopics s
        JOIN main_topics mt ON s.main_topic_id = mt.id
        LEFT JOIN subtopic_progress sp ON s.id = sp.subtopic_id AND sp.student_id = ?
        WHERE mt.topic_name = ?
        ORDER BY s.difficulty_order
        """
        
        try:
            self.cursor.execute(query, (student_id, main_topic_name))
            results = self.cursor.fetchall()
            return results
        except sqlite3.Error as e:
            print(f"❌ Error getting subtopic details: {e}")
            return []
    
    def get_all_students(self):
        """Get all students from database"""
        query = "SELECT * FROM students ORDER BY name"
        try:
            self.cursor.execute(query)
            students = self.cursor.fetchall()
            return students
        except sqlite3.Error as e:
            print(f"❌ Error getting students: {e}")
            return []
    
    def close(self):
        """Close database connection"""
        self.connection.close()
        print("📚 Database connection closed")

    def upgrade_for_multitutor(self):
        """Upgrade database to support multiple tutors - preserves existing data"""
        print("🔄 Upgrading database for multi-tutor support...")
        
        # Add tutors table
        tutors_table = """
        CREATE TABLE IF NOT EXISTS tutors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            email TEXT,
            created_date TEXT DEFAULT CURRENT_TIMESTAMP,
            last_login TEXT,
            active BOOLEAN DEFAULT 1
        );
        """
        
        # Add year groups table for better curriculum organization
        year_groups_table = """
        CREATE TABLE IF NOT EXISTS year_groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year_name TEXT UNIQUE NOT NULL,
            description TEXT,
            age_range TEXT,
            active BOOLEAN DEFAULT 1
        );
        """
        
        # Execute table creation
        self.cursor.execute(tutors_table)
        self.cursor.execute(year_groups_table)
        
        # Add tutor_id column to sessions table if it doesn't exist
        try:
            self.cursor.execute("ALTER TABLE sessions ADD COLUMN tutor_id INTEGER REFERENCES tutors(id)")
            print("✅ Added tutor_id column to sessions table")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print("✅ tutor_id column already exists in sessions table")
            else:
                print(f"⚠️ Error adding tutor_id column: {e}")
        
        # Add default tutor if none exist
        self.cursor.execute("SELECT COUNT(*) FROM tutors")
        if self.cursor.fetchone()[0] == 0:
            default_tutor = """
            INSERT INTO tutors (username, password_hash, full_name, email)
            VALUES ('admin', 'temp_password_hash', 'Default Tutor', 'admin@tutorai.local')
            """
            self.cursor.execute(default_tutor)
            print("✅ Added default tutor account")
        
        # Add default year groups if none exist
        self.cursor.execute("SELECT COUNT(*) FROM year_groups")
        if self.cursor.fetchone()[0] == 0:
            default_year_groups = [
                ("Year 3", "Ages 7-8", "7-8 years"),
                ("Year 4", "Ages 8-9", "8-9 years"),
                ("Year 5", "Ages 9-10", "9-10 years"),
                ("Year 6", "Ages 10-11", "10-11 years")
            ]
            
            for year_name, description, age_range in default_year_groups:
                self.cursor.execute(
                    "INSERT INTO year_groups (year_name, description, age_range) VALUES (?, ?, ?)",
                    (year_name, description, age_range)
                )
            print("✅ Added default year groups")
        
        self.connection.commit()
        print("🎉 Database upgraded for multi-tutor support!")
        print("💡 All existing data preserved")

    def add_tutor(self, username, password_hash, full_name, email=None):
        """Add a new tutor to the database"""
        query = """
        INSERT INTO tutors (username, password_hash, full_name, email)
        VALUES (?, ?, ?, ?)
        """
        
        try:
            self.cursor.execute(query, (username, password_hash, full_name, email))
            self.connection.commit()
            tutor_id = self.cursor.lastrowid
            print(f"✅ Added tutor: {full_name} (Username: {username})")
            return tutor_id
        except sqlite3.IntegrityError:
            print(f"❌ Username '{username}' already exists!")
            return None
        except sqlite3.Error as e:
            print(f"❌ Error adding tutor: {e}")
            return None

    def get_all_tutors(self):
        """Get all active tutors"""
        query = "SELECT id, username, full_name, email, last_login FROM tutors WHERE active = 1 ORDER BY full_name"
        try:
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"❌ Error getting tutors: {e}")
            return []

    def create_session_with_tutor(self, student_id, tutor_id, duration_minutes=None, topics_covered=None, notes=None, homework=None):
        """Create a session record with tutor attribution"""
        query = """
        INSERT INTO sessions (student_id, tutor_id, duration_minutes, main_topics_covered, tutor_notes, homework_set)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        
        try:
            self.cursor.execute(query, (student_id, tutor_id, duration_minutes, topics_covered, notes, homework))
            self.connection.commit()
            
            # Update student's last session date
            self.cursor.execute(
                "UPDATE students SET last_session_date = CURRENT_TIMESTAMP WHERE id = ?",
                (student_id,)
            )
            self.connection.commit()
            
            session_id = self.cursor.lastrowid
            print(f"✅ Session created: Student {student_id}, Tutor {tutor_id}")
            return session_id
        except sqlite3.Error as e:
            print(f"❌ Error creating session: {e}")
            return None
        
    def get_all_main_topics(self):
        """Get all main topics"""
        query = "SELECT * FROM main_topics ORDER BY topic_name"
        try:
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"❌ Error getting main topics: {e}")
            return []

    def get_main_topic(self, topic_id):
        """Get a specific main topic by ID"""
        query = "SELECT * FROM main_topics WHERE id = ?"
        try:
            self.cursor.execute(query, (topic_id,))
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            print(f"❌ Error getting main topic: {e}")
            return None

    def update_main_topic(self, topic_id, topic_name, description=None, target_year_groups=None, color_code=None):
        """Update a main topic"""
        query = """
        UPDATE main_topics 
        SET topic_name = ?, description = ?, target_year_groups = ?, color_code = ?
        WHERE id = ?
        """
        try:
            self.cursor.execute(query, (topic_name, description, target_year_groups, color_code, topic_id))
            self.connection.commit()
            print(f"✅ Updated main topic: {topic_name}")
            return True
        except sqlite3.Error as e:
            print(f"❌ Error updating main topic: {e}")
            return False

    def delete_main_topic(self, topic_id):
        """Delete a main topic and all its subtopics"""
        try:
            # First delete all subtopics
            self.cursor.execute("DELETE FROM subtopics WHERE main_topic_id = ?", (topic_id,))
            # Then delete the main topic
            self.cursor.execute("DELETE FROM main_topics WHERE id = ?", (topic_id,))
            self.connection.commit()
            print(f"✅ Deleted main topic and its subtopics")
            return True
        except sqlite3.Error as e:
            print(f"❌ Error deleting main topic: {e}")
            return False

    def get_subtopics_by_main_topic(self, main_topic_id):
        """Get all subtopics for a main topic"""
        query = """
        SELECT * FROM subtopics 
        WHERE main_topic_id = ? 
        ORDER BY difficulty_order
        """
        try:
            self.cursor.execute(query, (main_topic_id,))
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"❌ Error getting subtopics: {e}")
            return []

    def update_subtopic(self, subtopic_id, subtopic_name, description=None, difficulty_order=1):
        """Update a subtopic"""
        query = """
        UPDATE subtopics 
        SET subtopic_name = ?, description = ?, difficulty_order = ?
        WHERE id = ?
        """
        try:
            self.cursor.execute(query, (subtopic_name, description, difficulty_order, subtopic_id))
            self.connection.commit()
            print(f"✅ Updated subtopic: {subtopic_name}")
            return True
        except sqlite3.Error as e:
            print(f"❌ Error updating subtopic: {e}")
            return False

    def delete_subtopic(self, subtopic_id):
        """Delete a subtopic"""
        try:
            # First delete any progress records for this subtopic
            self.cursor.execute("DELETE FROM subtopic_progress WHERE subtopic_id = ?", (subtopic_id,))
            # Then delete the subtopic
            self.cursor.execute("DELETE FROM subtopics WHERE id = ?", (subtopic_id,))
            self.connection.commit()
            print(f"✅ Deleted subtopic")
            return True
        except sqlite3.Error as e:
            print(f"❌ Error deleting subtopic: {e}")
            return False
        
    
        


# Demo usage and testing
if __name__ == "__main__":
    print("🚀 Setting up Tutor AI Database with Hierarchical Topics...")
    
    # Initialize database
    db = TutorAIDatabase()
    
    # Add some sample students
    print("\n📝 Adding sample students...")
    alice_id = db.add_student("Alice Smith", 8, "Year 3", "St. Mary's Primary")
    bob_id = db.add_student("Bob Johnson", 9, "Year 4", "Riverside Academy")
    
    # Record some progress on subtopics
    print("\n📊 Recording student progress on subtopics...")
    if alice_id:
        # Alice is good at basic fractions but struggles with adding them
        db.update_subtopic_progress(alice_id, 6, 8, 15, 13, "Understands fractions well")  # Fractions - Recognition
        db.update_subtopic_progress(alice_id, 7, 4, 12, 6, "Struggles with different denominators")  # Fractions - Addition
        db.update_subtopic_progress(alice_id, 2, 9, 20, 19, "Addition is strong")  # Addition
        db.update_subtopic_progress(alice_id, 4, 7, 25, 20, "Times tables good up to 7x")  # Multiplication
    
    if bob_id:
        # Bob is strong across the board but needs decimal work
        db.update_subtopic_progress(bob_id, 6, 9, 10, 10, "Excellent fraction understanding")
        db.update_subtopic_progress(bob_id, 7, 8, 15, 13, "Can add fractions confidently")
        db.update_subtopic_progress(bob_id, 9, 3, 8, 4, "Decimal place value confusion")  # Decimals - Recognition
    
    # Show main topic summaries
    print("\n📈 Alice's Main Topic Summary:")
    alice_summary = db.get_student_main_topic_summary(alice_id)
    for topic_name, color, total_subs, assessed_subs, avg_mastery, completion_pct in alice_summary:
        print(f"  {topic_name}: {completion_pct}% complete, Average level: {avg_mastery}/10")
        print(f"    Assessed {assessed_subs}/{total_subs} subtopics")
    
    # Show detailed Number breakdown for Alice
    print(f"\n🔍 Alice's Number Subtopic Details:")
    alice_number_details = db.get_student_subtopic_details(alice_id, "Number")
    for subtopic_name, order, level, assessed, attempted, correct, notes in alice_number_details:
        status = "📈" if level >= 7 else "⚠️" if level >= 4 else "❌" if level > 0 else "⭕"
        print(f"  {status} {subtopic_name}: {level}/10", end="")
        if attempted:
            accuracy = round((correct/attempted)*100, 1)
            print(f" ({accuracy}% accuracy, {attempted} questions)")
        else:
            print(" (Not assessed)")
        if notes:
            print(f"      Notes: {notes}")
    
    # Close database
    db.close()
    
    print(f"\n🎉 Hierarchical database setup complete!")
    print("💡 Now you can track detailed progress: Main topics show completion %, subtopics show 1-10 mastery!")