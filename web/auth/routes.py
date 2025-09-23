from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required
import sys
import os
from werkzeug.security import check_password_hash, generate_password_hash

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.db_connection import get_db

# Simple User class for Flask-Login
class Tutor:
    def __init__(self, id, username, full_name, email, role='tutor'):
        self.id = id
        self.username = username
        self.full_name = full_name
        self.email = email
        self.role = role
        self.is_authenticated = True
        self.is_active = True
        self.is_anonymous = False

    def get_id(self):
        return str(self.id)
    
    def is_admin(self):
        return self.role == 'admin'

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

def verify_tutor_login(username, password):
    """Verify tutor login using database connection wrapper"""
    
    with get_db() as db:
        try:
            # Query for tutor
            result = db.execute("""
                SELECT id, username, full_name, email, password_hash, role 
                FROM tutors 
                WHERE username = ? AND active = true
            """, (username,)).fetchone()
            
            if result:
                # Handle both dict (PostgreSQL) and Row (SQLite) objects
                if isinstance(result, dict):
                    tutor_id = result['id']
                    tutor_username = result['username']
                    tutor_fullname = result['full_name']
                    tutor_email = result['email']
                    tutor_role = result.get('role', 'tutor')
                    stored_hash = result.get('password_hash')
                else:
                    # SQLite Row object
                    tutor_id = result['id']
                    tutor_username = result['username']
                    tutor_fullname = result['full_name']
                    tutor_email = result['email']
                    tutor_role = result['role'] if 'role' in result.keys() else 'tutor'
                    stored_hash = result['password_hash'] if 'password_hash' in result.keys() else None
                
                # Verify password
                if stored_hash and stored_hash != 'temp_password_hash':
                    if check_password_hash(stored_hash, password):
                        # Update last login
                        db.execute(
                            "UPDATE tutors SET last_login = CURRENT_TIMESTAMP WHERE id = ?",
                            (tutor_id,)
                        )
                        return Tutor(tutor_id, tutor_username, tutor_fullname, tutor_email, tutor_role)
                
                # For initial setup only (when SETUP_MODE=true)
                elif os.getenv('SETUP_MODE', 'false').lower() == 'true':
                    # Check against environment variables for demo accounts
                    env_passwords = {
                        'admin': os.getenv('ADMIN_PASSWORD', 'admin123'),
                        'tutor1': os.getenv('TUTOR1_PASSWORD', 'password'),
                        'tutor2': os.getenv('TUTOR2_PASSWORD', 'password')
                    }
                    
                    default_password = os.getenv('DEFAULT_TUTOR_PASSWORD', 'password')
                    
                    if (password == env_passwords.get(username) or 
                        (username not in env_passwords and password == default_password)):
                        
                        # Hash and store the password for future use
                        hashed = generate_password_hash(password)
                        db.execute(
                            "UPDATE tutors SET password_hash = ? WHERE id = ?",
                            (hashed, tutor_id)
                        )
                        
                        # Update last login
                        db.execute(
                            "UPDATE tutors SET last_login = CURRENT_TIMESTAMP WHERE id = ?",
                            (tutor_id,)
                        )
                        
                        return Tutor(tutor_id, tutor_username, tutor_fullname, tutor_email, tutor_role)
        
        except Exception as e:
            print(f"Login error: {e}")
            return None
    
    return None

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login route"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('Please enter both username and password.', 'error')
        else:
            tutor = verify_tutor_login(username, password)
            if tutor:
                login_user(tutor)
                flash(f'Welcome back, {tutor.full_name}!', 'success')
                next_page = request.args.get('next')
                return redirect(next_page or url_for('main.dashboard'))
            else:
                flash('Invalid username or password.', 'error')
    
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """Logout route"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))