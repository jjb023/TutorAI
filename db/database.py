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
        
        # Topics table - curriculum structure
        topics_table = """
        CREATE TABLE IF NOT EXISTS topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic_name TEXT NOT NULL,
            parent_topic TEXT,
            difficulty_min INTEGER DEFAULT 1,
            difficulty_max INTEGER DEFAULT 10,
            description TEXT
        );
        """
        
        # Student Progress - tracks mastery levels
        progress_table = """
        CREATE TABLE IF NOT EXISTS student_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            topic_id INTEGER,
            mastery_level INTEGER DEFAULT 1,
            last_assessed TEXT,
            notes TEXT,
            FOREIGN KEY (student_id) REFERENCES students(id),
            FOREIGN KEY (topic_id) REFERENCES topics(id)
        );
        """
        
        # Execute table creation
        self.cursor.execute(students_table)
        self.cursor.execute(topics_table)
        self.cursor.execute(progress_table)
        self.connection.commit()
        print("✅ Database tables created successfully!")
    
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
    
    def get_student_by_id(self, student_id):
        """Get specific student by ID"""
        query = "SELECT * FROM students WHERE id = ?"
        try:
            self.cursor.execute(query, (student_id,))
            student = self.cursor.fetchone()
            return student
        except sqlite3.Error as e:
            print(f"❌ Error getting student: {e}")
            return None
    
    def add_topic(self, topic_name, parent_topic=None, difficulty_min=1, difficulty_max=10, description=None):
        """Add a curriculum topic"""
        query = """
        INSERT INTO topics (topic_name, parent_topic, difficulty_min, difficulty_max, description)
        VALUES (?, ?, ?, ?, ?)
        """
        
        try:
            self.cursor.execute(query, (topic_name, parent_topic, difficulty_min, difficulty_max, description))
            self.connection.commit()
            topic_id = self.cursor.lastrowid
            print(f"✅ Added topic: {topic_name} (ID: {topic_id})")
            return topic_id
        except sqlite3.Error as e:
            print(f"❌ Error adding topic: {e}")
            return None
    
    def update_student_progress(self, student_id, topic_id, mastery_level, notes=None):
        """Update or insert student progress for a topic"""
        # Check if progress record exists
        check_query = """
        SELECT id FROM student_progress 
        WHERE student_id = ? AND topic_id = ?
        """
        
        self.cursor.execute(check_query, (student_id, topic_id))
        existing = self.cursor.fetchone()
        
        current_time = datetime.now().isoformat()
        
        if existing:
            # Update existing record
            update_query = """
            UPDATE student_progress 
            SET mastery_level = ?, last_assessed = ?, notes = ?
            WHERE student_id = ? AND topic_id = ?
            """
            self.cursor.execute(update_query, (mastery_level, current_time, notes, student_id, topic_id))
        else:
            # Insert new record
            insert_query = """
            INSERT INTO student_progress (student_id, topic_id, mastery_level, last_assessed, notes)
            VALUES (?, ?, ?, ?, ?)
            """
            self.cursor.execute(insert_query, (student_id, topic_id, mastery_level, current_time, notes))
        
        self.connection.commit()
        print(f"✅ Updated progress: Student {student_id}, Topic {topic_id}, Level {mastery_level}")
    
    def get_student_progress(self, student_id):
        """Get all progress for a specific student"""
        query = """
        SELECT 
            topics.topic_name,
            student_progress.mastery_level,
            student_progress.last_assessed,
            student_progress.notes
        FROM student_progress
        JOIN topics ON student_progress.topic_id = topics.id
        WHERE student_progress.student_id = ?
        ORDER BY topics.topic_name
        """
        
        try:
            self.cursor.execute(query, (student_id,))
            progress = self.cursor.fetchall()
            return progress
        except sqlite3.Error as e:
            print(f"❌ Error getting progress: {e}")
            return []
    
    def close(self):
        """Close database connection"""
        self.connection.close()
        print("📚 Database connection closed")


# Demo usage and testing
if __name__ == "__main__":
    print("🚀 Setting up Tutor AI Database...")
    
    # Initialize database
    db = TutorAIDatabase()
    
    # Add some sample students
    print("\n📝 Adding sample students...")
    alice_id = db.add_student("Alice Smith", 8, "Year 3", "St. Mary's Primary", "alice.parent@email.com")
    bob_id = db.add_student("Bob Johnson", 9, "Year 4", "Riverside Academy", "bob.parent@email.com")
    charlie_id = db.add_student("Charlie Brown", 7, "Year 2", notes="Struggles with concentration")
    
    # Add some curriculum topics
    print("\n📚 Adding curriculum topics...")
    fractions_id = db.add_topic("Fractions", "Number", 1, 8, "Understanding parts of a whole")
    decimals_id = db.add_topic("Decimals", "Number", 3, 9, "Decimal notation and operations")
    algebra_id = db.add_topic("Basic Algebra", "Algebra", 5, 10, "Simple equations and expressions")
    
    # Record some progress
    print("\n📊 Recording student progress...")
    if alice_id and fractions_id:
        db.update_student_progress(alice_id, fractions_id, 6, "Good understanding of basic fractions")
    if bob_id and decimals_id:
        db.update_student_progress(bob_id, decimals_id, 4, "Needs more practice with decimal places")
    
    # Display all students
    print("\n👥 All students in database:")
    students = db.get_all_students()
    for student in students:
        print(f"ID: {student[0]}, Name: {student[1]}, Age: {student[2]}, Year: {student[3]}")
    
    # Show Alice's progress
    if alice_id:
        print(f"\n📈 Alice's progress:")
        progress = db.get_student_progress(alice_id)
        for topic, level, assessed, notes in progress:
            print(f"  {topic}: Level {level}/10 (Last assessed: {assessed})")
            if notes:
                print(f"    Notes: {notes}")
    
    # Close database
    db.close()
    
    print(f"\n🎉 Database setup complete! File created: {os.path.abspath('tutor_ai.db')}")
    print("💡 Next steps: Run this script to create your database, then start adding real student data!")