"""
Sample questions to populate the question bank
Run this after setting up the worksheet system
"""

def add_sample_questions(db_connection, subtopic_id, tutor_id=1):
    """Add sample questions for a subtopic"""
    
    # Example for Addition subtopic
    addition_questions = [
        # Easy (1-2 min, no working space)
        ("What is 5 + 3?", 1, 1, "none"),
        ("Calculate 12 + 8", 1, 1, "none"),
        ("Find the sum of 15 and 7", 1, 1, "none"),
        ("What is 24 + 16?", 1, 2, "small"),
        ("Add 33 and 28", 1, 2, "small"),
        
        # Medium (3-5 min, some space)
        ("Tom has 47 marbles and his friend gives him 38 more. How many marbles does Tom have now?", 2, 3, "medium"),
        ("A shop sold 126 apples in the morning and 89 in the afternoon. How many apples were sold in total?", 2, 4, "medium"),
        ("Calculate 234 + 178 + 95", 2, 4, "medium"),
        
        # Hard (7-10 min, lots of space)
        ("A school has 3 year groups. Year 3 has 145 students, Year 4 has 167 students, and Year 5 has 139 students. If 28 new students join Year 3 and 15 join Year 4, how many students are there in total?", 3, 8, "large"),
        ("Sarah is saving money. She has £2.45 in her piggy bank. Her grandmother gives her £5.80 and she finds £1.25 in her pocket. How much money does Sarah have altogether?", 3, 7, "large"),
    ]
    
    cursor = db_connection.cursor()
    for question_text, difficulty, time_est, space in addition_questions:
        cursor.execute('''
            INSERT INTO questions 
            (subtopic_id, question_text, difficulty_level, time_estimate_minutes, 
             space_required, created_by_tutor_id)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (subtopic_id, question_text, difficulty, time_est, space, tutor_id))
    
    db_connection.commit()
    print(f"✅ Added {len(addition_questions)} sample questions")