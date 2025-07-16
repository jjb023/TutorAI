#!/usr/bin/env python3
"""
Populate question bank with sample questions for common subtopics
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
    
    for question_text, difficulty, time_est, space in questions:
        try:
            cursor.execute('''
                INSERT INTO questions 
                (subtopic_id, question_text, difficulty_level, time_estimate_minutes, 
                 space_required, created_by_tutor_id, active)
                VALUES (?, ?, ?, ?, ?, ?, 1)
            ''', (subtopic_id, question_text, difficulty, time_est, space, tutor_id))
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
    
    # ADDITION QUESTIONS
    addition_questions = [
        # Easy (1-2 min, minimal space)
        ("What is 5 + 3?", 1, 1, "none"),
        ("Calculate 12 + 8", 1, 1, "none"),
        ("Find the sum of 15 and 7", 1, 1, "none"),
        ("What is 24 + 16?", 1, 2, "small"),
        ("Add 33 and 28", 1, 2, "small"),
        ("9 + 6 = ?", 1, 1, "none"),
        ("17 + 14 = ?", 1, 1, "none"),
        ("Find: 45 + 32", 1, 2, "small"),
        
        # Medium (3-5 min, some space)
        ("Tom has 47 marbles and his friend gives him 38 more. How many marbles does Tom have now?", 2, 3, "medium"),
        ("A shop sold 126 apples in the morning and 89 in the afternoon. How many apples were sold in total?", 2, 4, "medium"),
        ("Calculate 234 + 178 + 95", 2, 4, "medium"),
        ("There are 156 students in Year 3 and 189 students in Year 4. How many students are there altogether?", 2, 4, "medium"),
        ("Add: 567 + 234 + 123", 2, 5, "medium"),
        
        # Hard (7-10 min, lots of space)
        ("A school has 3 year groups. Year 3 has 145 students, Year 4 has 167 students, and Year 5 has 139 students. If 28 new students join Year 3 and 15 join Year 4, how many students are there in total?", 3, 8, "large"),
        ("Sarah is saving money. She has £2.45 in her piggy bank. Her grandmother gives her £5.80 and she finds £1.25 in her pocket. How much money does Sarah have altogether?", 3, 7, "large"),
        ("A charity collected £234.50 on Monday, £189.75 on Tuesday, and £345.25 on Wednesday. What was the total amount collected?", 3, 8, "large"),
    ]
    
    # SUBTRACTION QUESTIONS
    subtraction_questions = [
        # Easy
        ("What is 8 - 3?", 1, 1, "none"),
        ("Calculate 15 - 7", 1, 1, "none"),
        ("20 - 12 = ?", 1, 1, "none"),
        ("Find: 45 - 23", 1, 2, "small"),
        ("Subtract 18 from 50", 1, 2, "small"),
        
        # Medium
        ("A baker made 85 cupcakes and sold 47. How many cupcakes are left?", 2, 3, "medium"),
        ("There were 234 books in the library. 78 books were borrowed. How many books remain?", 2, 4, "medium"),
        ("Calculate 500 - 267", 2, 3, "medium"),
        ("A school had 456 students. 89 students left for a field trip. How many students stayed at school?", 2, 4, "medium"),
        
        # Hard
        ("A shop had £543.75 in the till. After giving £287.90 in change throughout the day, how much is left?", 3, 7, "large"),
        ("There were 1,234 tickets for a concert. On Monday 456 were sold, on Tuesday 389 were sold. How many tickets are still available?", 3, 8, "large"),
    ]
    
    # MULTIPLICATION QUESTIONS
    multiplication_questions = [
        # Easy
        ("What is 3 × 4?", 1, 1, "none"),
        ("Calculate 5 × 6", 1, 1, "none"),
        ("7 × 8 = ?", 1, 1, "none"),
        ("Find: 9 × 6", 1, 1, "none"),
        ("Double 15", 1, 1, "none"),
        
        # Medium
        ("A box contains 12 chocolates. How many chocolates are in 8 boxes?", 2, 3, "medium"),
        ("Each student needs 4 pencils. How many pencils are needed for 27 students?", 2, 4, "medium"),
        ("Calculate 23 × 15", 2, 4, "medium"),
        ("There are 45 rows of seats with 12 seats in each row. How many seats in total?", 2, 4, "medium"),
        
        # Hard
        ("A school orders 24 boxes of books. Each box contains 36 books. Each book costs £4.50. What is the total cost?", 3, 9, "large"),
        ("A rectangular garden is 18 metres long and 14 metres wide. What is its area? If fencing costs £12 per metre, how much will it cost to fence the entire garden?", 3, 10, "large"),
    ]
    
    # DIVISION QUESTIONS
    division_questions = [
        # Easy
        ("What is 12 ÷ 3?", 1, 1, "none"),
        ("Calculate 20 ÷ 4", 1, 1, "none"),
        ("15 ÷ 5 = ?", 1, 1, "none"),
        ("Share 18 sweets equally among 6 children", 1, 2, "small"),
        
        # Medium
        ("84 students need to be put into groups of 7. How many groups will there be?", 2, 3, "medium"),
        ("A baker has 156 cookies to pack into boxes of 12. How many full boxes can be made?", 2, 4, "medium"),
        ("Divide 348 by 6", 2, 4, "medium"),
        
        # Hard
        ("A school has 458 students going on a trip. Each bus can hold 32 students. How many buses are needed? How many empty seats will there be?", 3, 8, "large"),
        ("£247.50 needs to be shared equally among 6 people. How much does each person get?", 3, 7, "large"),
    ]
    
    # FRACTIONS - RECOGNITION QUESTIONS
    fractions_recognition_questions = [
        # Easy
        ("What fraction of this shape is shaded? [Draw a square with half shaded]", 1, 1, "small"),
        ("Write one half as a fraction", 1, 1, "none"),
        ("Circle the fraction that shows one quarter: 1/2, 1/3, 1/4, 1/5", 1, 1, "none"),
        
        # Medium
        ("A pizza is cut into 8 equal slices. Tom eats 3 slices. What fraction of the pizza did Tom eat?", 2, 3, "medium"),
        ("Which is larger: 3/4 or 2/3? Show your working", 2, 4, "medium"),
        
        # Hard
        ("Arrange these fractions in order from smallest to largest: 2/3, 3/5, 4/7, 1/2", 3, 8, "large"),
    ]
    
    # FRACTIONS - ADDITION QUESTIONS
    fractions_addition_questions = [
        # Easy
        ("Add: 1/4 + 1/4", 1, 2, "small"),
        ("What is 2/5 + 1/5?", 1, 2, "small"),
        ("Calculate: 3/8 + 2/8", 1, 2, "small"),
        
        # Medium
        ("Sarah ate 2/6 of a cake and Tom ate 3/6. What fraction of the cake did they eat altogether?", 2, 4, "medium"),
        ("Add: 1/3 + 1/6", 2, 5, "medium"),
        
        # Hard
        ("Calculate: 2/3 + 3/4. Give your answer as a mixed number in simplest form", 3, 8, "large"),
        ("A recipe uses 3/4 cup of flour for the base and 2/3 cup for the topping. How much flour is needed in total?", 3, 9, "large"),
    ]
    
    # DECIMALS - RECOGNITION QUESTIONS
    decimals_recognition_questions = [
        # Easy
        ("Write 0.5 in words", 1, 1, "none"),
        ("What is the value of the digit 3 in 2.34?", 1, 2, "small"),
        ("Circle the largest number: 0.7, 0.5, 0.9, 0.2", 1, 1, "none"),
        
        # Medium
        ("Order these decimals from smallest to largest: 0.45, 0.5, 0.39, 0.4", 2, 4, "medium"),
        ("Round 3.67 to the nearest whole number", 2, 2, "small"),
        
        # Hard
        ("Convert 3/4 to a decimal. Show your working", 3, 6, "large"),
    ]
    
    # DECIMALS - ADDITION QUESTIONS
    decimals_addition_questions = [
        # Easy
        ("Add: 0.3 + 0.4", 1, 1, "none"),
        ("What is 1.2 + 0.5?", 1, 2, "small"),
        
        # Medium
        ("Calculate: 2.45 + 1.38", 2, 3, "medium"),
        ("A book costs £4.99 and a pen costs £1.49. What is the total cost?", 2, 4, "medium"),
        
        # Hard
        ("Add: 12.456 + 8.789 + 3.21", 3, 6, "large"),
        ("Sarah ran 2.45 km on Monday, 3.8 km on Wednesday, and 4.125 km on Friday. What was her total distance?", 3, 8, "large"),
    ]
    
    # PERCENTAGES QUESTIONS
    percentages_questions = [
        # Easy
        ("What is 50% of 20?", 1, 2, "small"),
        ("Write 25% as a fraction", 1, 1, "none"),
        ("What is 10% of 100?", 1, 1, "none"),
        
        # Medium
        ("A shirt costs £40. It has a 20% discount. What is the sale price?", 2, 4, "medium"),
        ("In a class of 30 students, 60% are girls. How many girls are there?", 2, 4, "medium"),
        
        # Hard
        ("A phone originally cost £250. It increased in price by 15%, then had a 10% discount. What is the final price?", 3, 8, "large"),
        ("In a survey of 240 people, 35% liked chocolate, 40% liked vanilla, and the rest liked strawberry. How many people liked each flavour?", 3, 10, "large"),
    ]
    
    # Now add all questions
    total_added = 0
    
    total_added += add_questions_for_subtopic(cursor, "Addition Operations", addition_questions)
    total_added += add_questions_for_subtopic(cursor, "Subtraction", subtraction_questions)
    total_added += add_questions_for_subtopic(cursor, "Multiplication", multiplication_questions)
    total_added += add_questions_for_subtopic(cursor, "Division", division_questions)
    total_added += add_questions_for_subtopic(cursor, "Fractions - Recognition", fractions_recognition_questions)
    total_added += add_questions_for_subtopic(cursor, "Fractions - Addition", fractions_addition_questions)
    total_added += add_questions_for_subtopic(cursor, "Decimals - Recognition", decimals_recognition_questions)
    total_added += add_questions_for_subtopic(cursor, "Decimals - Addition", decimals_addition_questions)
    total_added += add_questions_for_subtopic(cursor, "Percentages", percentages_questions)
    
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