# web/session/services.py
from utils.database import get_db_connection
from datetime import datetime
import json

class SessionService:
    @staticmethod
    def create_session_with_progress(student_id, tutor_id, duration_minutes, 
                                    subtopic_assessments, session_notes=None):
        """Create a session and update subtopic progress in one transaction."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            try:
                # Start transaction
                conn.execute('BEGIN')
                
                # 1. Create the session
                cursor.execute('''
                    INSERT INTO sessions (student_id, tutor_id, session_date, duration_minutes, tutor_notes)
                    VALUES (?, ?, ?, ?, ?)
                ''', (student_id, tutor_id, datetime.now().isoformat(), duration_minutes, session_notes))
                
                session_id = cursor.lastrowid
                
                # 2. Update subtopic progress and track what was assessed
                topics_covered = set()
                
                for subtopic_id, assessment_data in subtopic_assessments.items():
                    mastery_level = assessment_data['level']
                    notes = assessment_data.get('notes', '')
                    
                    # Get current level for comparison
                    cursor.execute('''
                        SELECT mastery_level FROM subtopic_progress 
                        WHERE student_id = ? AND subtopic_id = ?
                    ''', (student_id, subtopic_id))
                    
                    current = cursor.fetchone()
                    old_level = current[0] if current else 0
                    
                    # Update or insert progress
                    cursor.execute('''
                        INSERT OR REPLACE INTO subtopic_progress 
                        (student_id, subtopic_id, mastery_level, last_assessed, notes)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (student_id, subtopic_id, mastery_level, datetime.now().isoformat(), notes))
                    
                    # Track which main topic this belongs to
                    cursor.execute('''
                        SELECT mt.topic_name FROM subtopics s
                        JOIN main_topics mt ON s.main_topic_id = mt.id
                        WHERE s.id = ?
                    ''', (subtopic_id,))
                    topic = cursor.fetchone()
                    if topic:
                        topics_covered.add(topic[0])
                
                # 3. Update session with topics covered
                if topics_covered:
                    cursor.execute('''
                        UPDATE sessions 
                        SET main_topics_covered = ?
                        WHERE id = ?
                    ''', (', '.join(topics_covered), session_id))
                
                # 4. Update student's last session date
                cursor.execute('''
                    UPDATE students 
                    SET last_session_date = CURRENT_TIMESTAMP 
                    WHERE id = ?
                ''', (student_id,))
                
                # Commit transaction
                conn.commit()
                
                print(f"✅ Session created with {len(subtopic_assessments)} subtopic updates")
                return session_id
                
            except Exception as e:
                # Rollback on error
                conn.rollback()
                print(f"❌ Error creating session: {e}")
                raise e
    
    @staticmethod
    def get_student_progress_summary(student_id):
        """Get comprehensive progress data for a student."""
        with get_db_connection() as conn:
            # Get topic summaries with progress
            topic_summaries = conn.execute('''
                SELECT 
                    mt.id,
                    mt.topic_name,
                    mt.color_code,
                    COUNT(s.id) as total_subtopics,
                    COUNT(sp.id) as assessed_subtopics,
                    ROUND(AVG(CASE WHEN sp.mastery_level IS NOT NULL THEN sp.mastery_level ELSE 0 END), 1) as avg_mastery,
                    ROUND((COUNT(sp.id) * 100.0 / COUNT(s.id)), 1) as completion_percentage
                FROM main_topics mt
                LEFT JOIN subtopics s ON mt.id = s.main_topic_id
                LEFT JOIN subtopic_progress sp ON s.id = sp.subtopic_id AND sp.student_id = ?
                GROUP BY mt.id
                ORDER BY mt.topic_name
            ''', (student_id,)).fetchall()
            
            # Get detailed subtopic progress
            detailed_progress = []
            for topic in topic_summaries:
                subtopics = conn.execute('''
                    SELECT 
                        s.id,
                        s.subtopic_name,
                        s.difficulty_order,
                        COALESCE(sp.mastery_level, 0) as mastery_level,
                        sp.last_assessed,
                        sp.questions_attempted,
                        sp.questions_correct,
                        sp.notes
                    FROM subtopics s
                    LEFT JOIN subtopic_progress sp ON s.id = sp.subtopic_id AND sp.student_id = ?
                    WHERE s.main_topic_id = ?
                    ORDER BY s.difficulty_order
                ''', (student_id, topic['id'])).fetchall()
                
                detailed_progress.append({
                    'topic_name': topic['topic_name'],
                    'color_code': topic['color_code'],
                    'subtopics': subtopics
                })
            
            # Get weak areas (mastery level 3-6)
            weak_areas = conn.execute('''
                SELECT 
                    s.subtopic_name,
                    mt.topic_name,
                    sp.mastery_level
                FROM subtopic_progress sp
                JOIN subtopics s ON sp.subtopic_id = s.id
                JOIN main_topics mt ON s.main_topic_id = mt.id
                WHERE sp.student_id = ? AND sp.mastery_level BETWEEN 3 AND 6
                ORDER BY sp.mastery_level ASC
                LIMIT 5
            ''', (student_id,)).fetchall()
            
            # Get areas ready to advance (mastery level >= 8)
            ready_to_advance = conn.execute('''
                SELECT 
                    s.subtopic_name,
                    s.id,
                    next_s.subtopic_name as next_subtopic
                FROM subtopic_progress sp
                JOIN subtopics s ON sp.subtopic_id = s.id
                LEFT JOIN subtopics next_s ON next_s.main_topic_id = s.main_topic_id 
                    AND next_s.difficulty_order = s.difficulty_order + 1
                WHERE sp.student_id = ? AND sp.mastery_level >= 8
                    AND next_s.id NOT IN (
                        SELECT subtopic_id FROM subtopic_progress 
                        WHERE student_id = ? AND mastery_level > 0
                    )
                LIMIT 3
            ''', (student_id, student_id)).fetchall()
            
            return {
                'topic_summaries': topic_summaries,
                'detailed_progress': detailed_progress,
                'weak_areas': weak_areas,
                'ready_to_advance': ready_to_advance
            }
    
    @staticmethod
    def get_session_entry_data():
        """Get data needed for session entry form."""
        with get_db_connection() as conn:
            # Get all topics with their subtopics and include current progress if student is selected
            topics = conn.execute('''
                SELECT 
                    mt.id,
                    mt.topic_name,
                    mt.color_code
                FROM main_topics mt
                ORDER BY mt.topic_name
            ''').fetchall()
            
            topics_with_subtopics = []
            for topic in topics:
                subtopics = conn.execute('''
                    SELECT 
                        s.id,
                        s.subtopic_name,
                        s.difficulty_order
                    FROM subtopics s
                    WHERE s.main_topic_id = ?
                    ORDER BY s.difficulty_order
                ''', (topic['id'],)).fetchall()
                
                # Convert Row objects to dictionaries
                subtopic_list = []
                for sub in subtopics:
                    subtopic_list.append({
                        'id': sub['id'],
                        'subtopic_name': sub['subtopic_name'],
                        'difficulty_order': sub['difficulty_order']
                    })
                
                topics_with_subtopics.append({
                    'id': topic['id'],
                    'topic_name': topic['topic_name'],
                    'color_code': topic['color_code'],
                    'subtopics': subtopic_list
                })
            
            return topics_with_subtopics
    
    @staticmethod
    def get_recent_sessions_with_progress(student_id, limit=5):
        """Get recent sessions with subtopic progress changes."""
        with get_db_connection() as conn:
            sessions = conn.execute('''
                SELECT 
                    s.id,
                    s.session_date,
                    s.duration_minutes,
                    s.main_topics_covered,
                    s.tutor_notes,
                    t.full_name as tutor_name
                FROM sessions s
                JOIN tutors t ON s.tutor_id = t.id
                WHERE s.student_id = ?
                ORDER BY s.session_date DESC
                LIMIT ?
            ''', (student_id, limit)).fetchall()
            
            # For each session, get what subtopics were assessed
            sessions_with_progress = []
            for session in sessions:
                # This is approximate - in a real system, you'd track session-subtopic relationships
                subtopics_assessed = conn.execute('''
                    SELECT 
                        s.subtopic_name,
                        sp.mastery_level as new_level
                    FROM subtopic_progress sp
                    JOIN subtopics s ON sp.subtopic_id = s.id
                    WHERE sp.student_id = ? 
                        AND date(sp.last_assessed) = date(?)
                ''', (student_id, session['session_date'])).fetchall()
                
                sessions_with_progress.append({
                    **dict(session),
                    'subtopics_assessed': subtopics_assessed
                })
            
            return sessions_with_progress