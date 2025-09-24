#!/usr/bin/env python3
"""
Script to import worksheet questions into the Tutor AI database
Based on Helen Grogan Tuition worksheets for 7+ mathematics
"""

import sys
import os
from datetime import datetime

# Set PostgreSQL URL for import
DATABASE_URL = "postgresql://postgres:NAjDrYiSrjQqeIOyIqAJUbXtIJIfGkzX@tramway.proxy.rlwy.net:47230/railway"
os.environ['DATABASE_URL'] = DATABASE_URL

# Import our database wrapper
from app import app
from utils.db_connection import get_db

def create_worksheet_questions():
    """Create and populate questions from the worksheets"""
    
    # First, define the questions with their classifications
    questions = [
        # PAGE 1 - Shape and Number Patterns
        {
            "topic": "Geometry",
            "subtopic": "Shape Recognition and Patterns", 
            "question": "One shape in each row is not finished. Copy out and complete the missing one from each row. (Numbers in circles: 51, 53, __, 57)",
            "difficulty": 2,
            "time_estimate": 3,
            "space_required": "small",
            "question_type": "pattern completion"
        },
        {
            "topic": "Geometry", 
            "subtopic": "Shape Recognition and Patterns",
            "question": "Complete the pattern with dots on dominoes (4 dominoes with increasing dot patterns)",
            "difficulty": 1,
            "time_estimate": 2,
            "space_required": "small",
            "question_type": "visual pattern"
        },
        {
            "topic": "Number",
            "subtopic": "Place Value",
            "question": "Complete the missing numbers in the grid pattern: 30, __, __, 40, 45",
            "difficulty": 2,
            "time_estimate": 2,
            "space_required": "none",
            "question_type": "number sequence"
        },
        
        # PAGE 2 - Sequence Ordering
        {
            "topic": "Geometry",
            "subtopic": "Shape Recognition and Patterns",
            "question": "Put the next four items in the right order using letters A, B, C and D (geometric shape progression)",
            "difficulty": 2,
            "time_estimate": 4,
            "space_required": "small",
            "question_type": "sequence ordering"
        },
        {
            "topic": "Geometry",
            "subtopic": "Shape Recognition and Patterns", 
            "question": "Order 3D shapes by rotating patterns (cubes with different face patterns)",
            "difficulty": 3,
            "time_estimate": 5,
            "space_required": "small",
            "question_type": "3D visualization"
        },
        {
            "topic": "Number",
            "subtopic": "Number Ordering",
            "question": "Order numbers in sequence: 10, 33, 30, 13, 31",
            "difficulty": 2,
            "time_estimate": 2,
            "space_required": "none",
            "question_type": "number ordering"
        },
        
        # PAGE 3 - Counting
        {
            "topic": "Number",
            "subtopic": "Counting and Number Sequences",
            "question": "Count on in tens from the number in the first box: 6, __, __, __, __",
            "difficulty": 1,
            "time_estimate": 2,
            "space_required": "none",
            "question_type": "counting sequence"
        },
        {
            "topic": "Number",
            "subtopic": "Counting and Number Sequences", 
            "question": "Count back in tens from 95: __, __, __, __, __, __, __, 95",
            "difficulty": 1,
            "time_estimate": 2,
            "space_required": "none",
            "question_type": "counting sequence"
        },
        {
            "topic": "Number",
            "subtopic": "Counting and Number Sequences",
            "question": "Write 33 and 38 in the correct place on this number line: 30 __ __ __ 35 __ __ __ 40",
            "difficulty": 2,
            "time_estimate": 3,
            "space_required": "none",
            "question_type": "number line"
        },
        {
            "topic": "Number",
            "subtopic": "Even and Odd Numbers",
            "question": "Cross out the even numbers in the list: 16, 19, 3, 28, 13, 22, 29, 26, 7, 10",
            "difficulty": 2,
            "time_estimate": 3,
            "space_required": "none",
            "question_type": "number classification"
        },
        {
            "topic": "Number",
            "subtopic": "Even and Odd Numbers",
            "question": "Cross out the odd numbers in the list: 25, 18, 6, 30, 15, 12, 1, 14, 11, 23",
            "difficulty": 2, 
            "time_estimate": 3,
            "space_required": "none",
            "question_type": "number classification"
        },
        
        # PAGE 4 - Place Value
        {
            "topic": "Number",
            "subtopic": "Place Value",
            "question": "What number does each abacus show? (4 different abacus representations)",
            "difficulty": 2,
            "time_estimate": 4,
            "space_required": "small",
            "question_type": "place value reading"
        },
        {
            "topic": "Number", 
            "subtopic": "Place Value",
            "question": "Swap round the digits in your answers and show each new number on the abacus drawings",
            "difficulty": 3,
            "time_estimate": 5,
            "space_required": "medium",
            "question_type": "place value manipulation"
        },
        {
            "topic": "Number",
            "subtopic": "Place Value",
            "question": "Fill in the missing number: a) 99 = 90 + __ b) 88 = 81 + __ c) 70 = __ + 2",
            "difficulty": 2,
            "time_estimate": 3,
            "space_required": "none",
            "question_type": "number bonds"
        },
        {
            "topic": "Number",
            "subtopic": "Number Ordering", 
            "question": "Write down the largest number you can using these digits: a) 4,5 b) 6,3 c) 2,7 d) 8,9",
            "difficulty": 2,
            "time_estimate": 3,
            "space_required": "none",
            "question_type": "number formation"
        },
        
        # PAGE 5 - Data Handling (Venn Diagrams)
        {
            "topic": "Statistics",
            "subtopic": "Venn Diagrams",
            "question": "Put these numbers on the Venn diagram (Odd numbers / Numbers with 2 tens): 11, 23, 28 and 27",
            "difficulty": 3,
            "time_estimate": 5,
            "space_required": "medium",
            "question_type": "Venn diagram classification"
        },
        {
            "topic": "Statistics",
            "subtopic": "Venn Diagrams", 
            "question": "Which numbers have two tens and are odd numbers?",
            "difficulty": 2,
            "time_estimate": 2,
            "space_required": "small",
            "question_type": "data interpretation"
        },
        {
            "topic": "Statistics",
            "subtopic": "Venn Diagrams",
            "question": "Which numbers are even numbers? (from the Venn diagram)",
            "difficulty": 2,
            "time_estimate": 2,
            "space_required": "small", 
            "question_type": "data interpretation"
        },
        {
            "topic": "Statistics",
            "subtopic": "Data Organization",
            "question": "Circle the most costly item and cross out the cheapest one: pen (2 for 40p), ruler (25p each), rubber (2 for 30p), pencil (12p each)",
            "difficulty": 3,
            "time_estimate": 4,
            "space_required": "none",
            "question_type": "cost comparison"
        },
        
        # PAGE 6 - Data Handling (Charts and Tables)
        {
            "topic": "Statistics",
            "subtopic": "Bar Charts and Graphs",
            "question": "How many more children were off school on Tuesday than on Wednesday?",
            "difficulty": 2,
            "time_estimate": 2,
            "space_required": "none",
            "question_type": "chart interpretation"
        },
        {
            "topic": "Statistics",
            "subtopic": "Bar Charts and Graphs",
            "question": "On which day were the most children off school?",
            "difficulty": 1,
            "time_estimate": 1,
            "space_required": "none",
            "question_type": "chart interpretation"
        },
        {
            "topic": "Statistics",
            "subtopic": "Tables and Data Organization",
            "question": "Finish off this table: 2 rubbers=10p, 3 rubbers=?, 1 rubber=?, 4 rubbers=?, 5 rubbers=?",
            "difficulty": 2,
            "time_estimate": 3,
            "space_required": "small",
            "question_type": "pattern in tables"
        },
        {
            "topic": "Statistics",
            "subtopic": "Tables and Data Organization",
            "question": "There are 21 crayons. 4 are red, 6 are blue, 3 are green and the remainder are pink. Put this information on the table.",
            "difficulty": 3,
            "time_estimate": 4,
            "space_required": "small",
            "question_type": "data organization"
        },
        
        # PAGE 7 - Geometry (Triangle Counting)
        {
            "topic": "Geometry",
            "subtopic": "Triangle Counting",
            "question": "How many triangles can you see in each drawing? (12 different geometric figures)",
            "difficulty": 3,
            "time_estimate": 8,
            "space_required": "small",
            "question_type": "visual counting"
        },
        
        # PAGE 8 - Number Triangles (Algebra/Puzzles)
        {
            "topic": "Algebra",
            "subtopic": "Number Puzzles",
            "question": "The numbers in each pair of circles add up to the number in the square between them. Find the missing numbers. (Triangle A: 4 at top, 3 and ? at bottom, with 9 in middle square)",
            "difficulty": 3,
            "time_estimate": 6,
            "space_required": "medium",
            "question_type": "number triangle puzzle"
        },
        {
            "topic": "Algebra",
            "subtopic": "Number Puzzles", 
            "question": "Number triangle puzzle B: Find missing numbers when sum relationships are given (5 and 10 visible, 6 at corner)",
            "difficulty": 3,
            "time_estimate": 6,
            "space_required": "medium",
            "question_type": "number triangle puzzle"
        },
        {
            "topic": "Algebra",
            "subtopic": "Number Puzzles",
            "question": "Number triangle puzzle with larger numbers: 40 at top, 43 and 13 at bottom, find middle values",
            "difficulty": 3,
            "time_estimate": 7,
            "space_required": "medium",
            "question_type": "number triangle puzzle"
        },
        
        # PAGE 9 - Fractions (Recognition)
        {
            "topic": "Fractions",
            "subtopic": "Fraction Recognition",
            "question": "What fraction is shaded? (Circle with half shaded)",
            "difficulty": 1,
            "time_estimate": 1,
            "space_required": "none",
            "question_type": "fraction identification"
        },
        {
            "topic": "Fractions",
            "subtopic": "Fraction Recognition", 
            "question": "What fraction is shaded? (Rectangle with diagonal half shaded)",
            "difficulty": 2,
            "time_estimate": 2,
            "space_required": "none",
            "question_type": "fraction identification"
        },
        {
            "topic": "Fractions",
            "subtopic": "Fraction Recognition",
            "question": "What fraction is shaded? (Circle divided into quarters with one quarter shaded)",
            "difficulty": 2,
            "time_estimate": 2,
            "space_required": "none",
            "question_type": "fraction identification"
        },
        {
            "topic": "Fractions", 
            "subtopic": "Fraction Recognition",
            "question": "What fraction is shaded? (Various complex shapes - hexagon, triangles, etc.)",
            "difficulty": 3,
            "time_estimate": 3,
            "space_required": "none",
            "question_type": "fraction identification"
        },
        
        # PAGE 10 - Fractions (Representation)
        {
            "topic": "Fractions",
            "subtopic": "Fraction Representation",
            "question": "Color 1/3 of the circle",
            "difficulty": 2,
            "time_estimate": 2,
            "space_required": "none",
            "question_type": "fraction representation"
        },
        {
            "topic": "Fractions",
            "subtopic": "Fraction Representation",
            "question": "Color 3/4 of the rectangle",
            "difficulty": 2,
            "time_estimate": 2,
            "space_required": "none",
            "question_type": "fraction representation"
        },
        {
            "topic": "Fractions",
            "subtopic": "Fraction Representation",
            "question": "Color 1/2 of the triangle",
            "difficulty": 2,
            "time_estimate": 2,
            "space_required": "none",
            "question_type": "fraction representation"
        },
        {
            "topic": "Fractions",
            "subtopic": "Fraction Representation",
            "question": "Color 2/4 of the parallelogram",
            "difficulty": 2,
            "time_estimate": 2,
            "space_required": "none",
            "question_type": "fraction representation"
        },
        
        # PAGE 11 - Basic Algebra
        {
            "topic": "Algebra",
            "subtopic": "Basic Algebra",
            "question": "C = 2, D = 3, E = 5, F = 8, G = 10. Calculate C + D + E = ?",
            "difficulty": 1,
            "time_estimate": 2,
            "space_required": "none",
            "question_type": "substitution"
        },
        {
            "topic": "Algebra",
            "subtopic": "Basic Algebra",
            "question": "A = 3, B = 4, C = 5, D = 9, E = 12. Calculate A × B = ?",
            "difficulty": 2,
            "time_estimate": 2,
            "space_required": "none",
            "question_type": "substitution"
        },
        {
            "topic": "Algebra", 
            "subtopic": "Basic Algebra",
            "question": "B = 3, C = 5, D = 8, E = 19, F = 24. Calculate B × D - C = ?",
            "difficulty": 3,
            "time_estimate": 4,
            "space_required": "small",
            "question_type": "complex substitution"
        },
        {
            "topic": "Algebra",
            "subtopic": "Basic Algebra",
            "question": "E = 2, F = 3, G = 10, H = 11, J = 12. Calculate E × H - J = ?",
            "difficulty": 3,
            "time_estimate": 4,
            "space_required": "small",
            "question_type": "complex substitution"
        }
    ]
    
    return questions

def insert_questions_into_database():
    """Insert all questions into the database"""
    
    with app.app_context():
        with get_db() as db:
            # Get the questions
            questions = create_worksheet_questions()
            
            print(f"Inserting {len(questions)} questions into database...")
            
            # Get tutor ID (assuming admin user for created_by_tutor_id)
            result = db.execute("SELECT id FROM tutors WHERE username = ?", ('admin',)).fetchone()
            if isinstance(result, dict):
                admin_id = result['id']
            else:
                admin_id = result[0] if result else 1
            
            # Track topics and subtopics we need to create
            topics_created = {}
            subtopics_created = {}
            
            for i, q in enumerate(questions, 1):
                try:
                    # Get or create main topic
                    topic_name = q['topic']
                    if topic_name not in topics_created:
                        topic_result = db.execute("SELECT id FROM main_topics WHERE topic_name = ?", (topic_name,)).fetchone()
                        
                        if topic_result:
                            if isinstance(topic_result, dict):
                                topics_created[topic_name] = topic_result['id']
                            else:
                                topics_created[topic_name] = topic_result[0]
                        else:
                            # Create new topic
                            db.execute("""
                                INSERT INTO main_topics (topic_name, description, target_year_groups, color_code)
                                VALUES (?, ?, ?, ?)
                            """, (topic_name, f"{topic_name} curriculum area", "Year 2-6", "#607EBC"))
                            
                            # Get the inserted ID
                            new_topic = db.execute("SELECT id FROM main_topics WHERE topic_name = ?", (topic_name,)).fetchone()
                            if isinstance(new_topic, dict):
                                topics_created[topic_name] = new_topic['id']
                            else:
                                topics_created[topic_name] = new_topic[0]
                            print(f"Created new topic: {topic_name}")
                    
                    main_topic_id = topics_created[topic_name]
            
                    # Get or create subtopic
                    subtopic_name = q['subtopic']
                    subtopic_key = f"{topic_name}:{subtopic_name}"
                    
                    if subtopic_key not in subtopics_created:
                        subtopic_result = db.execute("SELECT id FROM subtopics WHERE subtopic_name = ? AND main_topic_id = ?", 
                                     (subtopic_name, main_topic_id)).fetchone()
                        
                        if subtopic_result:
                            if isinstance(subtopic_result, dict):
                                subtopics_created[subtopic_key] = subtopic_result['id']
                            else:
                                subtopics_created[subtopic_key] = subtopic_result[0]
                        else:
                            # Create new subtopic
                            db.execute("""
                                INSERT INTO subtopics (main_topic_id, subtopic_name, description, difficulty_order)
                                VALUES (?, ?, ?, ?)
                            """, (main_topic_id, subtopic_name, f"{subtopic_name} skills", q['difficulty']))
                            
                            # Get the inserted ID
                            new_subtopic = db.execute("SELECT id FROM subtopics WHERE subtopic_name = ? AND main_topic_id = ?", 
                                                    (subtopic_name, main_topic_id)).fetchone()
                            if isinstance(new_subtopic, dict):
                                subtopics_created[subtopic_key] = new_subtopic['id']
                            else:
                                subtopics_created[subtopic_key] = new_subtopic[0]
                            print(f"Created new subtopic: {subtopic_name}")
                    
                    subtopic_id = subtopics_created[subtopic_key]
                    
                    # Insert the question
                    db.execute("""
                        INSERT INTO questions 
                        (subtopic_id, question_text, difficulty_level, time_estimate_minutes, 
                         space_required, question_type, created_by_tutor_id, active)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (subtopic_id, q['question'], q['difficulty'], q['time_estimate'], 
                          q['space_required'], q['question_type'], admin_id, True))
                    
                    print(f"Question {i:2d}: {q['question'][:50]}...")
                    
                except Exception as e:
                    print(f"Error inserting question {i}: {e}")
                    import traceback
                    traceback.print_exc()
                    continue
            
            print(f"\nSuccessfully imported {len(questions)} questions!")
            print(f"Created {len(topics_created)} topics and {len(subtopics_created)} subtopics")

def main():
    """Main function"""
    print("Helen Grogan Tuition Worksheet Import")
    print("=" * 50)
    
    try:
        insert_questions_into_database()
        print("\n✅ Import completed successfully!")
        
        # Show summary
        with app.app_context():
            with get_db() as db:
                questions_result = db.execute("SELECT COUNT(*) FROM questions").fetchone()
                topics_result = db.execute("SELECT COUNT(*) FROM main_topics").fetchone()
                subtopics_result = db.execute("SELECT COUNT(*) FROM subtopics").fetchone()
                
                if isinstance(questions_result, dict):
                    total_questions = questions_result['count']
                    total_topics = topics_result['count']
                    total_subtopics = subtopics_result['count']
                else:
                    total_questions = questions_result[0]
                    total_topics = topics_result[0]
                    total_subtopics = subtopics_result[0]
                
                print(f"\nDatabase now contains:")
                print(f"  📚 {total_topics} main topics")
                print(f"  📝 {total_subtopics} subtopics") 
                print(f"  ❓ {total_questions} total questions")
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())