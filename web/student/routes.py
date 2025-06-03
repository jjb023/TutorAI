from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from .services import StudentService

student_bp = Blueprint('student', __name__, url_prefix='/students')

@student_bp.route('/')
@login_required
def list_students():
    """Show all students"""
    students = StudentService.get_all_students()
    return render_template('student/list.html', students=students)

@student_bp.route('/<int:student_id>')
@login_required
def student_detail(student_id):
    """Show detailed progress for a specific student"""
    student = StudentService.get_student(student_id)
    if not student:
        flash('Student not found!', 'error')
        return redirect(url_for('student.list_students'))
    
    sessions = StudentService.get_student_sessions(student_id)
    return render_template('student/detail.html', student=student, sessions=sessions)

@student_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_student():
    """Add a new student"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        age = request.form.get('age')
        contact_info = request.form.get('contact_info', '').strip()
        
        if not name or not age:
            flash('Name and age are required!', 'error')
            return render_template('student/edit.html')
        
        try:
            StudentService.create_student(name, int(age), contact_info)
            flash(f'Student {name} added successfully!', 'success')
            return redirect(url_for('student.list_students'))
        except Exception as e:
            flash(f'Error adding student: {e}', 'error')
    
    return render_template('student/edit.html')

@student_bp.route('/<int:student_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_student(student_id):
    """Edit student details"""
    student = StudentService.get_student(student_id)
    if not student:
        flash('Student not found!', 'error')
        return redirect(url_for('student.list_students'))
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        age = request.form.get('age')
        contact_info = request.form.get('contact_info', '').strip()
        
        if not name or not age:
            flash('Name and age are required!', 'error')
            return render_template('student/edit.html', student=student)
        
        try:
            StudentService.update_student(student_id, name, int(age), contact_info)
            flash(f'Student {name} updated successfully!', 'success')
            return redirect(url_for('student.student_detail', student_id=student_id))
        except Exception as e:
            flash(f'Error updating student: {e}', 'error')
    
    return render_template('student/edit.html', student=student)

@student_bp.route('/<int:student_id>/delete', methods=['POST'])
@login_required
def delete_student(student_id):
    """Delete student"""
    student = StudentService.get_student(student_id)
    if not student:
        flash('Student not found!', 'error')
        return redirect(url_for('student.list_students'))
    
    try:
        StudentService.delete_student(student_id)
        flash(f'Student {student[1]} deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting student: {e}', 'error')
    
    return redirect(url_for('student.list_students'))