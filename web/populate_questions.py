#!/usr/bin/env python3
"""
Populate question bank with sample questions for common subtopics
Updated to handle answer field
"""

import sqlite3
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def add_questions_for_subtopic(cursor, subtopic_name, questions, tutor_id=1):
    """Add questions for a specific subtopic"""
    
    # Find the subtopic ID
    cursor.execute("SELECT id FROM subtopics WHERE subtopic_name = ?", (subtopic_name,))
    result = cursor.fetchone()
    
    if not result:
        print(f"⚠️  Subtopic '{subtopic_name}' not found, skipping...")
        return 0
    
    subtopic_id = result[0]
    count = 0
    
    for question_data in questions:
        # Handle both old format (4 items) and new format (5 items with answer)
        if len(question_data) == 4:
            question_text, difficulty, time_est, space = question_data
            answer = None
        else:
            question_text, difficulty, time_est, space, answer = question_data
        
        try:
            cursor.execute('''
                INSERT INTO questions 
                (subtopic_id, question_text, answer, difficulty_level, time_estimate_minutes, 
                 space_required, created_by_tutor_id, active)
                VALUES (?, ?, ?, ?, ?, ?, ?, 1)
            ''', (subtopic_id, question_text, answer, difficulty, time_est, space, tutor_id))
            count += 1
        except sqlite3.IntegrityError:
            print(f"⚠️  Question already exists: {question_text[:50]}...")
    
    print(f"✅ Added {count} questions for {subtopic_name}")
    return count

def populate_all_questions():
    """Populate questions for all common subtopics"""
    
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'tutor_ai.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("🚀 Populating question bank...")
    print("=" * 50)
    
    # ADDITION QUESTIONS (now with answers)
    addition_questions = [
        # Easy (1-2 min, minimal space)
        ("What is 5 + 3?", 1, 1, "none", "8"),
        ("Calculate 12 + 8", 1, 1, "none", "20"),
        ("Find the sum of 15 and 7", 1, 1, "none", "22"),
        ("What is 24 + 16?", 1, 2, "small", "40"),
        ("Add 33 and 28", 1, 2, "small", "61"),
        ("9 + 6 = ?", 1, 1, "none", "15"),
        ("17 + 14 = ?", 1, 1, "none", "31"),
        ("Find: 45 + 32", 1, 2, "small", "77"),
        
        # Medium (3-5 min, some space)
        ("Tom has 47 marbles and his friend gives him 38 more. How many marbles does Tom have now?", 2, 3, "medium", "85 marbles"),
        ("A shop sold 126 apples in the morning and 89 in the afternoon. How many apples were sold in total?", 2, 4, "medium", "215 apples"),
        ("Calculate 234 + 178 + 95", 2, 4, "medium", "507"),
        ("There are 156 students in Year 3 and 189 students in Year 4. How many students are there altogether?", 2, 4, "medium", "345 students"),
        ("Add: 567 + 234 + 123", 2, 5, "medium", "924"),
        
        # Hard (7-10 min, lots of space)
        ("A school has 3 year groups. Year 3 has 145 students, Year 4 has 167 students, and Year 5 has 139 students. If 28 new students join Year 3 and 15 join Year 4, how many students are there in total?", 3, 8, "large", "494 students (145+28+167+15+139)"),
        ("Sarah is saving money. She has £2.45 in her piggy bank. Her grandmother gives her £5.80 and she finds £1.25 in her pocket. How much money does Sarah have altogether?", 3, 7, "large", "£9.50"),
        ("A charity collected £234.50 on Monday, £189.75 on Tuesday, and £345.25 on Wednesday. What was the total amount collected?", 3, 8, "large", "£769.50"),
    ]
    
    # SUBTRACTION QUESTIONS
    subtraction_questions = [
        # Easy
        ("What is 8 - 3?", 1, 1, "none", "5"),
        ("Calculate 15 - 7", 1, 1, "none", "8"),
        ("20 - 12 = ?", 1, 1, "none", "8"),
        ("Find: 45 - 23", 1, 2, "small", "22"),
        ("Subtract 18 from 50", 1, 2, "small", "32"),
        
        # Medium
        ("A baker made 85 cupcakes and sold 47. How many cupcakes are left?", 2, 3, "medium", "38 cupcakes"),
        ("There were 234 books in the library. 78 books were borrowed. How many books remain?", 2, 4, "medium", "156 books"),
        ("Calculate 500 - 267", 2, 3, "medium", "233"),
        ("A school had 456 students. 89 students left for a field trip. How many students stayed at school?", 2, 4, "medium", "367 students"),
        
        # Hard
        ("A shop had £543.75 in the till. After giving £287.90 in change throughout the day, how much is left?", 3, 7, "large", "£255.85"),
        ("There were 1,234 tickets for a concert. On Monday 456 were sold, on Tuesday 389 were sold. How many tickets are still available?", 3, 8, "large", "389 tickets"),
    ]
    
    # MULTIPLICATION QUESTIONS
    multiplication_questions = [
        # Easy
        ("What is 3 × 4?", 1, 1, "none", "12"),
        ("Calculate 5 × 6", 1, 1, "none", "30"),
        ("7 × 8 = ?", 1, 1, "none", "56"),
        ("Find: 9 × 6", 1, 1, "none", "54"),
        ("Double 15", 1, 1, "none", "30"),
        
        # Medium
        ("A box contains 12 chocolates. How many chocolates are in 8 boxes?", 2, 3, "medium", "96 chocolates"),
        ("Each student needs 4 pencils. How many pencils are needed for 27 students?", 2, 4, "medium", "108 pencils"),
        ("Calculate 23 × 15", 2, 4, "medium", "345"),
        ("There are 45 rows of seats with 12 seats in each row. How many seats in total?", 2, 4, "medium", "540 seats"),
        
        # Hard
        ("A school orders 24 boxes of books. Each box contains 36 books. Each book costs £4.50. What is the total cost?", 3, 9, "large", "£3,888 (24 × 36 × 4.50)"),
        ("A rectangular garden is 18 metres long and 14 metres wide. What is its area? If fencing costs £12 per metre, how much will it cost to fence the entire garden?", 3, 10, "large", "Area: 252 m², Fencing cost: £768 (perimeter 64m × £12)"),
    ]
    
    # DIVISION QUESTIONS
    division_questions = [
        # Easy
        ("What is 12 ÷ 3?", 1, 1, "none", "4"),
        ("Calculate 20 ÷ 4", 1, 1, "none", "5"),
        ("15 ÷ 5 = ?", 1, 1, "none", "3"),
        ("Share 18 sweets equally among 6 children", 1, 2, "small", "3 sweets each"),
        
        # Medium
        ("84 students need to be put into groups of 7. How many groups will there be?", 2, 3, "medium", "12 groups"),
        ("A baker has 156 cookies to pack into boxes of 12. How many full boxes can be made?", 2, 4, "medium", "13 boxes"),
        ("Divide 348 by 6", 2, 4, "medium", "58"),
        
        # Hard
        ("A school has 458 students going on a trip. Each bus can hold 32 students. How many buses are needed? How many empty seats will there be?", 3, 8, "large", "15 buses needed, 22 empty seats"),
        ("£247.50 needs to be shared equally among 6 people. How much does each person get?", 3, 7, "large", "£41.25 each"),
    ]
    
    # FRACTIONS - RECOGNITION QUESTIONS
    fractions_recognition_questions = [
        # Easy
        ("What fraction of this shape is shaded? [Draw a square with half shaded]", 1, 1, "small", "1/2"),
        ("Write one half as a fraction", 1, 1, "none", "1/2"),
        ("Circle the fraction that shows one quarter: 1/2, 1/3, 1/4, 1/5", 1, 1, "none", "1/4"),
        
        # Medium
        ("A pizza is cut into 8 equal slices. Tom eats 3 slices. What fraction of the pizza did Tom eat?", 2, 3, "medium", "3/8"),
        ("Which is larger: 3/4 or 2/3? Show your working", 2, 4, "medium", "3/4 is larger"),
        
        # Hard
        ("Arrange these fractions in order from smallest to largest: 2/3, 3/5, 4/7, 1/2", 3, 8, "large", "1/2, 4/7, 3/5, 2/3"),
    ]
    
    # Continue with other question sets...
    # (I'll keep the format but shorten for space)
    
    # Now add all questions
    total_added = 0
    
    # Update the function calls to match the new name
    total_added += add_questions_for_subtopic(cursor, "Addition", addition_questions)
    total_added += add_questions_for_subtopic(cursor, "Subtraction", subtraction_questions)
    total_added += add_questions_for_subtopic(cursor, "Multiplication", multiplication_questions)
    total_added += add_questions_for_subtopic(cursor, "Division", division_questions)
    total_added += add_questions_for_subtopic(cursor, "Fractions - Recognition", fractions_recognition_questions)
    
    conn.commit()
    
    # Show statistics
    print("\n" + "=" * 50)
    print("📊 QUESTION BANK STATISTICS")
    print("=" * 50)
    
    cursor.execute("""
        SELECT s.subtopic_name, 
               COUNT(q.id) as total,
               SUM(CASE WHEN q.difficulty_level = 1 THEN 1 ELSE 0 END) as easy,
               SUM(CASE WHEN q.difficulty_level = 2 THEN 1 ELSE 0 END) as medium,
               SUM(CASE WHEN q.difficulty_level = 3 THEN 1 ELSE 0 END) as hard
        FROM subtopics s
        LEFT JOIN questions q ON s.id = q.subtopic_id AND q.active = 1
        GROUP BY s.id, s.subtopic_name
        HAVING total > 0
        ORDER BY s.subtopic_name
    """)
    
    for row in cursor.fetchall():
        print(f"\n{row[0]}:")
        print(f"  Total: {row[1]} questions")
        print(f"  Easy: {row[2]}, Medium: {row[3]}, Hard: {row[4]}")
    
    print(f"\n✅ Total questions added: {total_added}")
    conn.close()

if __name__ == "__main__":
    populate_all_questions()