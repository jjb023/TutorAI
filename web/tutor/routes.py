from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from .services import TutorService

tutor_bp = Blueprint('tutor', __name__, url_prefix='/tutors')

@tutor_bp.route('/')
@login_required
def list_tutors():
    """Show all tutors"""
    tutors = TutorService.get_all_tutors()
    return render_template('tutor/list.html', tutors=tutors)

@tutor_bp.route('/<int:tutor_id>')
@login_required
def tutor_detail(tutor_id):
    """Show detailed information for a specific tutor"""
    tutor = TutorService.get_tutor(tutor_id)
    if not tutor:
        flash('Tutor not found!', 'error')
        return redirect(url_for('tutor.list_tutors'))
    
    sessions = TutorService.get_tutor_sessions(tutor_id)
    return render_template('tutor/detail.html', tutor=tutor, sessions=sessions)

@tutor_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_tutor():
    """Add a new tutor (admin only)"""
    if current_user.username != 'admin':
        flash('Admin access required for this action.', 'error')
        return redirect(url_for('tutor.list_tutors'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip().lower()
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip() or None
        password = request.form.get('password', '').strip()
        
        if not username or not full_name or not password:
            flash('Username, full name, and password are required!', 'error')
            return render_template('tutor/edit.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters!', 'error')
            return render_template('tutor/edit.html')
        
        try:
            TutorService.create_tutor(username, full_name, email)
            flash(f'Tutor {full_name} added successfully!', 'success')
            return redirect(url_for('tutor.list_tutors'))
        except Exception as e:
            flash(f'Error adding tutor: {e}', 'error')
    
    return render_template('tutor/edit.html')

@tutor_bp.route('/<int:tutor_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_tutor(tutor_id):
    """Edit tutor details (admin only)"""
    if current_user.username != 'admin':
        flash('Admin access required for this action.', 'error')
        return redirect(url_for('tutor.list_tutors'))
    
    tutor = TutorService.get_tutor(tutor_id)
    if not tutor:
        flash('Tutor not found!', 'error')
        return redirect(url_for('tutor.list_tutors'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip().lower()
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip() or None
        
        if not username or not full_name:
            flash('Username and full name are required!', 'error')
            return render_template('tutor/edit.html', tutor=tutor)
        
        try:
            TutorService.update_tutor(tutor_id, username, full_name, email)
            flash(f'Tutor {full_name} updated successfully!', 'success')
            return redirect(url_for('tutor.tutor_detail', tutor_id=tutor_id))
        except Exception as e:
            flash(f'Error updating tutor: {e}', 'error')
    
    return render_template('tutor/edit.html', tutor=tutor)

@tutor_bp.route('/<int:tutor_id>/delete', methods=['POST'])
@login_required
def delete_tutor(tutor_id):
    """Delete tutor (admin only)"""
    if current_user.username != 'admin':
        flash('Admin access required for this action.', 'error')
        return redirect(url_for('tutor.list_tutors'))
    
    tutor = TutorService.get_tutor(tutor_id)
    if not tutor:
        flash('Tutor not found!', 'error')
        return redirect(url_for('tutor.list_tutors'))
    
    if tutor.username == 'admin':
        flash('Cannot delete admin account!', 'error')
        return redirect(url_for('tutor.list_tutors'))
    
    try:
        TutorService.delete_tutor(tutor_id)
        flash(f'Tutor {tutor.full_name} deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting tutor: {e}', 'error')
    
    return redirect(url_for('tutor.list_tutors'))