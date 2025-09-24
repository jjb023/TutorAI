# web/worksheet/services.py
from utils.db_connection import get_db
import json
import random
from datetime import datetime

class QuestionService:
    @staticmethod
    def create_question(subtopic_id, question_text, difficulty_level, 
                       time_estimate, space_required, tutor_id, 
                       question_type=None, answer=None, is_template=False, template_params=None):
        """Add a new question to the bank with optional template support."""
        with get_db() as db:
            db.execute('''
                INSERT INTO questions 
                (subtopic_id, question_text, answer, difficulty_level, 
                 time_estimate_minutes, space_required, question_type, 
                 created_by_tutor_id, active, is_template, template_params)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (subtopic_id, question_text, answer, difficulty_level, 
                  time_estimate, space_required, question_type, tutor_id, 
                  True, is_template, template_params))
            
            # Get the inserted ID
            result = db.execute("SELECT id FROM questions WHERE subtopic_id = ? AND question_text = ? ORDER BY id DESC LIMIT 1", 
                              (subtopic_id, question_text)).fetchone()
            if isinstance(result, dict):
                return result['id']
            else:
                return result[0] if result else None

    @staticmethod
    def parse_template_variables(question_text):
        """Extract variables from question text like {num1:1-20}"""
        import re
        import json
        
        # Pattern to match {variable:min-max} or just {variable}
        pattern = r'\{(\w+)(?::(\d+)-(\d+))?\}'
        matches = re.findall(pattern, question_text)
        
        variables = {}
        for match in matches:
            var_name = match[0]
            min_val = int(match[1]) if match[1] else 1
            max_val = int(match[2]) if match[2] else 100
            
            variables[var_name] = {
                "type": "int",
                "min": min_val,
                "max": max_val
            }
        
        return json.dumps(variables) if variables else None

    @staticmethod
    def generate_question_from_template(template_text, template_params):
        """Generate a specific question from a template"""
        import json
        import random
        import re
        
        if isinstance(template_params, str):
            params = json.loads(template_params)
        else:
            params = template_params
        
        generated_text = template_text
        generated_values = {}
        
        for var_name, config in params.items():
            if config['type'] == 'int':
                value = random.randint(config['min'], config['max'])
            else:
                value = config['min']  # Default for now
            
            generated_values[var_name] = value
            # Replace all occurrences of the variable
            generated_text = re.sub(
                rf'\{{{var_name}(?::\d+-\d+)?\}}', 
                str(value), 
                generated_text
            )
        
        # Try to calculate answer for simple math
        answer = QuestionService._calculate_simple_answer(generated_text, generated_values)
        
        return generated_text, answer, generated_values

    @staticmethod
    def _calculate_simple_answer(question_text, values):
        """Calculate answer for simple addition/subtraction"""
        # Simple cases only - you can expand this
        if 'num1' in values and 'num2' in values:
            if '+' in question_text and '?' in question_text:
                return str(values['num1'] + values['num2'])
            elif '-' in question_text and '?' in question_text:
                return str(values['num1'] - values['num2'])
        return None
    
    @staticmethod
    def get_questions_by_subtopic(subtopic_id, difficulty_level=None):
        """Get questions for a subtopic, optionally filtered by difficulty."""
        with get_db() as db:
            if difficulty_level:
                result = db.execute('''
                    SELECT * FROM questions 
                    WHERE subtopic_id = ? AND difficulty_level = ? AND active = true
                    ORDER BY created_date DESC
                ''', (subtopic_id, difficulty_level))
            else:
                result = db.execute('''
                    SELECT * FROM questions 
                    WHERE subtopic_id = ? AND active = true
                    ORDER BY difficulty_level, created_date DESC
                ''', (subtopic_id,))
            
            questions = result.fetchall()
            
            # Convert to list of dictionaries
            if questions and isinstance(questions[0], dict):
                return questions
            else:
                # Handle Row objects - convert to dict
                return [dict(q) for q in questions]
    
    @staticmethod
    def update_question(question_id, question_text=None, answer=None,
                       difficulty_level=None, time_estimate=None, 
                       space_required=None, question_type=None):
        """Update an existing question."""
        with get_db() as db:
            updates = []
            params = []
            
            if question_text is not None:
                updates.append("question_text = ?")
                params.append(question_text)
            if answer is not None:
                updates.append("answer = ?")
                params.append(answer)
            if difficulty_level is not None:
                updates.append("difficulty_level = ?")
                params.append(difficulty_level)
            if time_estimate is not None:
                updates.append("time_estimate_minutes = ?")
                params.append(time_estimate)
            if space_required is not None:
                updates.append("space_required = ?")
                params.append(space_required)
            if question_type is not None:
                updates.append("question_type = ?")
                params.append(question_type)
            
            if updates:
                params.append(question_id)
                query = f"UPDATE questions SET {', '.join(updates)} WHERE id = ?"
                db.execute(query, params)
    
    @staticmethod
    def get_question(question_id):
        """Get a single question by ID."""
        with get_db() as db:
            result = db.execute('''
                SELECT * FROM questions WHERE id = ?
            ''', (question_id,))
            question = result.fetchone()
            
            if question:
                return dict(question) if isinstance(question, dict) else dict(question)
            return None
    
    @staticmethod
    def delete_question(question_id):
        """Soft delete a question (mark as inactive)."""
        with get_db() as db:
            db.execute('UPDATE questions SET active = false WHERE id = ?', (question_id,))
    
    @staticmethod
    def get_question_stats(subtopic_id):
        """Get statistics about questions for a subtopic."""
        with get_db() as db:
            result_query = db.execute('''
                SELECT 
                    difficulty_level,
                    COUNT(*) as count,
                    AVG(time_estimate_minutes) as avg_time
                FROM questions 
                WHERE subtopic_id = ? AND active = true
                GROUP BY difficulty_level
            ''', (subtopic_id,))
            stats = result_query.fetchall()
            
            # Convert to dictionary format with default values
            result = {
                'easy': {'count': 0, 'avg_time': 0},
                'medium': {'count': 0, 'avg_time': 0},
                'hard': {'count': 0, 'avg_time': 0}
            }
            
            for stat in stats:
                if isinstance(stat, dict):
                    difficulty = stat['difficulty_level']
                    count = stat['count']
                    avg_time = stat['avg_time']
                else:
                    difficulty = stat[0]
                    count = stat[1]
                    avg_time = stat[2]
                
                if difficulty == 1:
                    result['easy'] = {'count': count, 'avg_time': avg_time or 0}
                elif difficulty == 2:
                    result['medium'] = {'count': count, 'avg_time': avg_time or 0}
                elif difficulty == 3:
                    result['hard'] = {'count': count, 'avg_time': avg_time or 0}
            
            return result


class WorksheetService:
    @staticmethod
    def get_recommended_difficulty(student_id, subtopic_id):
        """Recommend worksheet difficulty based on student's current mastery."""
        with get_db() as db:
            # Get student's current mastery level
            result = db.execute('''
                SELECT mastery_level FROM subtopic_progress
                WHERE student_id = ? AND subtopic_id = ?
            ''', (student_id, subtopic_id))
            progress = result.fetchone()
            
            if not progress:
                return 'easy', {'easy': 70, 'medium': 25, 'hard': 5}
            
            if isinstance(progress, dict):
                mastery = progress['mastery_level']
            else:
                mastery = progress[0]
            
            if not mastery or mastery == 0:
                return 'easy', {'easy': 70, 'medium': 25, 'hard': 5}
            
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
        with get_db() as db:
            # Get student and subtopic info
            student_result = db.execute('SELECT name FROM students WHERE id = ?', (student_id,))
            student = student_result.fetchone()
            
            subtopic_result = db.execute('''
                SELECT s.subtopic_name, mt.topic_name 
                FROM subtopics s
                JOIN main_topics mt ON s.main_topic_id = mt.id
                WHERE s.id = ?
            ''', (subtopic_id,))
            subtopic = subtopic_result.fetchone()
            
            if not student or not subtopic:
                raise ValueError("Invalid student or subtopic")
            
            # Convert results to consistent format
            if isinstance(student, dict):
                student_name = student['name']
            else:
                student_name = student[0]
            
            if isinstance(subtopic, dict):
                topic_name = subtopic['topic_name']
                subtopic_name = subtopic['subtopic_name']
            else:
                subtopic_name = subtopic[0]
                topic_name = subtopic[1]
            
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
                title = f"{topic_name} - {subtopic_name} Practice"
            
            db.execute('''
                INSERT INTO worksheets 
                (student_id, subtopic_id, title, difficulty_level, 
                 generated_by_tutor_id, status)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (student_id, subtopic_id, title, 'mixed', tutor_id, 'draft'))
            
            # Get the inserted worksheet ID
            worksheet_result = db.execute('''
                SELECT id FROM worksheets 
                WHERE student_id = ? AND subtopic_id = ? AND title = ?
                ORDER BY id DESC LIMIT 1
            ''', (student_id, subtopic_id, title))
            worksheet_row = worksheet_result.fetchone()
            
            if isinstance(worksheet_row, dict):
                worksheet_id = worksheet_row['id']
            else:
                worksheet_id = worksheet_row[0]
            
            # Add questions to worksheet
            for i, question in enumerate(selected_questions, 1):
                if question.get('is_template'):
                    # Generate a specific instance from the template
                    generated_text, generated_answer, values = QuestionService.generate_question_from_template(
                        question['question_text'],
                        question.get('template_params')
                    )
                    
                    # Save with generated text
                    db.execute('''
                        INSERT INTO worksheet_questions 
                        (worksheet_id, question_id, question_order, space_allocated, custom_question_text)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (worksheet_id, question['id'], i, question['space_required'], generated_text))
                else:
                    # Regular static question
                    db.execute('''
                        INSERT INTO worksheet_questions 
                        (worksheet_id, question_id, question_order, space_allocated)
                        VALUES (?, ?, ?, ?)
                    ''', (worksheet_id, question['id'], i, question['space_required']))
            
            return worksheet_id
    
    @staticmethod
    def get_worksheet(worksheet_id):
        """Get worksheet with all questions."""
        with get_db() as db:
            # Get worksheet info
            worksheet_result = db.execute('''
                SELECT w.*, s.name as student_name, sub.subtopic_name, mt.topic_name
                FROM worksheets w
                JOIN students s ON w.student_id = s.id
                JOIN subtopics sub ON w.subtopic_id = sub.id
                JOIN main_topics mt ON sub.main_topic_id = mt.id
                WHERE w.id = ?
            ''', (worksheet_id,))
            worksheet = worksheet_result.fetchone()
            
            if not worksheet:
                return None
            
            # Get questions
            questions_result = db.execute('''
                SELECT 
                    wq.*,
                    q.question_text as original_text,
                    q.answer,
                    q.difficulty_level,
                    q.time_estimate_minutes,
                    q.space_required
                FROM worksheet_questions wq
                JOIN questions q ON wq.question_id = q.id
                WHERE wq.worksheet_id = ?
                ORDER BY wq.question_order
            ''', (worksheet_id,))
            questions = questions_result.fetchall()
            
            # Convert to consistent format
            worksheet_dict = dict(worksheet) if isinstance(worksheet, dict) else dict(worksheet)
            questions_list = []
            
            for q in questions:
                if isinstance(q, dict):
                    questions_list.append(q)
                else:
                    questions_list.append(dict(q))
            
            return {
                'worksheet': worksheet_dict,
                'questions': questions_list
            }
    
    @staticmethod
    def update_worksheet_question(worksheet_id, question_order, new_text=None, 
                                 new_space=None):
        """Update a specific question in a worksheet."""
        with get_db() as db:
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
                db.execute(query, params)
    
    @staticmethod
    def finalize_worksheet(worksheet_id, pdf_path):
        """Mark worksheet as finalized with PDF path."""
        with get_db() as db:
            db.execute('''
                UPDATE worksheets 
                SET status = ?, pdf_path = ?
                WHERE id = ?
            ''', ('finalized', pdf_path, worksheet_id))