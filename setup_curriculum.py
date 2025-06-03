# setup_curriculum.py - Simple script to set up 7+ curriculum
from database import TutorAIDatabase

def setup_7plus_curriculum():
    """Set up complete 7+ maths curriculum structure"""
    print("🔄 Setting up 7+ Maths Curriculum...")
    
    db = TutorAIDatabase("data/tutor_ai.db")
    
    # Add question bank support first
    print("🔄 Adding question bank support...")
    
    # Question bank table
    question_bank_table = """
    CREATE TABLE IF NOT EXISTS question_bank (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subtopic_id INTEGER,
        question_text TEXT NOT NULL,
        question_type TEXT,
        difficulty_level TEXT,
        answer TEXT,
        explanation TEXT,
        question_code TEXT,
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
        subtopics_covered TEXT,
        difficulty_focus TEXT,
        questions_included TEXT,
        generated_date TEXT DEFAULT CURRENT_TIMESTAMP,
        completed_date TEXT,
        score INTEGER,
        notes TEXT,
        FOREIGN KEY (student_id) REFERENCES students(id),
        FOREIGN KEY (tutor_id) REFERENCES tutors(id)
    );
    """
    
    # Execute table creation
    db.cursor.execute(question_bank_table)
    db.cursor.execute(worksheets_table)
    db.connection.commit()
    print("✅ Question bank tables added!")
    
    # Clear existing curriculum for fresh start
    print("🔄 Setting up fresh curriculum...")
    db.cursor.execute("DELETE FROM subtopic_progress")
    db.cursor.execute("DELETE FROM subtopics")
    db.cursor.execute("DELETE FROM main_topics")
    db.connection.commit()
    
    # Main curriculum areas based on 7+ syllabus
    curriculum_areas = [
        ("Number and Number System", "Counting, place value, ordering, fractions, estimation", "#FF6B6B", [
            # Counting and Properties
            ("Counting to 100", "Count reliably up to 100 objects by grouping", 1),
            ("Number Sequences", "Count in steps of 1,2,3,4,5,10 from any two-digit number", 2),
            ("Counting in Hundreds", "Count in hundreds from and back to zero", 3),
            ("Odd and Even Numbers", "Recognise odd and even numbers", 4),
            ("Multiples Recognition", "Recognise two-digit multiples of 2, 5 or 10", 5),
            
            # Place Value and Ordering
            ("Reading Three-Digit Numbers", "Read and write three-digit numbers in figures and words", 6),
            ("Two-Digit Place Value", "Know what each digit represents including 0 as placeholder", 7),
            ("Comparing Numbers", "Use vocabulary of comparing and ordering numbers", 8),
            ("Equality Symbol", "Use the = sign to represent equality", 9),
            ("Number Comparison", "Compare two-digit numbers and find numbers between", 10),
            ("Number Lines", "Order numbers on 100 square and position on number line", 11),
            
            # Estimation and Rounding
            ("Estimation Vocabulary", "Use vocabulary of estimation and approximation", 12),
            ("Rounding to 10", "Round any two-digit number to the nearest 10", 13),
            
            # Fractions
            ("Halves and Quarters", "Recognise and find 1/2 and 1/4 of shapes and numbers", 14),
            ("Fraction Equivalence", "Understand 2 halves = 1 whole, 4 quarters = 1 whole", 15),
        ]),
        
        ("Calculations", "Addition, subtraction, multiplication, division strategies", "#4ECDC4", [
            # Addition and Subtraction Understanding
            ("Addition Operations", "Understand addition operations and vocabulary", 1),
            ("Mathematical Symbols", "Use +, -, = signs and unknown number symbols", 2),
            ("Inverse Operations", "Understand subtraction as inverse of addition", 3),
            ("Addition Properties", "Recognise addition can be done in any order", 4),
            ("Three Single Digits", "Add three single-digit numbers mentally (to 27)", 5),
            ("Two-Digit Addition", "Add two two-digit numbers (totals to 100)", 6),
            
            # Number Facts
            ("Addition Facts to 20", "Know all addition facts to 20 by heart", 7),
            ("Pairs to 100", "Know pairs of multiples of 10 totalling 100", 8),
            ("TU + U to 50", "Derive TU + U to 50 and corresponding subtractions", 9),
            
            # Mental Strategies
            ("Mental Add/Subtract", "Use variety of methods for addition/subtraction", 10),
            ("Related Facts", "State subtraction corresponding to addition and vice versa", 11),
            
            # Multiplication and Division Understanding
            ("Multiplication Concept", "Understand multiplication as repeated addition/arrays", 12),
            ("Division Concept", "Understand division as grouping or sharing", 13),
            ("Multiplication Symbols", "Use x, ÷, = signs in calculations", 14),
            ("Halving and Doubling", "Know halving as inverse of doubling", 15),
            
            # Times Tables
            ("2 Times Table", "Know 2 times table by heart", 16),
            ("5 Times Table", "Know 5 times table by heart", 17),
            ("10 Times Table", "Know 10 times table by heart", 18),
            ("Doubles to 10", "Know doubles of all numbers to 10", 19),
            ("Division Facts", "Derive division facts for 2, 5, 10 times tables", 20),
            ("Doubles to 15", "Derive doubles of numbers to 15", 21),
            ("Doubles of 5s", "Doubles of multiples of 5 to 50", 22),
            ("Halves of 10s", "Halves of multiples of 10 to 100", 23),
            
            # Strategies and Checking
            ("Mental Mult/Div", "Use variety of methods for multiplication/division", 24),
            ("Checking Strategies", "Use appropriate checking strategies", 25),
        ]),
        
        ("Money, Measures, Shape and Space", "Money, measurement, time, 2D shapes, position and movement", "#45B7D1", [
            # Money
            ("Coin Recognition", "Recognise all coins and use £.p notation", 1),
            ("Money Calculations", "Find totals, give change, work out payment", 2),
            
            # Measures
            ("Length Vocabulary", "Use vocabulary related to length", 3),
            ("Length Measurement", "Estimate, measure, compare lengths in m, cm", 4),
            ("Scale Reading", "Read simple scales to nearest labelled division", 5),
            ("Ruler Skills", "Use ruler to draw and measure to nearest cm", 6),
            
            # Time
            ("Time Vocabulary", "Use and read vocabulary related to time", 7),
            ("Time Units", "Use time units and know relationships", 8),
            ("Clock Reading", "Read analogue and digital clocks", 9),
            ("Time Notation", "Understand time notation like 7:30", 10),
            
            # Shapes
            ("2D Shape Description", "Describe features of familiar 2D shapes", 11),
            ("Shape Sorting", "Sort shapes by features like sides and corners", 12),
            ("Line Symmetry", "Recognise line symmetry", 13),
            
            # Position and Movement
            ("Position Vocabulary", "Use mathematical vocabulary for position/direction", 14),
            ("Turns and Angles", "Recognise whole, half, quarter turns", 15),
            ("Right Angles", "Know right angle as quarter turn, recognise in shapes", 16),
            ("Route Instructions", "Give instructions for moving along routes", 17),
        ]),
        
        ("Problem Solving", "Applied mathematics, reasoning, and mathematical thinking", "#96CEB4", [
            ("Money Problems", "Solve word problems involving money using operations", 1),
            ("Measure Problems", "Solve word problems involving measures", 2),
            ("Operation Selection", "Choose appropriate operations for problems", 3),
            ("Calculation Strategies", "Choose efficient calculation strategies", 4),
            ("Pattern Recognition", "Solve puzzles and recognise patterns", 5),
            ("Mathematical Reasoning", "Explain how problems were solved", 6),
        ])
    ]
    
    # Add all main topics and subtopics
    total_subtopics = 0
    for main_topic_name, description, color, subtopics in curriculum_areas:
        # Add main topic
        topic_id = db.add_main_topic(main_topic_name, description, "Year 2-3", color)
        
        if topic_id:
            # Add all subtopics for this main topic
            for subtopic_name, sub_description, order in subtopics:
                db.add_subtopic(topic_id, subtopic_name, sub_description, order)
                total_subtopics += 1
    
    db.close()
    
    print("✅ 7+ Maths Curriculum setup complete!")
    print(f"📊 Added {len(curriculum_areas)} main topics with {total_subtopics} subtopics")
    print("🎉 Ready for question bank import and worksheet generation!")

if __name__ == "__main__":
    setup_7plus_curriculum()