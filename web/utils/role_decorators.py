"""Role-based access control decorators"""

from functools import wraps
from flask import abort, redirect, url_for, flash
from flask_login import current_user
from tutor.services import TutorService

def admin_required(f):
    """Decorator to require admin role for access."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('auth.login'))
        
        # Check if user is admin
        if not TutorService.is_admin(current_user.id):
            flash('Admin access required.', 'error')
            abort(403)
        
        return f(*args, **kwargs)
    return decorated_function

def tutor_or_admin_required(f):
    """Decorator to require tutor or admin role for access."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('auth.login'))
        
        # Any authenticated tutor/admin can access
        return f(*args, **kwargs)
    return decorated_function

def get_current_user_role():
    """Get the current user's role."""
    if not current_user.is_authenticated:
        return None
    
    try:
        tutor = TutorService.get_tutor(current_user.id)
        if tutor:
            if isinstance(tutor, dict):
                return tutor.get('role', 'tutor')
            else:
                # Handle Row object - find role column
                try:
                    return tutor['role']
                except (KeyError, TypeError):
                    return 'tutor'  # Default to tutor if role not found
        return 'tutor'
    except Exception:
        return 'tutor'

def is_current_user_admin():
    """Check if current user is admin."""
    return get_current_user_role() == 'admin'

def can_manage_tutors():
    """Check if current user can manage tutors (admin only)."""
    return is_current_user_admin()

def can_manage_students():
    """Check if current user can manage students (both admin and tutor)."""
    return current_user.is_authenticated

def can_manage_topics():
    """Check if current user can manage topics (both admin and tutor)."""
    return current_user.is_authenticated