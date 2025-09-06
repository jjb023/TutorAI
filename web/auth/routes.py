from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
import sys
import os
from werkzeug.security import check_password_hash, generate_password_hash

# Add the parent directory to the path so we can import our database
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from database import TutorAIDatabase

# Simple User class for Flask-Login
class Tutor:
    def __init__(self, id, username, full_name, email):
        self.id = id
        self.username = username
        self.full_name = full_name
        self.email = email
        self.is_authenticated = True
        self.is_active = True
        self.is_anonymous = False

    def get_id(self):
        return str(self.id)

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

def verify_tutor_login(username, password):
    """Secure password verification using environment variables and hashing"""
    current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    db_path = os.path.join(current_dir, 'data', 'tutor_ai.db')
    db = TutorAIDatabase(db_path)
    
    try:
        # First check if password_hash exists in database
        db.cursor.execute("""
            SELECT id, username, full_name, email, password_hash 
            FROM tutors 
            WHERE username = ? AND active = 1
        """, (username,))
        tutor_data = db.cursor.fetchone()
        
        if tutor_data:
            stored_hash = tutor_data[4] if len(tutor_data) > 4 else None
            
            # If hash exists, use proper verification
            if stored_hash and stored_hash != 'temp_password_hash':
                if check_password_hash(stored_hash, password):
                    # Update last login and return tutor
                    db.cursor.execute(
                        "UPDATE tutors SET last_login = CURRENT_TIMESTAMP WHERE id = ?", 
                        (tutor_data[0],)
                    )
                    db.connection.commit()
                    return Tutor(tutor_data[0], tutor_data[1], tutor_data[2], tutor_data[3])
            
            # For initial setup only (when SETUP_MODE=true)
            elif os.getenv('SETUP_MODE', 'false').lower() == 'true':
                # Check against environment variables for demo accounts
                env_passwords = {
                    'admin': os.getenv('ADMIN_PASSWORD'),
                    'tutor1': os.getenv('TUTOR1_PASSWORD'),
                    'tutor2': os.getenv('TUTOR2_PASSWORD')
                }
                
                default_password = os.getenv('DEFAULT_TUTOR_PASSWORD')
                
                if (password == env_passwords.get(username) or 
                    (username not in env_passwords and password == default_password)):
                    
                    # Hash and store the password for future use
                    hashed = generate_password_hash(password)
                    db.cursor.execute(
                        "UPDATE tutors SET password_hash = ? WHERE id = ?",
                        (hashed, tutor_data[0])
                    )
                    db.connection.commit()
                    
                    # Update last login
                    db.cursor.execute(
                        "UPDATE tutors SET last_login = CURRENT_TIMESTAMP WHERE id = ?",
                        (tutor_data[0],)
                    )
                    db.connection.commit()
                    
                    return Tutor(tutor_data[0], tutor_data[1], tutor_data[2], tutor_data[3])
    finally:
        db.close()
    
    return None

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
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
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))