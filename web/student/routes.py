# web/student/routes.py - UPDATED WITH VALIDATION
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from .services import StudentService
from session.services import SessionService
from utils.validators import StudentValidator, ValidationError, sanitize_html

student_bp = Blueprint('student', __name__, url_prefix='/students')

@student_bp.route('/')
@login_required
def list_students():
    """Show all students with progress indicators."""
    try:
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
    
    except Exception as e:
        flash(f'Error loading students: {str(e)}', 'error')
        return render_template('student/list.html', students=[])

@student_bp.route('/<int:student_id>')
@login_required
def student_detail(student_id):
    """Show comprehensive student progress report."""
    try:
        # Validate student_id
        if student_id <= 0:
            flash('Invalid student ID', 'error')
            return redirect(url_for('student.list_students'))
        
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
    
    except Exception as e:
        flash(f'Error loading student details: {str(e)}', 'error')
        return redirect(url_for('student.list_students'))

@student_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_student():
    """Add a new student with validation."""
    if request.method == 'POST':
        errors = {}
        
        # Validate required fields
        try:
            name = StudentValidator.validate_name(request.form.get('name', ''))
        except ValidationError as e:
            errors['name'] = str(e)
        
        try:
            age = StudentValidator.validate_age(request.form.get('age'))
        except ValidationError as e:
            errors['age'] = str(e)
        
        try:
            year_group = StudentValidator.validate_year_group(request.form.get('year_group', ''))
        except ValidationError as e:
            errors['year_group'] = str(e)
        
        # Validate optional fields
        target_school = sanitize_html(request.form.get('target_school', '').strip())[:100] or None
        notes = sanitize_html(request.form.get('notes', '').strip())[:500] or None
        
        parent_contact = request.form.get('parent_contact', '').strip() or None
        if parent_contact and '@' in parent_contact:
            try:
                parent_contact = StudentValidator.validate_email(parent_contact)
            except ValidationError as e:
                errors['parent_contact'] = str(e)
        
        # If validation errors, show form again with errors
        if errors:
            for field, error in errors.items():
                flash(f'{field}: {error}', 'error')
            return render_template('student/edit.html', errors=errors, form_data=request.form)
        
        # All validation passed, create student
        try:
            student_id = StudentService.create_student(name, age, year_group, 
                                                     target_school, parent_contact, notes)
            flash(f'Student {name} added successfully!', 'success')
            
            # Offer to do initial assessment
            return redirect(url_for('session.entry', student_id=student_id))
            
        except Exception as e:
            flash(f'Error adding student: {str(e)}', 'error')
            return render_template('student/edit.html', form_data=request.form)
    
    return render_template('student/edit.html')

@student_bp.route('/<int:student_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_student(student_id):
    """Edit student details with validation."""
    # Validate student_id
    if student_id <= 0:
        flash('Invalid student ID', 'error')
        return redirect(url_for('student.list_students'))
    
    student = StudentService.get_student(student_id)
    if not student:
        flash('Student not found!', 'error')
        return redirect(url_for('student.list_students'))
    
    if request.method == 'POST':
        errors = {}
        
        # Validate fields
        try:
            name = StudentValidator.validate_name(request.form.get('name', ''))
        except ValidationError as e:
            errors['name'] = str(e)
        
        try:
            age = StudentValidator.validate_age(request.form.get('age'))
        except ValidationError as e:
            errors['age'] = str(e)
        
        try:
            year_group = StudentValidator.validate_year_group(request.form.get('year_group', ''))
        except ValidationError as e:
            errors['year_group'] = str(e)
        
        # Sanitize optional fields
        target_school = sanitize_html(request.form.get('target_school', '').strip())[:100] or None
        notes = sanitize_html(request.form.get('notes', '').strip())[:500] or None
        
        parent_contact = request.form.get('parent_contact', '').strip() or None
        if parent_contact and '@' in parent_contact:
            try:
                parent_contact = StudentValidator.validate_email(parent_contact)
            except ValidationError as e:
                errors['parent_contact'] = str(e)
        
        if errors:
            for field, error in errors.items():
                flash(f'{field}: {error}', 'error')
            return render_template('student/edit.html', student=student, errors=errors)
        
        try:
            StudentService.update_student(student_id, name, age, year_group,
                                        target_school, parent_contact, notes)
            flash(f'Student {name} updated successfully!', 'success')
            return redirect(url_for('student.student_detail', student_id=student_id))
        except Exception as e:
            flash(f'Error updating student: {str(e)}', 'error')
    
    return render_template('student/edit.html', student=student)

@student_bp.route('/<int:student_id>/delete', methods=['POST'])
@login_required
def delete_student(student_id):
    """Delete student and all related data."""
    # Validate student_id
    if student_id <= 0:
        flash('Invalid student ID', 'error')
        return redirect(url_for('student.list_students'))
    
    student = StudentService.get_student(student_id)
    if not student:
        flash('Student not found!', 'error')
        return redirect(url_for('student.list_students'))
    
    try:
        # Confirm deletion with session check
        confirm = request.form.get('confirm_delete', '')
        if confirm != 'yes':
            flash('Deletion not confirmed', 'warning')
            return redirect(url_for('student.student_detail', student_id=student_id))
        
        StudentService.delete_student(student_id)
        flash(f'Student {student["name"]} deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting student: {str(e)}', 'error')
    
    return redirect(url_for('student.list_students'))

@student_bp.route('/<int:student_id>/progress-chart')
@login_required
def progress_chart(student_id):
    """Show visual progress chart for student."""
    # Validate student_id
    if student_id <= 0:
        flash('Invalid student ID', 'error')
        return redirect(url_for('student.list_students'))
    
    student = StudentService.get_student(student_id)
    if not student:
        flash('Student not found!', 'error')
        return redirect(url_for('student.list_students'))
    
    try:
        # Get progress data for visualization
        progress_data = SessionService.get_student_progress_summary(student_id)
        
        return render_template('student/progress_chart.html',
                             student=student,
                             progress_data=progress_data)
    except Exception as e:
        flash(f'Error loading progress chart: {str(e)}', 'error')
        return redirect(url_for('student.student_detail', student_id=student_id))