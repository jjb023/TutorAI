# web/utils/decorators.py
"""
Decorators and helper functions for Tutor AI Flask application.
Provides reusable decorators for validation, caching, and performance.

Author: Josh Beal
Date: 2025
"""

from functools import wraps, lru_cache
from flask import abort, flash, redirect, url_for, request, g
from flask_login import current_user
import time
import logging

logger = logging.getLogger(__name__)


def validate_id(param_name='id'):
    """
    Decorator to validate numeric IDs in route parameters.
    
    Args:
        param_name: Name of the parameter to validate (default: 'id')
    
    Usage:
        @app.route('/student/<int:student_id>')
        @validate_id('student_id')
        def view_student(student_id):
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check if the parameter exists in kwargs
            if param_name in kwargs:
                try:
                    id_value = int(kwargs[param_name])
                    if id_value <= 0:
                        flash('Invalid ID provided', 'error')
                        abort(400)
                except (ValueError, TypeError):
                    flash('Invalid ID format', 'error')
                    abort(400)
            
            # Also check for any parameter ending with '_id'
            for key, value in kwargs.items():
                if key.endswith('_id') and key != param_name:
                    try:
                        if int(value) <= 0:
                            flash(f'Invalid {key}', 'error')
                            abort(400)
                    except (ValueError, TypeError):
                        flash(f'Invalid {key} format', 'error')
                        abort(400)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    """
    Decorator to restrict access to admin users only.
    
    Usage:
        @app.route('/admin/settings')
        @login_required
        @admin_required
        def admin_settings():
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'info')
            return redirect(url_for('auth.login'))
        
        if current_user.username != 'admin':
            flash('Admin access required for this action.', 'error')
            return redirect(url_for('main.dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function


def tutor_required(f):
    """
    Decorator to ensure user is an authenticated tutor.
    More lenient than admin_required - allows any authenticated tutor.
    
    Usage:
        @app.route('/sessions/new')
        @tutor_required
        def new_session():
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'info')
            return redirect(url_for('auth.login', next=request.url))
        
        # Could add additional tutor-specific checks here
        # For example, checking if tutor account is active
        
        return f(*args, **kwargs)
    return decorated_function


def measure_performance(f):
    """
    Decorator to measure and log function execution time.
    Useful for identifying performance bottlenecks.
    
    Usage:
        @measure_performance
        def slow_function():
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        
        # Store start time in g for access in templates
        g.start_time = start_time
        
        result = f(*args, **kwargs)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Log if execution takes more than 1 second
        if execution_time > 1.0:
            logger.warning(
                f"Slow function: {f.__name__} took {execution_time:.2f} seconds"
            )
        else:
            logger.debug(
                f"Function {f.__name__} executed in {execution_time:.3f} seconds"
            )
        
        # Store execution time for potential display
        g.execution_time = execution_time
        
        return result
    return decorated_function


def cache_result(timeout=300):
    """
    Decorator to cache function results for a specified time.
    Uses Flask's cache or a simple in-memory cache.
    
    Args:
        timeout: Cache timeout in seconds (default: 5 minutes)
    
    Usage:
        @cache_result(timeout=600)  # Cache for 10 minutes
        def get_expensive_data():
            ...
    """
    def decorator(f):
        # Use lru_cache for simplicity - in production, use Flask-Caching
        cached_func = lru_cache(maxsize=128)(f)
        
        @wraps(f)
        def decorated_function(*args, **kwargs):
            return cached_func(*args, **kwargs)
        
        # Add method to clear cache if needed
        decorated_function.cache_clear = cached_func.cache_clear
        decorated_function.cache_info = cached_func.cache_info
        
        return decorated_function
    return decorator


def validate_form_data(*required_fields):
    """
    Decorator to validate that required form fields are present.
    
    Args:
        *required_fields: Names of required form fields
    
    Usage:
        @app.route('/submit', methods=['POST'])
        @validate_form_data('name', 'email', 'message')
        def submit_form():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if request.method == 'POST':
                missing_fields = []
                
                for field in required_fields:
                    if not request.form.get(field, '').strip():
                        missing_fields.append(field)
                
                if missing_fields:
                    flash(
                        f"Missing required fields: {', '.join(missing_fields)}", 
                        'error'
                    )
                    # Return to previous page or form
                    return redirect(request.referrer or url_for('main.dashboard'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def log_activity(action_type):
    """
    Decorator to log user activities for audit purposes.
    
    Args:
        action_type: Type of action being performed (e.g., 'create_student', 'delete_session')
    
    Usage:
        @app.route('/student/add', methods=['POST'])
        @log_activity('create_student')
        def add_student():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Log the action before execution
            user_id = current_user.id if current_user.is_authenticated else 'anonymous'
            logger.info(
                f"Action: {action_type} | User: {user_id} | "
                f"IP: {request.remote_addr} | Path: {request.path}"
            )
            
            try:
                result = f(*args, **kwargs)
                
                # Log successful completion
                logger.info(f"Action completed: {action_type} | User: {user_id}")
                
                return result
                
            except Exception as e:
                # Log any errors
                logger.error(
                    f"Action failed: {action_type} | User: {user_id} | Error: {str(e)}"
                )
                raise
        
        return decorated_function
    return decorator


def prevent_duplicate_submission(timeout=5):
    """
    Decorator to prevent duplicate form submissions.
    Uses session to track recent submissions.
    
    Args:
        timeout: Seconds to wait before allowing resubmission (default: 5)
    
    Usage:
        @app.route('/submit', methods=['POST'])
        @prevent_duplicate_submission(timeout=10)
        def submit_form():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if request.method == 'POST':
                # Create a unique key for this form submission
                form_key = f"{f.__name__}_{request.path}"
                
                # Check if this form was recently submitted
                from flask import session
                last_submission = session.get(f'last_submission_{form_key}', 0)
                current_time = time.time()
                
                if current_time - last_submission < timeout:
                    remaining = timeout - (current_time - last_submission)
                    flash(
                        f'Please wait {remaining:.0f} seconds before resubmitting.', 
                        'warning'
                    )
                    return redirect(request.referrer or url_for('main.dashboard'))
                
                # Update last submission time
                session[f'last_submission_{form_key}'] = current_time
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def handle_errors(default_message="An error occurred"):
    """
    Decorator to handle exceptions gracefully and show user-friendly messages.
    
    Args:
        default_message: Default error message to show users
    
    Usage:
        @app.route('/risky-operation')
        @handle_errors("Unable to complete operation")
        def risky_operation():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except ValidationError as e:
                # Handle validation errors specifically
                flash(f"Validation error: {str(e)}", 'error')
                return redirect(request.referrer or url_for('main.dashboard'))
            except DatabaseError as e:
                # Handle database errors
                logger.error(f"Database error in {f.__name__}: {str(e)}")
                flash("Database error occurred. Please try again later.", 'error')
                return redirect(url_for('main.dashboard'))
            except Exception as e:
                # Handle any other errors
                logger.error(f"Unexpected error in {f.__name__}: {str(e)}")
                flash(default_message, 'error')
                return redirect(url_for('main.dashboard'))
        
        return decorated_function
    return decorator


# Import these for the handle_errors decorator
class ValidationError(Exception):
    """Custom validation error"""
    pass

class DatabaseError(Exception):
    """Custom database error"""
    pass