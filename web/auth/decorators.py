from functools import wraps
from flask import redirect, url_for, flash, abort
from flask_login import current_user

def admin_required(f):
    """Decorator to require admin privileges."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('auth.login'))
        
        if not current_user.is_admin:
            flash('Admin privileges required.', 'error')
            abort(403)
        
        return f(*args, **kwargs)
    return decorated_function