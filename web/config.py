# web/config.py
"""
Configuration management for Tutor AI Flask application.
Supports development, testing, and production environments.

Author: Josh Beal
Date: 2025
"""

import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config:
    """Base configuration class with shared settings."""
    
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-please-change-in-production'
    
    # Database
    DATABASE_PATH = os.environ.get('DATABASE_PATH') or '../data/tutor_ai.db'
    
    # Session Configuration
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
    SESSION_COOKIE_NAME = 'tutor_ai_session'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = False  # Override in production
    
    # Security Headers
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None
    
    # File Upload Configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or 'uploads'
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif'}
    
    # Worksheet Generation
    WORKSHEET_OUTPUT_DIR = os.environ.get('WORKSHEET_OUTPUT_DIR') or 'worksheets'
    MAX_QUESTIONS_PER_WORKSHEET = 50
    
    # OpenAI Configuration (for future use)
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    OPENAI_MODEL = os.environ.get('OPENAI_MODEL') or 'gpt-3.5-turbo'
    
    # Application Settings
    ITEMS_PER_PAGE = 20  # Pagination
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'
    
    @staticmethod
    def init_app(app):
        """Initialize application with configuration."""
        # Create necessary directories
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        os.makedirs(app.config['WORKSHEET_OUTPUT_DIR'], exist_ok=True)


class DevelopmentConfig(Config):
    """Development environment configuration."""
    
    DEBUG = True
    TESTING = False
    
    # Development-specific settings
    EXPLAIN_TEMPLATE_LOADING = False
    PRESERVE_CONTEXT_ON_EXCEPTION = True
    
    # More verbose logging in development
    LOG_LEVEL = 'DEBUG'
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # Development-specific initialization
        print("🔧 Running in DEVELOPMENT mode")
        print(f"📁 Database: {app.config['DATABASE_PATH']}")


class ProductionConfig(Config):
    """Production environment configuration."""
    
    DEBUG = False
    TESTING = False
    
    # Enhanced security in production
    SESSION_COOKIE_SECURE = True  # Requires HTTPS
    
    # Production database path
    DATABASE_PATH = os.environ.get('DATABASE_PATH') or '/var/data/tutor_ai.db'
    
    # Stricter settings
    WTF_CSRF_ENABLED = True
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # Production logging
        import logging
        from logging.handlers import RotatingFileHandler
        
        if not app.debug and not app.testing:
            # Set up file logging
            if not os.path.exists('logs'):
                os.mkdir('logs')
            
            file_handler = RotatingFileHandler(
                'logs/tutor_ai.log',
                maxBytes=10240000,  # 10MB
                backupCount=10
            )
            
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s '
                '[in %(pathname)s:%(lineno)d]'
            ))
            
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)
            
            app.logger.setLevel(logging.INFO)
            app.logger.info('Tutor AI startup')


class TestingConfig(Config):
    """Testing environment configuration."""
    
    TESTING = True
    DEBUG = False
    
    # Use in-memory database for tests
    DATABASE_PATH = ':memory:'
    
    # Disable CSRF for testing
    WTF_CSRF_ENABLED = False
    
    # Disable login requirement for testing
    LOGIN_DISABLED = True
    
    # Fast password hashing for tests
    BCRYPT_LOG_ROUNDS = 4
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        print("🧪 Running in TESTING mode")


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config():
    """Get configuration based on environment variable."""
    env = os.environ.get('FLASK_ENV') or 'development'
    return config.get(env) or config['default']