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
    
    # Database - Use environment variable or default
    DATABASE_PATH = os.environ.get('DATABASE_PATH') or '../data/tutor_ai.db'
    
    # Session Configuration
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
    SESSION_COOKIE_NAME = 'tutor_ai_session'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = False  # Override in production

class DevelopmentConfig(Config):
    """Development environment configuration."""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production environment configuration."""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True  # Requires HTTPS in production

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}