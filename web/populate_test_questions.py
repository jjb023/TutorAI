#!/usr/bin/env python3
"""
Populate question bank with test questions for worksheet generation testing
This creates a variety of questions across all subtopics with different difficulties
"""

import sqlite3
import os
import sys
import random

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def populate_test_questions():
    """Populate all subtopics with test questions"""
    
    # Get the database path
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'tutor_ai.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("🚀 Populating test questions for all subtopics...")
    print("=" * 50)
    
    # Get all subtopics
    cursor.execute("""
        SELECT s.id, s.subtopic_name, mt.topic_name 
        FROM subtopics s
        JOIN main_topics mt ON s.main_topic_id = mt.id
        ORDER BY mt.topic_name, s.difficulty_order
    """)
    
    subtopics = cursor.fetchall()
    
    if not subtopics:
        print("❌ No subtopics found in database!")
        print("   Please run the main database setup first.")
        return
    
    print(f"📚 Found {len(subtopics)} subtopics to populate")
    print()
    
    # Question templates by difficulty
    question_templates = {
        1: [  # Easy questions (1-2 min)
            "Calculate the value of X in this simple problem",
            "What is the answer to this basic question",
            "Find the result of this simple calculation",
            "Complete this straightforward exercise",
            "Solve this elementary problem"
        ],
        2: [  # Medium questions (3-5 min)
            "Work through this multi-step problem and show your working",
            "Apply the concept to solve this moderate challenge",
            "Use the method learned to find the solution",
            "Complete this problem requiring careful calculation",
            "Solve this problem using the appropriate technique"
        ],
        3: [  # Hard questions (7-10 min)
            "Analyze this complex scenario and provide a detailed solution",
            "Solve this challenging multi-part problem showing all steps",
            "Apply advanced concepts to resolve this difficult question",
            "Work through this comprehensive problem requiring multiple techniques",
            "Complete this extended problem demonstrating full understanding"
        ]
    }
    
    space_requirements = {
        1: ['none', 'small'],      # Easy questions need less space
        2: ['small', 'medium'],     # Medium questions need moderate space
        3: ['medium', 'large']      # Hard questions need more space
    }
    
    time_estimates = {
        1: [1, 2],      # Easy: 1-2 minutes
        2: [3, 4, 5],   # Medium: 3-5 minutes
        3: [7, 8, 9, 10] # Hard: 7-10 minutes
    }
    
    total_questions_added = 0
    questions_per_subtopic = 50  # 50 questions per subtopic for good variety
    
    # Add questions for each subtopic
    for subtopic_id, subtopic_name, topic_name in subtopics:
        print(f"\n📝 Adding questions for: {topic_name} → {subtopic_name}")
        
        questions_added = 0
        
        # Distribute questions across difficulties
        # 40% easy, 40% medium, 20% hard
        difficulty_distribution = {
            1: int(questions_per_subtopic * 0.4),  # 20 easy
            2: int(questions_per_subtopic * 0.4),  # 20 medium
            3: questions_per_subtopic - (int(questions_per_subtopic * 0.4) * 2)  # 10 hard
        }
        
        for difficulty, count in difficulty_distribution.items():
            for i in range(count):
                # Create question text
                template = random.choice(question_templates[difficulty])
                question_number = questions_added + 1
                question_text = f"{template} - {subtopic_name} Example {question_number}"
                
                # Generate answer
                answer = f"Answer to {subtopic_name} Example {question_number}: Result = {random.randint(1, 100)}"
                
                # Random time and space
                time_est = random.choice(time_estimates[difficulty])
                space = random.choice(space_requirements[difficulty])
                
                # Determine question type
                question_types = ['calculation', 'word_problem', 'reasoning', 'application']
                question_type = random.choice(question_types)
                
                try:
                    cursor.execute('''
                        INSERT INTO questions 
                        (subtopic_id, question_text, answer, difficulty_level, 
                         time_estimate_minutes, space_required, question_type, 
                         created_by_tutor_id, active)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
                    ''', (subtopic_id, question_text, answer, difficulty, 
                          time_est, space, question_type, 1))  # tutor_id = 1 (admin)
                    
                    questions_added += 1
                except sqlite3.IntegrityError:
                    print(f"⚠️  Duplicate question skipped")
        
        total_questions_added += questions_added
        print(f"   ✅ Added {questions_added} questions")
    
    # Commit all changes
    conn.commit()
    
    # Show final statistics
    print("\n" + "=" * 50)
    print("📊 QUESTION BANK STATISTICS")
    print("=" * 50)
    
    cursor.execute("""
        SELECT 
            mt.topic_name,
            COUNT(DISTINCT s.id) as subtopic_count,
            COUNT(q.id) as total_questions,
            SUM(CASE WHEN q.difficulty_level = 1 THEN 1 ELSE 0 END) as easy,
            SUM(CASE WHEN q.difficulty_level = 2 THEN 1 ELSE 0 END) as medium,
            SUM(CASE WHEN q.difficulty_level = 3 THEN 1 ELSE 0 END) as hard
        FROM main_topics mt
        LEFT JOIN subtopics s ON mt.id = s.main_topic_id
        LEFT JOIN questions q ON s.id = q.subtopic_id AND q.active = 1
        GROUP BY mt.id, mt.topic_name
        ORDER BY mt.topic_name
    """)
    
    for row in cursor.fetchall():
        if row[2] > 0:  # Only show topics with questions
            print(f"\n{row[0]}:")
            print(f"  Subtopics: {row[1]}")
            print(f"  Total Questions: {row[2]}")
            print(f"  Distribution: Easy={row[3]}, Medium={row[4]}, Hard={row[5]}")
    
    # Overall total
    cursor.execute("SELECT COUNT(*) FROM questions WHERE active = 1")
    grand_total = cursor.fetchone()[0]
    
    print(f"\n🎯 GRAND TOTAL: {grand_total} questions in the bank")
    print(f"✅ Added {total_questions_added} new test questions")
    
    conn.close()
    
    print("\n💡 Next steps:")
    print("1. Run your Flask app")
    print("2. Login as admin")
    print("3. Go to any student's page")
    print("4. Click 'Generate Worksheet'")
    print("5. Select a subtopic and test the worksheet generation!")

if __name__ == "__main__":
    populate_test_questions()