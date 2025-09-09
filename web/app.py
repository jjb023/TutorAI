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
    def load_user(user_id):
        # Simple demo users for now
        demo_users = {
            '1': Tutor(1, 'admin', 'Administrator', 'admin@tutorai.demo'),
            '2': Tutor(2, 'tutor1', 'Demo Tutor 1', 'tutor1@tutorai.demo'),
            '3': Tutor(3, 'demo', 'Demo User', 'demo@tutorai.demo')
        }
        return demo_users.get(user_id)
    
    # Register blueprints
    from auth import auth_bp
    from main import main_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    
    return app

# Create the app instance for Gunicorn
app = create_app('production' if os.environ.get('FLASK_ENV') == 'production' else 'development')

# Add this route to your app.py for testing
@app.route('/test-login')
def test_login():
    """Test login without form"""
    from auth.routes import verify_tutor_login, Tutor
    from flask_login import login_user
    
    # Try to login admin directly
    tutor = verify_tutor_login('admin', 'admin123')
    if tutor:
        login_user(tutor)
        return f"✅ Login successful! User: {tutor.full_name} | <a href='/dashboard'>Go to Dashboard</a>"
    else:
        return "❌ Login failed!"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(debug=True, host='0.0.0.0', port=port)