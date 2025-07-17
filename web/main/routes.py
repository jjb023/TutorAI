from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from utils.database import get_db_connection
from datetime import datetime

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))

@main_bp.route('/dashboard')
@login_required
def dashboard():
    try:
        with get_db_connection() as conn:
            # Get statistics
            total_students = conn.execute('SELECT COUNT(*) FROM students').fetchone()[0]
            total_tutors = conn.execute('SELECT COUNT(*) FROM tutors WHERE active = 1').fetchone()[0]
            
            # Get total topics (main topics)
            total_topics = conn.execute('SELECT COUNT(*) FROM main_topics').fetchone()[0]
            
            # Get recent sessions with tutor names
            recent_sessions = []
            try:
                sessions_data = conn.execute('''
                    SELECT 
                        s.session_date, 
                        s.duration_minutes, 
                        t.full_name as tutor_name
                    FROM sessions s
                    JOIN tutors t ON s.tutor_id = t.id
                    ORDER BY s.session_date DESC
                    LIMIT 3
                ''').fetchall()
                
                # Format the sessions with proper datetime
                for session in sessions_data:
                    # Parse the ISO format datetime
                    dt = datetime.fromisoformat(session['session_date'].replace('T', ' '))
                    formatted_datetime = dt.strftime('%H:%M %d.%m.%Y')
                    
                    recent_sessions.append({
                        'formatted_datetime': formatted_datetime,
                        'duration_minutes': session['duration_minutes'],
                        'tutor_name': session['tutor_name']
                    })
                    
            except Exception as e:
                print(f"Error getting recent sessions: {e}")
        
        stats = {
            'total_students': total_students,
            'total_tutors': total_tutors,
            'total_topics': total_topics
        }
        
        print(f"Dashboard stats: {stats}")
        
        return render_template('dashboard.html', 
                             stats=stats, 
                             recent_sessions=recent_sessions)
    
    except Exception as e:
        print(f"Dashboard error: {e}")
        import traceback
        traceback.print_exc()
        
        # Fallback stats if database has issues
        stats = {
            'total_students': 0,
            'total_tutors': 0,
            'total_topics': 0
        }
        return render_template('dashboard.html', 
                             stats=stats, 
                             recent_sessions=[])