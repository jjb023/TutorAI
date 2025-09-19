from flask import Flask
from flask_login import LoginManager
from config import config
import os

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

def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config.get(config_name, config['default']))
    
    print(f"🚀 Starting in {config_name} mode")
    print(f"📂 Database path: {app.config['DATABASE_PATH']}")
    
    # Initialize database with app context
    with app.app_context():
        try:
            from utils.database_init import init_database
            db_path = init_database()
            print(f"✅ Database ready at: {db_path}")
        except Exception as e:
            print(f"❌ Database setup failed: {e}")
            # Continue anyway for demo purposes
    
    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    @login_manager.user_loader
    def load_user(user_id):  # type: ignore
        """Load user from database for Flask-Login"""
        try:
            from utils.db_connection import get_db
            with get_db() as db:
                result = db.execute(
                    "SELECT id, username, full_name, email FROM tutors WHERE id = ? AND active = true",
                    (user_id,)
                ).fetchone()
                
                if result:
                    if isinstance(result, dict):
                        return Tutor(result['id'], result['username'], result['full_name'], result['email'])
                    else:
                        return Tutor(result['id'], result['username'], result['full_name'], result['email'])
        except Exception as e:
            print(f"Error loading user {user_id}: {e}")
        return None
    
    # Register blueprints
    from auth import auth_bp
    from main import main_bp
    
    # Try to import additional blueprints if they exist
    try:
        from student import student_bp
        app.register_blueprint(student_bp)
    except ImportError:
        print("⚠️ Student blueprint not found")
    
    try:
        from tutor import tutor_bp
        app.register_blueprint(tutor_bp)
    except ImportError:
        print("⚠️ Tutor blueprint not found")
    
    try:
        from session import session_bp
        app.register_blueprint(session_bp)
    except ImportError:
        print("⚠️ Session blueprint not found")
    
    try:
        from topic import topic_bp
        app.register_blueprint(topic_bp)
    except ImportError:
        print("⚠️ Topic blueprint not found")
    
    try:
        from worksheet import worksheet_bp
        app.register_blueprint(worksheet_bp)
    except ImportError:
        print("⚠️ Worksheet blueprint not found")
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    
    return app

# Create the app instance for Gunicorn
app = create_app('production' if os.environ.get('FLASK_ENV') == 'production' else 'development')

# Test route for database connectivity
@app.route('/test-db')
def test_db():
    """Test database connection"""
    try:
        from utils.db_connection import get_db
        with get_db() as db:
            result = db.execute("SELECT COUNT(*) as count FROM tutors").fetchone()
            if isinstance(result, dict):
                count = result['count']
            else:
                count = result[0]
            return f"✅ Database connected! Found {count} tutors | <a href='/auth/login'>Login</a>"
    except Exception as e:
        return f"❌ Database error: {e}"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(debug=True, host='0.0.0.0', port=port)