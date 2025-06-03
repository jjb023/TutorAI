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
    try:
        with get_db_connection() as conn:
            # First, let's see what tables exist
            tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
            print("Available tables:", [table[0] for table in tables])
            
            # Get statistics using your existing database structure
            total_students = conn.execute('SELECT COUNT(*) FROM students').fetchone()[0]
            total_tutors = conn.execute('SELECT COUNT(*) FROM tutors WHERE active = 1').fetchone()[0]
            
            # Check if sessions table exists and has data
            try:
                total_sessions = conn.execute('SELECT COUNT(*) FROM sessions').fetchone()[0]
            except:
                total_sessions = 0
            
            # Try to get recent sessions
            recent_sessions = []
            try:
                recent_sessions = conn.execute('''
                    SELECT s.session_date, s.duration_minutes, st.name as student_name
                    FROM sessions s
                    JOIN students st ON s.student_id = st.id
                    ORDER BY s.session_date DESC
                    LIMIT 5
                ''').fetchall()
            except Exception as e:
                print(f"Error getting recent sessions: {e}")
        
        stats = {
            'total_students': total_students,
            'total_tutors': total_tutors,
            'total_sessions': total_sessions
        }
        
        print(f"Dashboard stats: {stats}")
        
        return render_template('dashboard.html', 
                             stats=stats, 
                             recent_sessions=recent_sessions,
                             progress_data=[])
    
    except Exception as e:
        print(f"Dashboard error: {e}")
        import traceback
        traceback.print_exc()
        
        # Fallback stats if database has issues
        stats = {
            'total_students': 0,
            'total_tutors': 0,
            'total_sessions': 0
        }
        return render_template('dashboard.html', 
                             stats=stats, 
                             recent_sessions=[],
                             progress_data=[])