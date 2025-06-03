from flask import Flask
from flask_login import LoginManager
from config import config
from utils.database import init_app as init_db, init_db as create_tables
from auth.models import User

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
        return User.get(int(user_id))
    
    # Initialize database
    init_db(app)
    
    # Register blueprints
    from auth import auth_bp
    from main import main_bp
    from student import student_bp
    from tutor import tutor_bp
    from session import session_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(tutor_bp)
    app.register_blueprint(session_bp)
    
    # Create tables and default admin user
    with app.app_context():
        create_tables()
        
        # Create default admin user if it doesn't exist
        admin_user = User.get_by_username('admin')
        if not admin_user:
            User.create('admin', 'admin123', is_admin=True)
            print("Default admin user created: admin/admin123")
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)