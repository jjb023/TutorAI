from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from .services import SessionService
from student.services import StudentService
from tutor.services import TutorService

session_bp = Blueprint('session', __name__, url_prefix='/sessions')

@session_bp.route('/')
@login_required
def list_sessions():
    """List all sessions."""
    sessions = SessionService.get_all_sessions()
    stats = SessionService.get_session_stats()
    return render_template('session/list.html', sessions=sessions, stats=stats)

@session_bp.route('/entry')
@login_required
def entry():
    """Session entry form."""
    students = StudentService.get_all_students()
    tutors = TutorService.get_all_tutors()
    
    # Get student_id from query params if provided
    selected_student_id = request.args.get('student_id', type=int)
    
    return render_template('session/entry.html', 
                         students=students, 
                         tutors=tutors,
                         selected_student_id=selected_student_id)

@session_bp.route('/create', methods=['POST'])
@login_required
def create_session():
    """Create a new session."""
    student_id = request.form.get('student_id', type=int)
    tutor_id = request.form.get('tutor_id', type=int)
    duration = request.form.get('duration', type=int)
    progress_score = request.form.get('progress_score', type=int)
    notes = request.form.get('notes', '').strip()
    
    # Validation
    if not all([student_id, tutor_id, duration, progress_score]):
        flash('All fields except notes are required!', 'error')
        return redirect(url_for('session.entry'))
    
    if not (1 <= progress_score <= 10):
        flash('Progress score must be between 1 and 10!', 'error')
        return redirect(url_for('session.entry'))
    
    if duration <= 0:
        flash('Duration must be positive!', 'error')
        return redirect(url_for('session.entry'))
    
    try:
        SessionService.create_session(student_id, tutor_id, duration, progress_score, notes or None)
        
        # Get student name for success message
        student = StudentService.get_student(student_id)
        student_name = student.name if student else "Student"
        
        flash(f'Session recorded for {student_name}!', 'success')
        return redirect(url_for('student.student_detail', student_id=student_id))
    except Exception as e:
        flash(f'Error creating session: {e}', 'error')
        return redirect(url_for('session.entry'))