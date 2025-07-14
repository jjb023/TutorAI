from utils.database import get_db_connection
import json
import random
from datetime import datetime

class QuestionService:
    @staticmethod
    def create_question(subtopic_id, question_text, difficulty_level, 
                       time_estimate, space_required, tutor_id, question_type=None):
        """Add a new question to the bank."""
        with get_db_connection() as conn:
            cursor = conn.execute('''
                INSERT INTO questions 
                (subtopic_id, question_text, difficulty_level, time_estimate_minutes, 
                 space_required, question_type, created_by_tutor_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (subtopic_id, question_text, difficulty_level, time_estimate, 
                  space_required, question_type, tutor_id))
            conn.commit()
            return cursor.lastrowid
    
    @staticmethod
    def get_questions_by_subtopic(subtopic_id, difficulty_level=None):
        """Get questions for a subtopic, optionally filtered by difficulty."""
        with get_db_connection() as conn:
            if difficulty_level:
                questions = conn.execute('''
                    SELECT * FROM questions 
                    WHERE subtopic_id = ? AND difficulty_level = ? AND active = 1
                    ORDER BY created_date DESC
                ''', (subtopic_id, difficulty_level)).fetchall()
            else:
                questions = conn.execute('''
                    SELECT * FROM questions 
                    WHERE subtopic_id = ? AND active = 1
                    ORDER BY difficulty_level, created_date DESC
                ''', (subtopic_id,)).fetchall()
            
            return [dict(q) for q in questions]
    
    @staticmethod
    def update_question(question_id, question_text=None, difficulty_level=None, 
                       time_estimate=None, space_required=None):
        """Update an existing question."""
        with get_db_connection() as conn:
            updates = []
            params = []
            
            if question_text is not None:
                updates.append("question_text = ?")
                params.append(question_text)
            if difficulty_level is not None:
                updates.append("difficulty_level = ?")
                params.append(difficulty_level)
            if time_estimate is not None:
                updates.append("time_estimate_minutes = ?")
                params.append(time_estimate)
            if space_required is not None:
                updates.append("space_required = ?")
                params.append(space_required)
            
            if updates:
                params.append(question_id)
                query = f"UPDATE questions SET {', '.join(updates)} WHERE id = ?"
                conn.execute(query, params)
                conn.commit()
    
    @staticmethod
    def delete_question(question_id):
        """Soft delete a question (mark as inactive)."""
        with get_db_connection() as conn:
            conn.execute('UPDATE questions SET active = 0 WHERE id = ?', (question_id,))
            conn.commit()
    
    @staticmethod
    def get_question_stats(subtopic_id):
        """Get statistics about questions for a subtopic."""
        with get_db_connection() as conn:
            stats = conn.execute('''
                SELECT 
                    difficulty_level,
                    COUNT(*) as count,
                    AVG(time_estimate_minutes) as avg_time
                FROM questions 
                WHERE subtopic_id = ? AND active = 1
                GROUP BY difficulty_level
            ''', (subtopic_id,)).fetchall()
            
            return {
                'easy': next((s for s in stats if s['difficulty_level'] == 1), {'count': 0, 'avg_time': 0}),
                'medium': next((s for s in stats if s['difficulty_level'] == 2), {'count': 0, 'avg_time': 0}),
                'hard': next((s for s in stats if s['difficulty_level'] == 3), {'count': 0, 'avg_time': 0})
            }


class WorksheetService:
    @staticmethod
    def get_recommended_difficulty(student_id, subtopic_id):
        """Recommend worksheet difficulty based on student's current mastery."""
        with get_db_connection() as conn:
            # Get student's current mastery level
            progress = conn.execute('''
                SELECT mastery_level FROM subtopic_progress
                WHERE student_id = ? AND subtopic_id = ?
            ''', (student_id, subtopic_id)).fetchone()
            
            if not progress or progress['mastery_level'] == 0:
                return 'easy', {'easy': 70, 'medium': 25, 'hard': 5}
            
            mastery = progress['mastery_level']
            
            if mastery <= 3:
                return 'easy', {'easy': 70, 'medium': 25, 'hard': 5}
            elif mastery <= 6:
                return 'medium', {'easy': 30, 'medium': 50, 'hard': 20}
            elif mastery <= 8:
                return 'hard', {'easy': 20, 'medium': 40, 'hard': 40}
            else:
                return 'challenge', {'easy': 10, 'medium': 30, 'hard': 60}
    
    @staticmethod
    def generate_worksheet(student_id, subtopic_id, tutor_id, 
                          difficulty_distribution=None, total_questions=20,
                          title=None):
        """Generate a worksheet with smart question selection."""
        with get_db_connection() as conn:
            # Get student and subtopic info
            student = conn.execute('SELECT name FROM students WHERE id = ?', 
                                 (student_id,)).fetchone()
            subtopic = conn.execute('''
                SELECT s.subtopic_name, mt.topic_name 
                FROM subtopics s
                JOIN main_topics mt ON s.main_topic_id = mt.id
                WHERE s.id = ?
            ''', (subtopic_id,)).fetchone()
            
            if not student or not subtopic:
                raise ValueError("Invalid student or subtopic")
            
            # Get recommended difficulty if not provided
            if not difficulty_distribution:
                _, difficulty_distribution = WorksheetService.get_recommended_difficulty(
                    student_id, subtopic_id)
            
            # Calculate number of questions per difficulty
            easy_count = int(total_questions * difficulty_distribution['easy'] / 100)
            medium_count = int(total_questions * difficulty_distribution['medium'] / 100)
            hard_count = total_questions - easy_count - medium_count
            
            # Get questions from the bank
            selected_questions = []
            
            # Get easy questions
            easy_questions = QuestionService.get_questions_by_subtopic(subtopic_id, 1)
            if len(easy_questions) >= easy_count:
                selected_questions.extend(random.sample(easy_questions, easy_count))
            else:
                selected_questions.extend(easy_questions)
                print(f"Warning: Only {len(easy_questions)} easy questions available")
            
            # Get medium questions
            medium_questions = QuestionService.get_questions_by_subtopic(subtopic_id, 2)
            if len(medium_questions) >= medium_count:
                selected_questions.extend(random.sample(medium_questions, medium_count))
            else:
                selected_questions.extend(medium_questions)
                print(f"Warning: Only {len(medium_questions)} medium questions available")
            
            # Get hard questions
            hard_questions = QuestionService.get_questions_by_subtopic(subtopic_id, 3)
            if len(hard_questions) >= hard_count:
                selected_questions.extend(random.sample(hard_questions, hard_count))
            else:
                selected_questions.extend(hard_questions)
                print(f"Warning: Only {len(hard_questions)} hard questions available")
            
            # Create worksheet record
            if not title:
                title = f"{subtopic['topic_name']} - {subtopic['subtopic_name']} Practice"
            
            cursor = conn.execute('''
                INSERT INTO worksheets 
                (student_id, subtopic_id, title, difficulty_level, 
                 generated_by_tutor_id, status)
                VALUES (?, ?, ?, ?, ?, 'draft')
            ''', (student_id, subtopic_id, title, 'mixed', tutor_id))
            
            worksheet_id = cursor.lastrowid
            
            # Add questions to worksheet
            for i, question in enumerate(selected_questions, 1):
                conn.execute('''
                    INSERT INTO worksheet_questions 
                    (worksheet_id, question_id, question_order, space_allocated)
                    VALUES (?, ?, ?, ?)
                ''', (worksheet_id, question['id'], i, question['space_required']))
            
            conn.commit()
            
            return worksheet_id
    
    @staticmethod
    def get_worksheet(worksheet_id):
        """Get worksheet with all questions."""
        with get_db_connection() as conn:
            # Get worksheet info
            worksheet = conn.execute('''
                SELECT w.*, s.name as student_name, sub.subtopic_name, mt.topic_name
                FROM worksheets w
                JOIN students s ON w.student_id = s.id
                JOIN subtopics sub ON w.subtopic_id = sub.id
                JOIN main_topics mt ON sub.main_topic_id = mt.id
                WHERE w.id = ?
            ''', (worksheet_id,)).fetchone()
            
            if not worksheet:
                return None
            
            # Get questions
            questions = conn.execute('''
                SELECT 
                    wq.*,
                    q.question_text as original_text,
                    q.difficulty_level,
                    q.time_estimate_minutes,
                    q.space_required
                FROM worksheet_questions wq
                JOIN questions q ON wq.question_id = q.id
                WHERE wq.worksheet_id = ?
                ORDER BY wq.question_order
            ''', (worksheet_id,)).fetchall()
            
            return {
                'worksheet': dict(worksheet),
                'questions': [dict(q) for q in questions]
            }
    
    @staticmethod
    def update_worksheet_question(worksheet_id, question_order, new_text=None, 
                                 new_space=None):
        """Update a specific question in a worksheet."""
        with get_db_connection() as conn:
            updates = []
            params = []
            
            if new_text is not None:
                updates.append("custom_question_text = ?")
                params.append(new_text)
            if new_space is not None:
                updates.append("space_allocated = ?")
                params.append(new_space)
            
            if updates:
                params.extend([worksheet_id, question_order])
                query = f"""UPDATE worksheet_questions 
                           SET {', '.join(updates)} 
                           WHERE worksheet_id = ? AND question_order = ?"""
                conn.execute(query, params)
                conn.commit()
    
    @staticmethod
    def finalize_worksheet(worksheet_id, pdf_path):
        """Mark worksheet as finalized with PDF path."""
        with get_db_connection() as conn:
            conn.execute('''
                UPDATE worksheets 
                SET status = 'finalized', pdf_path = ?
                WHERE id = ?
            ''', (pdf_path, worksheet_id))
            conn.commit()