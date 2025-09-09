from flask import Flask
from flask_login import LoginManager
from config import config
from utils.database import init_app as init_db
import sys
import os

# Add the parent directory to the path so we can import our database
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import TutorAIDatabase

# Simple User class for Flask-Login (using your existing system)
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

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        """Load user for Flask-Login using your existing database"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(os.path.dirname(current_dir), 'data', 'tutor_ai.db')
        db = TutorAIDatabase(db_path)
        try:
            db.cursor.execute("SELECT id, username, full_name, email FROM tutors WHERE id = ? AND active = 1", (user_id,))
            tutor_data = db.cursor.fetchone()
            if tutor_data:
                return Tutor(tutor_data[0], tutor_data[1], tutor_data[2], tutor_data[3])
        finally:
            db.close()
        return None
    
    # Initialize database
    init_db(app)
    
    # Register blueprints
    from auth import auth_bp
    from main import main_bp
    from student import student_bp
    from tutor import tutor_bp
    from session import session_bp
    from topic import topic_bp
    from worksheet import worksheet_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(tutor_bp)
    app.register_blueprint(session_bp)
    app.register_blueprint(topic_bp)
    app.register_blueprint(worksheet_bp)
    
    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    print("🚀 Starting Tutor AI Flask App...")
    print("📱 Access from other devices on your network:")
    print("   Find your IP address and use: http://YOUR_IP:5001")
    print("🌐 Local access: http://localhost:5001")
    print("⚠️  Press Ctrl+C to stop the server")
    app.run(debug=True, host='0.0.0.0', port=port)