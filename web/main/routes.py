from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from utils.database import get_db_connection

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))

@main_bp.route('/dashboard')
@login_required
def dashboard():
    with get_db_connection() as conn:
        # Get statistics
        total_students = conn.execute('SELECT COUNT(*) FROM students').fetchone()[0]
        total_tutors = conn.execute('SELECT COUNT(*) FROM tutors').fetchone()[0]
        total_sessions = conn.execute('SELECT COUNT(*) FROM sessions').fetchone()[0]
        
        # Get recent sessions
        recent_sessions = conn.execute('''
            SELECT s.date, s.duration, s.progress_score, st.name as student_name, t.name as tutor_name
            FROM sessions s
            JOIN students st ON s.student_id = st.id
            JOIN tutors t ON s.tutor_id = t.id
            ORDER BY s.date DESC
            LIMIT 5
        ''').fetchall()
        
        # Get progress trends (last 10 sessions)
        progress_data = conn.execute('''
            SELECT date, progress_score 
            FROM sessions 
            ORDER BY date DESC 
            LIMIT 10
        ''').fetchall()
    
    stats = {
        'total_students': total_students,
        'total_tutors': total_tutors,
        'total_sessions': total_sessions
    }
    
    return render_template('dashboard.html', 
                         stats=stats, 
                         recent_sessions=recent_sessions,
                         progress_data=list(reversed(progress_data)))