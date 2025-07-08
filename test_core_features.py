import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import TutorAIDatabase
import sqlite3

class TestTutorAI:
    def __init__(self):
        self.db_path = os.path.join('data', 'tutor_ai.db')
        self.results = []
        self.passed = 0
        self.failed = 0
    
    def test(self, description, condition):
        """Run a test and record result"""
        try:
            result = condition()
            if result:
                self.passed += 1
                self.results.append(f"✅ PASS: {description}")
                return True
            else:
                self.failed += 1
                self.results.append(f"❌ FAIL: {description}")
                return False
        except Exception as e:
            self.failed += 1
            self.results.append(f"❌ ERROR: {description} - {str(e)}")
            return False
    
    def run_tests(self):
        """Run all tests"""
        print("🧪 Testing Tutor AI Core Features")
        print("=" * 50)
        
        # Test 1: Database exists and has correct tables
        self.test_database_structure()
        
        # Test 2: Authentication system
        self.test_authentication()
        
        # Test 3: Student management
        self.test_student_management()
        
        # Test 4: Topic and subtopic structure
        self.test_topic_structure()
        
        # Test 5: Progress tracking
        self.test_progress_tracking()
        
        # Test 6: Session management
        self.test_session_management()
        
        # Print results
        print("\n" + "=" * 50)
        print("📊 Test Results:")
        print("=" * 50)
        for result in self.results:
            print(result)
        
        print(f"\n📈 Summary: {self.passed} passed, {self.failed} failed")
        print("=" * 50)
    
    def test_database_structure(self):
        """Test database tables exist"""
        print("\n📁 Testing Database Structure...")
        
        self.test("Database file exists", 
                 lambda: os.path.exists(self.db_path))
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check tables
        required_tables = ['students', 'tutors', 'main_topics', 'subtopics', 
                          'sessions', 'subtopic_progress']
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        existing_tables = [table[0] for table in cursor.fetchall()]
        
        for table in required_tables:
            self.test(f"Table '{table}' exists", 
                     lambda t=table: t in existing_tables)
        
        conn.close()
    
    def test_authentication(self):
        """Test tutor authentication"""
        print("\n🔐 Testing Authentication...")
        
        db = TutorAIDatabase(self.db_path)
        
        # Check admin exists
        db.cursor.execute("SELECT COUNT(*) FROM tutors WHERE username = 'admin'")
        admin_exists = db.cursor.fetchone()[0] > 0
        self.test("Admin account exists", lambda: admin_exists)
        
        # Check at least one tutor exists
        db.cursor.execute("SELECT COUNT(*) FROM tutors WHERE active = 1")
        tutor_count = db.cursor.fetchone()[0]
        self.test("At least one active tutor exists", lambda: tutor_count > 0)
        
        db.close()
    
    def test_student_management(self):
        """Test student CRUD operations"""
        print("\n👥 Testing Student Management...")
        
        db = TutorAIDatabase(self.db_path)
        
        # Test adding a student
        test_student_name = "Test Student 123"
        student_id = db.add_student(test_student_name, 10, "Year 5", 
                                   "Test School", "test@parent.com", "Test notes")
        
        self.test("Can add new student", lambda: student_id is not None)
        
        # Test retrieving student
        if student_id:
            db.cursor.execute("SELECT name FROM students WHERE id = ?", (student_id,))
            result = db.cursor.fetchone()
            self.test("Can retrieve added student", 
                     lambda: result and result[0] == test_student_name)
            
            # Clean up - delete test student
            db.cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
            db.connection.commit()
        
        # Test student count
        students = db.get_all_students()
        self.test("Can get all students", lambda: isinstance(students, list))
        
        db.close()
    
    def test_topic_structure(self):
        """Test topic and subtopic structure"""
        print("\n📚 Testing Topic Structure...")
        
        db = TutorAIDatabase(self.db_path)
        
        # Check main topics exist
        topics = db.get_all_main_topics()
        self.test("Main topics exist", lambda: len(topics) > 0)
        
        # Check subtopics exist for at least one topic
        if topics:
            topic_id = topics[0][0]  # First topic's ID
            subtopics = db.get_subtopics_by_main_topic(topic_id)
            self.test("Subtopics exist for topics", lambda: len(subtopics) > 0)
        
        # Test Number topic specifically
        db.cursor.execute("SELECT id FROM main_topics WHERE topic_name = 'Number'")
        number_topic = db.cursor.fetchone()
        self.test("'Number' topic exists", lambda: number_topic is not None)
        
        db.close()
    
    def test_progress_tracking(self):
        """Test progress tracking functionality"""
        print("\n📊 Testing Progress Tracking...")
        
        db = TutorAIDatabase(self.db_path)
        
        # Get a student and subtopic for testing
        students = db.get_all_students()
        if students:
            student_id = students[0][0]
            
            # Get a subtopic
            db.cursor.execute("SELECT id FROM subtopics LIMIT 1")
            subtopic = db.cursor.fetchone()
            
            if subtopic:
                subtopic_id = subtopic[0]
                
                # Test updating progress
                db.update_subtopic_progress(student_id, subtopic_id, 7, 10, 8, "Test progress")
                
                # Verify it saved
                db.cursor.execute("""
                    SELECT mastery_level FROM subtopic_progress 
                    WHERE student_id = ? AND subtopic_id = ?
                """, (student_id, subtopic_id))
                
                result = db.cursor.fetchone()
                self.test("Progress update saves correctly", 
                         lambda: result and result[0] == 7)
                
                # Test mastery level bounds
                self.test("Mastery level within bounds (1-10)", 
                         lambda: result and 1 <= result[0] <= 10)
        
        db.close()
    
    def test_session_management(self):
        """Test session creation and management"""
        print("\n⚡ Testing Session Management...")
        
        db = TutorAIDatabase(self.db_path)
        
        # Get required IDs
        students = db.get_all_students()
        tutors = db.get_all_tutors()
        
        if students and tutors:
            student_id = students[0][0]
            tutor_id = tutors[0][0]
            
            # Create a test session
            session_id = db.create_session_with_tutor(
                student_id, tutor_id, 60, "Test topics", "Test notes", "Test homework"
            )
            
            self.test("Can create session", lambda: session_id is not None)
            
            if session_id:
                # Check session was created
                db.cursor.execute("SELECT id FROM sessions WHERE id = ?", (session_id,))
                result = db.cursor.fetchone()
                self.test("Session saved to database", lambda: result is not None)
                
                # Clean up
                db.cursor.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
                db.connection.commit()
        
        db.close()

if __name__ == "__main__":
    tester = TestTutorAI()
    tester.run_tests()
    
    print("\n💡 Next steps:")
    print("1. Run through the manual testing checklist")
    print("2. Fix any failed tests")
    print("3. Test the web interface thoroughly")
    print("4. Consider adding more automated tests")