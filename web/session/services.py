# web/session/services.py
from utils.db_connection import get_db
from datetime import datetime
import json

class SessionService:
    @staticmethod
    def create_session_with_progress(student_id, tutor_id, duration_minutes, 
                                    subtopic_assessments, session_notes=None):
        """Create a session and update subtopic progress in one transaction."""
        with get_db() as db:
            try:
                # 1. Create the session
                db.execute('''
                    INSERT INTO sessions (student_id, tutor_id, session_date, duration_minutes, tutor_notes)
                    VALUES (?, ?, ?, ?, ?)
                ''', (student_id, tutor_id, datetime.now().isoformat(), duration_minutes, session_notes))
                
                # Get the inserted session ID
                result = db.execute('''
                    SELECT id FROM sessions 
                    WHERE student_id = ? AND tutor_id = ? AND session_date >= ? 
                    ORDER BY id DESC LIMIT 1
                ''', (student_id, tutor_id, datetime.now().isoformat()[:10])).fetchone()
                
                if isinstance(result, dict):
                    session_id = result['id']
                else:
                    session_id = result[0] if result else None
                
                if not session_id:
                    raise Exception("Failed to get session ID after insert")
                
                # 2. Update subtopic progress and track what was assessed
                topics_covered = set()
                
                for subtopic_id, assessment_data in subtopic_assessments.items():
                    mastery_level = assessment_data['level']
                    notes = assessment_data.get('notes', '')
                    
                    # Get current level for comparison
                    current_result = db.execute('''
                        SELECT mastery_level FROM subtopic_progress 
                        WHERE student_id = ? AND subtopic_id = ?
                    ''', (student_id, subtopic_id))
                    current = current_result.fetchone()
                    
                    if isinstance(current, dict):
                        old_level = current['mastery_level'] if current else 0
                    else:
                        old_level = current[0] if current else 0
                    
                    # PostgreSQL compatible upsert
                    db.execute('''
                        INSERT INTO subtopic_progress 
                        (student_id, subtopic_id, mastery_level, last_assessed, notes)
                        VALUES (?, ?, ?, ?, ?)
                        ON CONFLICT (student_id, subtopic_id) 
                        DO UPDATE SET 
                            mastery_level = EXCLUDED.mastery_level,
                            last_assessed = EXCLUDED.last_assessed,
                            notes = EXCLUDED.notes
                    ''', (student_id, subtopic_id, mastery_level, datetime.now().isoformat(), notes))
                    
                    # Track which main topic this belongs to
                    topic_result = db.execute('''
                        SELECT mt.topic_name FROM subtopics s
                        JOIN main_topics mt ON s.main_topic_id = mt.id
                        WHERE s.id = ?
                    ''', (subtopic_id,))
                    topic = topic_result.fetchone()
                    
                    if topic:
                        if isinstance(topic, dict):
                            topics_covered.add(topic['topic_name'])
                        else:
                            topics_covered.add(topic[0])
                
                # 3. Update session with topics covered
                if topics_covered:
                    db.execute('''
                        UPDATE sessions 
                        SET main_topics_covered = ?
                        WHERE id = ?
                    ''', (', '.join(topics_covered), session_id))
                
                # 4. Update student's last session date
                db.execute('''
                    UPDATE students 
                    SET last_session_date = CURRENT_TIMESTAMP 
                    WHERE id = ?
                ''', (student_id,))
                
                print(f"✅ Session created with {len(subtopic_assessments)} subtopic updates")
                return session_id
                
            except Exception as e:
                print(f"❌ Error creating session: {e}")
                raise e
    
    @staticmethod
    def get_student_progress_summary(student_id):
        """Get comprehensive progress data for a student."""
        with get_db() as db:
            # Get topic summaries with progress
            result = db.execute('''
                SELECT 
                    mt.id,
                    mt.topic_name,
                    mt.color_code,
                    COUNT(s.id) as total_subtopics,
                    COUNT(sp.id) as assessed_subtopics,
                    ROUND(AVG(CASE WHEN sp.mastery_level IS NOT NULL THEN sp.mastery_level ELSE 0 END), 1) as avg_mastery,
                    ROUND(CASE 
                        WHEN COUNT(s.id) > 0 THEN (COUNT(sp.id) * 100.0 / COUNT(s.id))
                        ELSE 0.0 
                    END, 1) as completion_percentage
                FROM main_topics mt
                LEFT JOIN subtopics s ON mt.id = s.main_topic_id
                LEFT JOIN subtopic_progress sp ON s.id = sp.subtopic_id AND sp.student_id = ?
                GROUP BY mt.id, mt.topic_name
                ORDER BY mt.topic_name
            ''', (student_id,))
            topic_summaries = result.fetchall()
            
            # Convert to consistent format
            if topic_summaries and isinstance(topic_summaries[0], dict):
                topic_summaries_list = topic_summaries
            else:
                topic_summaries_list = [dict(row) for row in topic_summaries]
            
            # detailed progress:
            detailed_progress = []
            for topic in topic_summaries_list:
                subtopics_result = db.execute('''
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
                ''', (student_id, topic['id']))
                subtopics = subtopics_result.fetchall()
                
                # Format the dates for each subtopic
                formatted_subtopics = []
                for subtopic in subtopics:
                    if isinstance(subtopic, dict):
                        subtopic_dict = subtopic
                    else:
                        subtopic_dict = dict(subtopic)
                        
                    if subtopic_dict['last_assessed']:
                        try:
                            from datetime import datetime
                            dt = datetime.fromisoformat(subtopic_dict['last_assessed'].replace('T', ' '))
                            subtopic_dict['last_assessed'] = dt.strftime('%d-%m-%y @ %H:%M')
                        except:
                            pass  # Keep original if parsing fails
                    formatted_subtopics.append(subtopic_dict)
                
                detailed_progress.append({
                    'topic_name': topic['topic_name'],
                    'color_code': topic['color_code'],
                    'subtopics': formatted_subtopics
                })
            
            # Get weak areas (mastery level 3-6)
            weak_areas_result = db.execute('''
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
            ''', (student_id,))
            weak_areas_raw = weak_areas_result.fetchall()
            
            # Convert to consistent format
            if weak_areas_raw and isinstance(weak_areas_raw[0], dict):
                weak_areas = weak_areas_raw
            else:
                weak_areas = [dict(row) for row in weak_areas_raw]
            
            # Get areas ready to advance (mastery level >= 8)
            ready_to_advance_result = db.execute('''
                SELECT 
                    s.subtopic_name,
                    s.id,
                    next_s.subtopic_name as next_subtopic
                FROM subtopic_progress sp
                JOIN subtopics s ON sp.subtopic_id = s.id
                LEFT JOIN subtopics next_s ON next_s.main_topic_id = s.main_topic_id 
                    AND next_s.difficulty_order = s.difficulty_order + 1
                WHERE sp.student_id = ? AND sp.mastery_level >= 8
                    AND (next_s.id IS NULL OR next_s.id NOT IN (
                        SELECT subtopic_id FROM subtopic_progress 
                        WHERE student_id = ? AND mastery_level > 0
                    ))
                LIMIT 3
            ''', (student_id, student_id))
            ready_to_advance_raw = ready_to_advance_result.fetchall()
            
            # Convert to consistent format
            if ready_to_advance_raw and isinstance(ready_to_advance_raw[0], dict):
                ready_to_advance = ready_to_advance_raw
            else:
                ready_to_advance = [dict(row) for row in ready_to_advance_raw]
            
            return {
                'topic_summaries': topic_summaries_list,
                'detailed_progress': detailed_progress,
                'weak_areas': weak_areas,
                'ready_to_advance': ready_to_advance
            }
    
    @staticmethod
    def get_session_entry_data():
        """Get data needed for session entry form."""
        with get_db() as db:
            # Get all topics with their subtopics and include current progress if student is selected
            topics_result = db.execute('''
                SELECT 
                    mt.id,
                    mt.topic_name,
                    mt.color_code
                FROM main_topics mt
                ORDER BY mt.topic_name
            ''')
            topics = topics_result.fetchall()
            
            topics_with_subtopics = []
            for topic in topics:
                if isinstance(topic, dict):
                    topic_dict = topic
                else:
                    topic_dict = dict(topic)
                    
                subtopics_result = db.execute('''
                    SELECT 
                        s.id,
                        s.subtopic_name,
                        s.difficulty_order
                    FROM subtopics s
                    WHERE s.main_topic_id = ?
                    ORDER BY s.difficulty_order
                ''', (topic_dict['id'],))
                subtopics = subtopics_result.fetchall()
                
                # Convert Row objects to dictionaries
                subtopic_list = []
                for sub in subtopics:
                    if isinstance(sub, dict):
                        sub_dict = sub
                    else:
                        sub_dict = dict(sub)
                        
                    subtopic_list.append({
                        'id': sub_dict['id'],
                        'subtopic_name': sub_dict['subtopic_name'],
                        'difficulty_order': sub_dict['difficulty_order']
                    })
                
                topics_with_subtopics.append({
                    'id': topic_dict['id'],
                    'topic_name': topic_dict['topic_name'],
                    'color_code': topic_dict['color_code'],
                    'subtopics': subtopic_list
                })
            
            return topics_with_subtopics
    
    @staticmethod
    def get_recent_sessions_with_progress(student_id, limit=5):
        """Get recent sessions with subtopic progress changes."""
        with get_db() as db:
            sessions_result = db.execute('''
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
            ''', (student_id, limit))
            sessions = sessions_result.fetchall()
            
            # For each session, get what subtopics were assessed
            sessions_with_progress = []
            for session in sessions:
                if isinstance(session, dict):
                    session_dict = session
                else:
                    session_dict = dict(session)
                    
                # Format the date here
                from datetime import datetime
                try:
                    # Parse the ISO format datetime
                    dt = datetime.fromisoformat(session_dict['session_date'].replace('T', ' '))
                    formatted_date = dt.strftime('%d-%m-%y @ %H:%M')
                except:
                    # Fallback if parsing fails
                    formatted_date = session_dict['session_date']
                
                # This is approximate - in a real system, you'd track session-subtopic relationships
                subtopics_result = db.execute('''
                    SELECT 
                        s.subtopic_name,
                        sp.mastery_level as new_level
                    FROM subtopic_progress sp
                    JOIN subtopics s ON sp.subtopic_id = s.id
                    WHERE sp.student_id = ? 
                        AND DATE(sp.last_assessed) = DATE(?)
                ''', (student_id, session_dict['session_date']))
                subtopics_assessed_raw = subtopics_result.fetchall()
                
                # Convert to consistent format
                if subtopics_assessed_raw and isinstance(subtopics_assessed_raw[0], dict):
                    subtopics_assessed = subtopics_assessed_raw
                else:
                    subtopics_assessed = [dict(row) for row in subtopics_assessed_raw]
                
                sessions_with_progress.append({
                    **session_dict,
                    'session_date': formatted_date,  # Use formatted date
                    'subtopics_assessed': subtopics_assessed
                })
            
            return sessions_with_progress