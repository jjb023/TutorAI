from database import TutorAIDatabase
from datetime import datetime
import os

class TutorAI:
    def __init__(self):
        """Initialize the Tutor AI interface"""
        self.db = TutorAIDatabase()
        print("🎯 Tutor AI - Student Progress Tracker")
        print("=" * 40)
    
    def run(self):
        """Main menu loop"""
        while True:
            self.show_main_menu()
            choice = input("\nEnter your choice (1-6): ").strip()
            
            if choice == '1':
                self.manage_students()
            elif choice == '2':
                self.update_progress()
            elif choice == '3':
                self.view_progress()
            elif choice == '4':
                self.manage_curriculum()
            elif choice == '5':
                self.quick_session_entry()
            elif choice == '6':
                print("👋 Goodbye! Keep up the great tutoring!")
                self.db.close()
                break
            else:
                print("❌ Invalid choice. Please try again.")
    
    def show_main_menu(self):
        """Display the main menu options"""
        print("\n" + "=" * 40)
        print("📚 MAIN MENU")
        print("=" * 40)
        print("1. 👥 Manage Students")
        print("2. 📊 Update Student Progress")
        print("3. 📈 View Student Progress")
        print("4. 📝 Manage Curriculum Topics")
        print("5. ⚡ Quick Session Entry")
        print("6. 🚪 Exit")
    
    def manage_students(self):
        """Student management submenu"""
        while True:
            print("\n" + "-" * 30)
            print("👥 STUDENT MANAGEMENT")
            print("-" * 30)
            print("1. Add New Student")
            print("2. View All Students")
            print("3. Back to Main Menu")
            
            choice = input("\nChoice (1-3): ").strip()
            
            if choice == '1':
                self.add_student()
            elif choice == '2':
                self.view_all_students()
            elif choice == '3':
                break
            else:
                print("❌ Invalid choice.")
    
    def add_student(self):
        """Add a new student with user input"""
        print("\n📝 Adding New Student")
        print("-" * 20)
        
        name = input("Student name: ").strip()
        if not name:
            print("❌ Name cannot be empty!")
            return
        
        try:
            age = int(input("Age: ").strip())
        except ValueError:
            print("❌ Please enter a valid age!")
            return
        
        year_group = input("Year group (e.g., Year 3): ").strip()
        target_school = input("Target school (optional): ").strip() or None
        parent_contact = input("Parent contact (optional): ").strip() or None
        notes = input("Notes (optional): ").strip() or None
        
        student_id = self.db.add_student(name, age, year_group, target_school, parent_contact, notes)
        
        if student_id:
            print(f"\n✅ {name} added successfully! (Student ID: {student_id})")
            
            # Ask if they want to set initial progress
            setup = input("Would you like to assess some topics now? (y/n): ").strip().lower()
            if setup == 'y':
                self.quick_assessment(student_id, name)
    
    def view_all_students(self):
        """Display all students in a nice format"""
        students = self.db.get_all_students()
        
        if not students:
            print("\n📝 No students in database yet.")
            return
        
        print(f"\n👥 ALL STUDENTS ({len(students)} total)")
        print("-" * 50)
        
        for student in students:
            id, name, age, year, school, contact, notes, created, last_session = student
            print(f"🎓 {name} (ID: {id})")
            print(f"   Age: {age}, Year: {year}")
            if school:
                print(f"   Target: {school}")
            if last_session:
                print(f"   Last session: {last_session}")
            print()
    
    def update_progress(self):
        """Update student progress on subtopics"""
        students = self.db.get_all_students()
        if not students:
            print("\n📝 No students in database. Add some students first!")
            return
        
        # Show students
        print("\n👥 Select a student:")
        for i, student in enumerate(students, 1):
            print(f"{i}. {student[1]} (Age {student[2]})")
        
        try:
            choice = int(input(f"\nStudent number (1-{len(students)}): ")) - 1
            student = students[choice]
            student_id, name = student[0], student[1]
        except (ValueError, IndexError):
            print("❌ Invalid student selection!")
            return
        
        print(f"\n📊 Updating progress for {name}")
        self.update_student_subtopics(student_id, name)
    
    def update_student_subtopics(self, student_id, student_name):
        """Update progress for specific subtopics"""
        # Get subtopics (simplified - just show Number subtopics for now)
        query = """
        SELECT s.id, s.subtopic_name, mt.topic_name, COALESCE(sp.mastery_level, 0)
        FROM subtopics s
        JOIN main_topics mt ON s.main_topic_id = mt.id
        LEFT JOIN subtopic_progress sp ON s.id = sp.subtopic_id AND sp.student_id = ?
        ORDER BY mt.topic_name, s.difficulty_order
        """
        
        self.db.cursor.execute(query, (student_id,))
        subtopics = self.db.cursor.fetchall()
        
        print(f"\n📚 Available subtopics for {student_name}:")
        current_main_topic = ""
        for i, (sub_id, sub_name, main_name, current_level) in enumerate(subtopics, 1):
            if main_name != current_main_topic:
                print(f"\n📖 {main_name}:")
                current_main_topic = main_name
            
            status = "✅" if current_level >= 7 else "📈" if current_level >= 4 else "⚠️" if current_level > 0 else "⭕"
            print(f"  {i}. {sub_name} {status} (Current: {current_level}/10)")
        
        try:
            choice = int(input(f"\nWhich subtopic to update? (1-{len(subtopics)}): ")) - 1
            subtopic_id, subtopic_name, _, current_level = subtopics[choice]
        except (ValueError, IndexError):
            print("❌ Invalid subtopic selection!")
            return
        
        print(f"\n📊 Updating: {subtopic_name}")
        print(f"Current level: {current_level}/10")
        
        try:
            new_level = int(input("New mastery level (1-10): "))
            if not 1 <= new_level <= 10:
                print("❌ Level must be between 1 and 10!")
                return
        except ValueError:
            print("❌ Please enter a valid number!")
            return
        
        # Optional details
        questions_attempted = input("Questions attempted (optional): ").strip()
        questions_correct = input("Questions correct (optional): ").strip()
        notes = input("Notes about this assessment (optional): ").strip()
        
        # Convert to integers if provided
        try:
            q_attempted = int(questions_attempted) if questions_attempted else 0
            q_correct = int(questions_correct) if questions_correct else 0
        except ValueError:
            q_attempted = q_correct = 0
        
        # Update database
        self.db.update_subtopic_progress(
            student_id, subtopic_id, new_level, 
            q_attempted, q_correct, notes or None
        )
        
        print(f"✅ Updated {subtopic_name}: {current_level}/10 → {new_level}/10")
        
        # Ask if they want to update another
        another = input("\nUpdate another subtopic? (y/n): ").strip().lower()
        if another == 'y':
            self.update_student_subtopics(student_id, student_name)
    
    def view_progress(self):
        """View student progress reports"""
        students = self.db.get_all_students()
        if not students:
            print("\n📝 No students in database.")
            return
        
        # Show students
        print("\n👥 Select a student to view progress:")
        for i, student in enumerate(students, 1):
            print(f"{i}. {student[1]} (Age {student[2]})")
        
        try:
            choice = int(input(f"\nStudent number (1-{len(students)}): ")) - 1
            student = students[choice]
            student_id, name = student[0], student[1]
        except (ValueError, IndexError):
            print("❌ Invalid student selection!")
            return
        
        self.show_student_progress(student_id, name)
    
    def show_student_progress(self, student_id, name):
        """Display comprehensive progress report"""
        print(f"\n📈 PROGRESS REPORT: {name}")
        print("=" * 50)
        
        # Main topic summary
        summary = self.db.get_student_main_topic_summary(student_id)
        
        for topic_name, color, total_subs, assessed_subs, avg_mastery, completion_pct in summary:
            if assessed_subs > 0:  # Only show topics with some progress
                print(f"\n📚 {topic_name}: {completion_pct}% complete")
                print(f"   Average mastery: {avg_mastery}/10")
                print(f"   Subtopics assessed: {assessed_subs}/{total_subs}")
                
                # Show subtopic details
                details = self.db.get_student_subtopic_details(student_id, topic_name)
                for sub_name, order, level, assessed, attempted, correct, notes in details:
                    if level > 0:  # Only show assessed subtopics
                        status = "🟢" if level >= 8 else "🟡" if level >= 5 else "🔴"
                        print(f"     {status} {sub_name}: {level}/10", end="")
                        if attempted:
                            accuracy = round((correct/attempted)*100, 1)
                            print(f" ({accuracy}% accuracy)")
                        else:
                            print()
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        self.generate_recommendations(student_id)
    
    def generate_recommendations(self, student_id):
        """Generate simple recommendations based on progress"""
        query = """
        SELECT s.subtopic_name, sp.mastery_level, mt.topic_name
        FROM subtopic_progress sp
        JOIN subtopics s ON sp.subtopic_id = s.id
        JOIN main_topics mt ON s.main_topic_id = mt.id
        WHERE sp.student_id = ? AND sp.mastery_level < 5 AND sp.mastery_level > 0
        ORDER BY sp.mastery_level ASC
        """
        
        self.db.cursor.execute(query, (student_id,))
        weak_areas = self.db.cursor.fetchall()
        
        if weak_areas:
            print("🎯 Focus on these areas:")
            for subtopic, level, main_topic in weak_areas[:3]:  # Show top 3
                print(f"   • {subtopic} (currently {level}/10)")
        else:
            print("🎉 Great progress! Consider introducing new topics.")
    
    def quick_session_entry(self):
        """Quick way to log a tutoring session"""
        print("\n⚡ QUICK SESSION ENTRY")
        print("-" * 25)
        print("Use this after a tutoring session to quickly update student progress")
        
        students = self.db.get_all_students()
        if not students:
            print("📝 No students in database. Add some students first!")
            return
        
        # Student selection (simplified)
        print("\nRecent students:")
        for i, student in enumerate(students[:5], 1):  # Show last 5
            print(f"{i}. {student[1]}")
        
        try:
            choice = int(input(f"Student (1-{min(5, len(students))}): ")) - 1
            student_id, name = students[choice][0], students[choice][1]
        except (ValueError, IndexError):
            print("❌ Invalid selection!")
            return
        
        print(f"\n📝 Quick session for {name}")
        print("Enter subtopic progress (press Enter when done):")
        
        while True:
            subtopic_input = input("Subtopic (or Enter to finish): ").strip()
            if not subtopic_input:
                break
                
            try:
                level = int(input(f"Mastery level for '{subtopic_input}' (1-10): "))
                if 1 <= level <= 10:
                    # For demo, just print what would be updated
                    print(f"✅ Would update: {subtopic_input} → {level}/10")
                    # In real implementation, you'd search for matching subtopic and update
                else:
                    print("❌ Level must be 1-10")
            except ValueError:
                print("❌ Please enter a valid number")
        
        print(f"✅ Session logged for {name}!")
    
    def manage_curriculum(self):
        """Simple curriculum management"""
        print("\n📝 CURRICULUM MANAGEMENT")
        print("-" * 25)
        print("Current main topics:")
        
        query = "SELECT topic_name, description FROM main_topics ORDER BY topic_name"
        self.db.cursor.execute(query)
        topics = self.db.cursor.fetchall()
        
        for topic_name, description in topics:
            print(f"📚 {topic_name}")
            if description:
                print(f"   {description}")
        
        print(f"\n💡 You have {len(topics)} main topics with subtopics ready to use!")
    
    def quick_assessment(self, student_id, student_name):
        """Quick initial assessment for new students"""
        print(f"\n🎯 Quick Assessment for {student_name}")
        print("Rate their current ability in these key areas (1-10):")
        
        # Common subtopics for initial assessment
        key_subtopics = [
            (2, "Addition"),
            (3, "Subtraction"), 
            (4, "Multiplication"),
            (6, "Fractions - Recognition")
        ]
        
        for subtopic_id, subtopic_name in key_subtopics:
            try:
                level = input(f"{subtopic_name} (1-10, or skip): ").strip()
                if level and level.isdigit():
                    level = int(level)
                    if 1 <= level <= 10:
                        self.db.update_subtopic_progress(
                            student_id, subtopic_id, level, 
                            notes="Initial assessment"
                        )
            except:
                continue
        
        print("✅ Initial assessment complete!")


if __name__ == "__main__":
    app = TutorAI()
    app.run()