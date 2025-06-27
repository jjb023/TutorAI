# web/session/routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from .services import SessionService
from student.services import StudentService
from tutor.services import TutorService

session_bp = Blueprint('session', __name__, url_prefix='/sessions')

@session_bp.route('/entry')
@login_required
def entry():
    """Enhanced session entry form with topic assessment."""
    students = StudentService.get_all_students()
    tutors = TutorService.get_all_tutors()
    
    # Get student_id from query params if provided
    selected_student_id = request.args.get('student_id', type=int)
    
    # Get all topics with subtopics
    topics = SessionService.get_session_entry_data()
    
    # If a student is selected, get their current progress
    if selected_student_id:
        for topic in topics:
            for subtopic in topic['subtopics']:
                # Add current mastery level for each subtopic
                progress = StudentService.get_subtopic_progress(selected_student_id, subtopic['id'])
                subtopic['current_level'] = progress['mastery_level'] if progress else 0
    
    return render_template('session/entry.html', 
                         students=students, 
                         tutors=tutors,
                         topics=topics,
                         selected_student_id=selected_student_id)

@session_bp.route('/create', methods=['POST'])
@login_required
def create_session():
    """Create a new session with subtopic progress updates."""
    student_id = request.form.get('student_id', type=int)
    tutor_id = current_user.id  # Use logged-in tutor
    duration_minutes = request.form.get('duration_minutes', type=int) or 60
    session_notes = request.form.get('session_notes', '').strip()
    
    # Validation
    if not student_id:
        flash('Please select a student!', 'error')
        return redirect(url_for('session.entry'))
    
    # Process subtopic assessments
    subtopic_assessments = {}
    assessed_subtopics = request.form.getlist('assess_subtopic')
    
    for subtopic_id in assessed_subtopics:
        level = request.form.get(f'subtopic_{subtopic_id}', type=int)
        notes = request.form.get(f'notes_{subtopic_id}', '').strip()
        
        if level:
            subtopic_assessments[int(subtopic_id)] = {
                'level': level,
                'notes': notes
            }
    
    if not subtopic_assessments:
        flash('Please assess at least one subtopic!', 'error')
        return redirect(url_for('session.entry', student_id=student_id))
    
    try:
        # Create session and update progress
        SessionService.create_session_with_progress(
            student_id, tutor_id, duration_minutes, 
            subtopic_assessments, session_notes
        )
        
        # Get student name for success message
        student = StudentService.get_student(student_id)
        student_name = student.name if student else "Student"
        
        flash(f'Session recorded for {student_name} with {len(subtopic_assessments)} topics assessed!', 'success')
        return redirect(url_for('student.student_detail', student_id=student_id))
        
    except Exception as e:
        print(f"Error creating session: {e}")
        flash(f'Error creating session: {e}', 'error')
        return redirect(url_for('session.entry'))

@session_bp.route('/quick-update/<int:student_id>')
@login_required
def quick_update(student_id):
    """Quick subtopic update without full session."""
    student = StudentService.get_student(student_id)
    if not student:
        flash('Student not found!', 'error')
        return redirect(url_for('student.list_students'))
    
    topics = SessionService.get_session_entry_data()
    
    # Add current progress for each subtopic
    for topic in topics:
        for subtopic in topic['subtopics']:
            progress = StudentService.get_subtopic_progress(student_id, subtopic['id'])
            subtopic['current_level'] = progress['mastery_level'] if progress else 0
    
    return render_template('session/quick_update.html',
                         student=student,
                         topics=topics)