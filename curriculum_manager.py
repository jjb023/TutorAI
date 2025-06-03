# curriculum_manager.py
# Import will be done locally to avoid circular imports

class CurriculumManager:
    def __init__(self, db_path="data/tutor_ai.db"):
        # Import locally to avoid circular imports
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from database import TutorAIDatabase
        self.db = TutorAIDatabase(db_path)
    
    def setup_7plus_curriculum(self):
        """Set up complete 7+ maths curriculum structure"""
        print("🔄 Setting up 7+ Maths Curriculum...")
        
        # Clear existing curriculum if needed
        # self.clear_curriculum()  # Uncomment if you want to start fresh
        
        # Main curriculum areas based on 7+ syllabus
        curriculum_areas = {
            "Number and Number System": {
                "description": "Counting, place value, ordering, fractions, estimation",
                "color": "#FF6B6B",
                "subtopics": [
                    # Counting and Properties
                    ("Counting to 100", "Count reliably up to 100 objects by grouping", 1, "counting"),
                    ("Number Sequences", "Count in steps of 1,2,3,4,5,10 from any two-digit number", 2, "sequences"),
                    ("Counting in Hundreds", "Count in hundreds from and back to zero", 3, "hundreds"),
                    ("Odd and Even Numbers", "Recognise odd and even numbers", 4, "odd_even"),
                    ("Multiples Recognition", "Recognise two-digit multiples of 2, 5 or 10", 5, "multiples"),
                    
                    # Place Value and Ordering
                    ("Reading Three-Digit Numbers", "Read and write three-digit numbers in figures and words", 6, "three_digit"),
                    ("Two-Digit Place Value", "Know what each digit represents including 0 as placeholder", 7, "place_value"),
                    ("Comparing Numbers", "Use vocabulary of comparing and ordering numbers", 8, "comparing"),
                    ("Equality Symbol", "Use the = sign to represent equality", 9, "equality"),
                    ("Number Comparison", "Compare two-digit numbers and find numbers between", 10, "comparison"),
                    ("Number Lines", "Order numbers on 100 square and position on number line", 11, "number_lines"),
                    
                    # Estimation and Rounding
                    ("Estimation Vocabulary", "Use vocabulary of estimation and approximation", 12, "estimation"),
                    ("Rounding to 10", "Round any two-digit number to the nearest 10", 13, "rounding"),
                    
                    # Fractions
                    ("Halves and Quarters", "Recognise and find 1/2 and 1/4 of shapes and numbers", 14, "basic_fractions"),
                    ("Fraction Equivalence", "Understand 2 halves = 1 whole, 4 quarters = 1 whole", 15, "fraction_equiv"),
                ]
            },
            
            "Calculations": {
                "description": "Addition, subtraction, multiplication, division strategies",
                "color": "#4ECDC4",
                "subtopics": [
                    # Addition and Subtraction Understanding
                    ("Addition Operations", "Understand addition operations and vocabulary", 1, "add_ops"),
                    ("Mathematical Symbols", "Use +, -, = signs and unknown number symbols", 2, "symbols"),
                    ("Inverse Operations", "Understand subtraction as inverse of addition", 3, "inverse"),
                    ("Addition Properties", "Recognise addition can be done in any order", 4, "add_properties"),
                    ("Three Single Digits", "Add three single-digit numbers mentally (to 27)", 5, "three_digits"),
                    ("Two-Digit Addition", "Add two two-digit numbers (totals to 100)", 6, "two_digit_add"),
                    
                    # Number Facts
                    ("Addition Facts to 20", "Know all addition facts to 20 by heart", 7, "facts_20"),
                    ("Pairs to 100", "Know pairs of multiples of 10 totalling 100", 8, "pairs_100"),
                    ("TU + U to 50", "Derive TU + U to 50 and corresponding subtractions", 9, "tu_plus_u"),
                    
                    # Mental Strategies
                    ("Mental Add/Subtract", "Use variety of methods for addition/subtraction", 10, "mental_add_sub"),
                    ("Related Facts", "State subtraction corresponding to addition and vice versa", 11, "related_facts"),
                    
                    # Multiplication and Division Understanding
                    ("Multiplication Concept", "Understand multiplication as repeated addition/arrays", 12, "mult_concept"),
                    ("Division Concept", "Understand division as grouping or sharing", 13, "div_concept"),
                    ("Multiplication Symbols", "Use x, ÷, = signs in calculations", 14, "mult_symbols"),
                    ("Halving and Doubling", "Know halving as inverse of doubling", 15, "halving_doubling"),
                    
                    # Times Tables
                    ("2 Times Table", "Know 2 times table by heart", 16, "times_2"),
                    ("5 Times Table", "Know 5 times table by heart", 17, "times_5"),
                    ("10 Times Table", "Know 10 times table by heart", 18, "times_10"),
                    ("Doubles to 10", "Know doubles of all numbers to 10", 19, "doubles_10"),
                    ("Division Facts", "Derive division facts for 2, 5, 10 times tables", 20, "div_facts"),
                    ("Doubles to 15", "Derive doubles of numbers to 15", 21, "doubles_15"),
                    ("Doubles of 5s", "Doubles of multiples of 5 to 50", 22, "doubles_5s"),
                    ("Halves of 10s", "Halves of multiples of 10 to 100", 23, "halves_10s"),
                    
                    # Strategies and Checking
                    ("Mental Mult/Div", "Use variety of methods for multiplication/division", 24, "mental_mult_div"),
                    ("Checking Strategies", "Use appropriate checking strategies", 25, "checking"),
                ]
            },
            
            "Money, Measures, Shape and Space": {
                "description": "Money, measurement, time, 2D shapes, position and movement",
                "color": "#45B7D1",
                "subtopics": [
                    # Money
                    ("Coin Recognition", "Recognise all coins and use £.p notation", 1, "coins"),
                    ("Money Calculations", "Find totals, give change, work out payment", 2, "money_calc"),
                    
                    # Measures
                    ("Length Vocabulary", "Use vocabulary related to length", 3, "length_vocab"),
                    ("Length Measurement", "Estimate, measure, compare lengths in m, cm", 4, "length_measure"),
                    ("Scale Reading", "Read simple scales to nearest labelled division", 5, "scale_reading"),
                    ("Ruler Skills", "Use ruler to draw and measure to nearest cm", 6, "ruler_skills"),
                    
                    # Time
                    ("Time Vocabulary", "Use and read vocabulary related to time", 7, "time_vocab"),
                    ("Time Units", "Use time units and know relationships", 8, "time_units"),
                    ("Clock Reading", "Read analogue and digital clocks", 9, "clock_reading"),
                    ("Time Notation", "Understand time notation like 7:30", 10, "time_notation"),
                    
                    # Shapes
                    ("2D Shape Description", "Describe features of familiar 2D shapes", 11, "2d_shapes"),
                    ("Shape Sorting", "Sort shapes by features like sides and corners", 12, "shape_sorting"),
                    ("Line Symmetry", "Recognise line symmetry", 13, "symmetry"),
                    
                    # Position and Movement
                    ("Position Vocabulary", "Use mathematical vocabulary for position/direction", 14, "position_vocab"),
                    ("Turns and Angles", "Recognise whole, half, quarter turns", 15, "turns"),
                    ("Right Angles", "Know right angle as quarter turn, recognise in shapes", 16, "right_angles"),
                    ("Route Instructions", "Give instructions for moving along routes", 17, "routes"),
                ]
            },
            
            "Problem Solving": {
                "description": "Applied mathematics, reasoning, and mathematical thinking",
                "color": "#96CEB4",
                "subtopics": [
                    ("Money Problems", "Solve word problems involving money using operations", 1, "money_problems"),
                    ("Measure Problems", "Solve word problems involving measures", 2, "measure_problems"),
                    ("Operation Selection", "Choose appropriate operations for problems", 3, "operation_choice"),
                    ("Calculation Strategies", "Choose efficient calculation strategies", 4, "calc_strategies"),
                    ("Pattern Recognition", "Solve puzzles and recognise patterns", 5, "patterns"),
                    ("Mathematical Reasoning", "Explain how problems were solved", 6, "reasoning"),
                ]
            }
        }
        
        # Add all main topics and subtopics
        for main_topic_name, topic_data in curriculum_areas.items():
            # Add main topic
            topic_id = self.db.add_main_topic(
                main_topic_name, 
                topic_data["description"], 
                "Year 2-3", 
                topic_data["color"]
            )
            
            if topic_id:
                # Add all subtopics for this main topic
                for subtopic_name, description, order, code in topic_data["subtopics"]:
                    self.db.add_subtopic(
                        topic_id, 
                        subtopic_name, 
                        description, 
                        order
                    )
        
        print("✅ 7+ Maths Curriculum setup complete!")
        print(f"📊 Added {len(curriculum_areas)} main topics with detailed subtopics")
    
    def add_question_bank_support(self):
        """Add tables to support question banks and worksheet generation"""
        print("🔄 Adding question bank support...")
        
        # Question bank table
        question_bank_table = """
        CREATE TABLE IF NOT EXISTS question_bank (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subtopic_id INTEGER,
            question_text TEXT NOT NULL,
            question_type TEXT, -- 'multiple_choice', 'short_answer', 'calculation', etc.
            difficulty_level TEXT, -- 'easy', 'medium', 'hard'
            answer TEXT,
            explanation TEXT,
            question_code TEXT, -- for linking to external question systems
            created_date TEXT DEFAULT CURRENT_TIMESTAMP,
            active BOOLEAN DEFAULT 1,
            FOREIGN KEY (subtopic_id) REFERENCES subtopics(id)
        );
        """
        
        # Worksheet generation tracking
        worksheets_table = """
        CREATE TABLE IF NOT EXISTS worksheets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            tutor_id INTEGER,
            title TEXT NOT NULL,
            subtopics_covered TEXT, -- JSON list of subtopic IDs
            difficulty_focus TEXT, -- 'easy', 'medium', 'hard', 'mixed'
            questions_included TEXT, -- JSON list of question IDs
            generated_date TEXT DEFAULT CURRENT_TIMESTAMP,
            completed_date TEXT,
            score INTEGER, -- percentage if completed
            notes TEXT,
            FOREIGN KEY (student_id) REFERENCES students(id),
            FOREIGN KEY (tutor_id) REFERENCES tutors(id)
        );
        """
        
        # Execute table creation
        self.db.cursor.execute(question_bank_table)
        self.db.cursor.execute(worksheets_table)
        self.db.connection.commit()
        
        print("✅ Question bank tables added!")
    
    def add_sample_questions(self):
        """Add some sample questions to demonstrate the structure"""
        print("🔄 Adding sample questions...")
        
        # Find some subtopic IDs
        self.db.cursor.execute("""
            SELECT s.id, s.subtopic_name, mt.topic_name 
            FROM subtopics s 
            JOIN main_topics mt ON s.main_topic_id = mt.id 
            LIMIT 5
        """)
        subtopics = self.db.cursor.fetchall()
        
        sample_questions = [
            {
                "question_text": "Count these objects: 🍎🍎🍎🍎🍎🍎🍎. How many apples are there?",
                "type": "short_answer",
                "difficulty": "easy",
                "answer": "7",
                "explanation": "Count each apple: 1, 2, 3, 4, 5, 6, 7"
            },
            {
                "question_text": "What is 15 + 7?",
                "type": "calculation",
                "difficulty": "medium",
                "answer": "22",
                "explanation": "15 + 7 = 22. You can think of it as 15 + 5 + 2 = 20 + 2 = 22"
            },
            {
                "question_text": "Round 47 to the nearest 10.",
                "type": "calculation",
                "difficulty": "medium",
                "answer": "50",
                "explanation": "47 is closer to 50 than to 40, so we round up to 50"
            }
        ]
        
        # Add sample questions to first few subtopics
        for i, (subtopic_id, subtopic_name, topic_name) in enumerate(subtopics[:3]):
            if i < len(sample_questions):
                question = sample_questions[i]
                query = """
                INSERT INTO question_bank 
                (subtopic_id, question_text, question_type, difficulty_level, answer, explanation)
                VALUES (?, ?, ?, ?, ?, ?)
                """
                self.db.cursor.execute(query, (
                    subtopic_id,
                    question["question_text"],
                    question["type"],
                    question["difficulty"],
                    question["answer"],
                    question["explanation"]
                ))
        
        self.db.connection.commit()
        print("✅ Sample questions added!")
    
    def show_curriculum_overview(self):
        """Display overview of current curriculum structure"""
        print("\n📚 CURRICULUM OVERVIEW")
        print("=" * 50)
        
        query = """
        SELECT mt.topic_name, mt.description, COUNT(s.id) as subtopic_count
        FROM main_topics mt
        LEFT JOIN subtopics s ON mt.id = s.main_topic_id
        GROUP BY mt.id, mt.topic_name
        ORDER BY mt.topic_name
        """
        
        self.db.cursor.execute(query)
        topics = self.db.cursor.fetchall()
        
        total_subtopics = 0
        for topic_name, description, subtopic_count in topics:
            print(f"\n📖 {topic_name}")
            print(f"   {description}")
            print(f"   📊 {subtopic_count} subtopics")
            total_subtopics += subtopic_count
        
        print(f"\n📈 TOTAL: {len(topics)} main topics, {total_subtopics} subtopics")
    
    def list_subtopics_by_topic(self, topic_name):
        """List all subtopics for a specific main topic"""
        query = """
        SELECT s.subtopic_name, s.description, s.difficulty_order
        FROM subtopics s
        JOIN main_topics mt ON s.main_topic_id = mt.id
        WHERE mt.topic_name = ?
        ORDER BY s.difficulty_order
        """
        
        self.db.cursor.execute(query, (topic_name,))
        subtopics = self.db.cursor.fetchall()
        
        print(f"\n📖 SUBTOPICS FOR: {topic_name}")
        print("-" * 40)
        
        for subtopic_name, description, order in subtopics:
            print(f"{order:2d}. {subtopic_name}")
            if description:
                print(f"     {description}")
    
    def clear_curriculum(self):
        """Clear existing curriculum (use with caution!)"""
        confirm = input("⚠️  This will delete ALL curriculum data. Type 'DELETE' to confirm: ")
        if confirm == "DELETE":
            self.db.cursor.execute("DELETE FROM subtopics")
            self.db.cursor.execute("DELETE FROM main_topics")
            self.db.connection.commit()
            print("🗑️  Curriculum cleared!")
        else:
            print("❌ Operation cancelled.")
    
    def close(self):
        """Close database connection"""
        self.db.close()


# Demo script
if __name__ == "__main__":
    print("🎯 Curriculum Manager for 7+ Maths")
    print("=" * 40)
    
    manager = CurriculumManager()
    
    # Setup complete 7+ curriculum
    manager.setup_7plus_curriculum()
    
    # Add question bank support
    manager.add_question_bank_support()
    
    # Add some sample questions
    manager.add_sample_questions()
    
    # Show overview
    manager.show_curriculum_overview()
    
    # Show example subtopics
    manager.list_subtopics_by_topic("Calculations")
    
    manager.close()
    print("\n🎉 7+ Curriculum setup complete!")