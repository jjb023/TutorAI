# web/student/routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from .services import StudentService
from session.services import SessionService

student_bp = Blueprint('student', __name__, url_prefix='/students')

@student_bp.route('/')
@login_required
def list_students():
    """Show all students with progress indicators."""
    students = StudentService.get_all_students()
    
    # Add progress summary for each student
    students_with_progress = []
    for student in students:
        progress_data = StudentService.get_student_progress_summary(student['id'])
        overall_progress = 0
        topics_assessed = 0
        
        for topic in progress_data['topic_summaries']:
            if topic['assessed_subtopics'] > 0:
                topics_assessed += topic['assessed_subtopics']
                overall_progress += topic['completion_percentage']
        
        if len(progress_data['topic_summaries']) > 0:
            overall_progress = overall_progress / len(progress_data['topic_summaries'])
        
        students_with_progress.append({
            **dict(student),
            'overall_progress': round(overall_progress, 1),
            'topics_assessed': topics_assessed
        })
    
    return render_template('student/list.html', students=students_with_progress)

@student_bp.route('/<int:student_id>')
@login_required
def student_detail(student_id):
    """Show comprehensive student progress report."""
    student = StudentService.get_student(student_id)
    if not student:
        flash('Student not found!', 'error')
        return redirect(url_for('student.list_students'))
    
    # Get comprehensive progress data
    progress_data = SessionService.get_student_progress_summary(student_id)
    
    # Get recent sessions with progress details
    recent_sessions = SessionService.get_recent_sessions_with_progress(student_id)
    
    # Calculate overall statistics
    total_subtopics = sum(topic['total_subtopics'] for topic in progress_data['topic_summaries'])
    topics_assessed = sum(topic['assessed_subtopics'] for topic in progress_data['topic_summaries'])
    
    overall_progress = 0
    if len(progress_data['topic_summaries']) > 0:
        overall_progress = sum(topic['completion_percentage'] for topic in progress_data['topic_summaries']) / len(progress_data['topic_summaries'])
    
    # Get session count
    session_count = StudentService.get_session_count(student_id)
    last_session_date = student['last_session_date']
    
    return render_template('student/detail.html', 
                         student=student,
                         topic_summaries=progress_data['topic_summaries'],
                         detailed_progress=progress_data['detailed_progress'],
                         weak_areas=progress_data['weak_areas'],
                         ready_to_advance=progress_data['ready_to_advance'],
                         recent_sessions=recent_sessions,
                         session_count=session_count,
                         last_session_date=last_session_date,
                         topics_assessed=topics_assessed,
                         total_subtopics=total_subtopics,
                         overall_progress=round(overall_progress, 1))

@student_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_student():
    """Add a new student."""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        age = request.form.get('age')
        year_group = request.form.get('year_group', '').strip()
        target_school = request.form.get('target_school', '').strip() or None
        parent_contact = request.form.get('parent_contact', '').strip() or None
        notes = request.form.get('notes', '').strip() or None
        
        if not name or not age or not year_group:
            flash('Name, age, and year group are required!', 'error')
            return render_template('student/edit.html')
        
        try:
            student_id = StudentService.create_student(name, int(age), year_group, 
                                                     target_school, parent_contact, notes)
            flash(f'Student {name} added successfully!', 'success')
            
            # Offer to do initial assessment
            return redirect(url_for('session.entry', student_id=student_id))
            
        except Exception as e:
            flash(f'Error adding student: {e}', 'error')
    
    return render_template('student/edit.html')

@student_bp.route('/<int:student_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_student(student_id):
    """Edit student details."""
    student = StudentService.get_student(student_id)
    if not student:
        flash('Student not found!', 'error')
        return redirect(url_for('student.list_students'))
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        age = request.form.get('age')
        year_group = request.form.get('year_group', '').strip()
        target_school = request.form.get('target_school', '').strip() or None
        parent_contact = request.form.get('parent_contact', '').strip() or None
        notes = request.form.get('notes', '').strip() or None
        
        if not name or not age or not year_group:
            flash('Name, age, and year group are required!', 'error')
            return render_template('student/edit.html', student=student)
        
        try:
            StudentService.update_student(student_id, name, int(age), year_group,
                                        target_school, parent_contact, notes)
            flash(f'Student {name} updated successfully!', 'success')
            return redirect(url_for('student.student_detail', student_id=student_id))
        except Exception as e:
            flash(f'Error updating student: {e}', 'error')
    
    return render_template('student/edit.html', student=student)

@student_bp.route('/<int:student_id>/delete', methods=['POST'])
@login_required
def delete_student(student_id):
    """Delete student and all related data."""
    student = StudentService.get_student(student_id)
    if not student:
        flash('Student not found!', 'error')
        return redirect(url_for('student.list_students'))
    
    try:
        StudentService.delete_student(student_id)
        flash(f'Student {student["name"]} deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting student: {e}', 'error')
    
    return redirect(url_for('student.list_students'))

@student_bp.route('/<int:student_id>/progress-chart')
@login_required
def progress_chart(student_id):
    """Show visual progress chart for student."""
    student = StudentService.get_student(student_id)
    if not student:
        flash('Student not found!', 'error')
        return redirect(url_for('student.list_students'))
    
    # Get progress data for visualization
    progress_data = SessionService.get_student_progress_summary(student_id)
    
    return render_template('student/progress_chart.html',
                         student=student,
                         progress_data=progress_data)