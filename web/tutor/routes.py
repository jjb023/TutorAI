from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from .services import TutorService
from utils.role_decorators import admin_required

tutor_bp = Blueprint('tutor', __name__, url_prefix='/tutors')

@tutor_bp.route('/')
@login_required
def list_tutors():
    """Show all tutors with or without management options."""
    view_only = request.args.get('view_only', 'false').lower() == 'true'
    
    tutors = TutorService.get_all_tutors()
    return render_template('tutor/list.html', tutors=tutors, view_only=view_only)

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
@admin_required
def add_tutor():
    """Add a new tutor (admin only)"""
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip().lower()
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip() or None
        password = request.form.get('password', '').strip()
        role = request.form.get('role', 'tutor')  # Get role from form
        
        if not username or not full_name or not password:
            flash('Username, full name, and password are required!', 'error')
            return render_template('tutor/edit.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters!', 'error')
            return render_template('tutor/edit.html')
        
        try:
            TutorService.create_tutor(username, full_name, email, password, role)
            flash(f'Tutor {full_name} added successfully with {role} role!', 'success')
            return redirect(url_for('tutor.list_tutors'))
        except Exception as e:
            flash(f'Error adding tutor: {e}', 'error')
    
    return render_template('tutor/edit.html')

@tutor_bp.route('/<int:tutor_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_tutor(tutor_id):
    """Edit tutor details (admin only)"""
    tutor = TutorService.get_tutor(tutor_id)
    if not tutor:
        flash('Tutor not found!', 'error')
        return redirect(url_for('tutor.list_tutors'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip().lower()
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip() or None
        role = request.form.get('role', 'tutor')  # Get role from form
        
        if not username or not full_name:
            flash('Username and full name are required!', 'error')
            return render_template('tutor/edit.html', tutor=tutor)
        
        # Get current tutor data to check role
        if isinstance(tutor, dict):
            current_username = tutor['username']
            current_role = tutor.get('role', 'tutor')
        else:
            current_username = tutor[1]
            current_role = tutor[5] if len(tutor) > 5 else 'tutor'
        
        try:
            TutorService.update_tutor(tutor_id, username, full_name, email, role)
            
            # Show different messages based on role change
            if current_role != role:
                flash(f'Tutor {full_name} updated successfully! Role changed from {current_role} to {role}.', 'success')
            else:
                flash(f'Tutor {full_name} updated successfully!', 'success')
            
            return redirect(url_for('tutor.tutor_detail', tutor_id=tutor_id))
        except Exception as e:
            flash(f'Error updating tutor: {e}', 'error')
    
    return render_template('tutor/edit.html', tutor=tutor)

@tutor_bp.route('/<int:tutor_id>/delete', methods=['POST'])
@admin_required
def delete_tutor(tutor_id):
    """Delete tutor (admin only)"""
    
    tutor = TutorService.get_tutor(tutor_id)
    if not tutor:
        flash('Tutor not found!', 'error')
        return redirect(url_for('tutor.list_tutors'))
    
    # Get username from tutor data
    if isinstance(tutor, dict):
        tutor_username = tutor['username']
        tutor_name = tutor['full_name']
    else:
        tutor_username = tutor[1]
        tutor_name = tutor[2]
    
    if tutor_username == 'admin':
        flash('Cannot delete admin account!', 'error')
        return redirect(url_for('tutor.list_tutors'))
    
    try:
        TutorService.delete_tutor(tutor_id)
        flash(f'Tutor {tutor_name} deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting tutor: {e}', 'error')
    
    return redirect(url_for('tutor.list_tutors'))