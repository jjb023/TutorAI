import os
from datetime import timedelta

class Config:
    # Database
    DATABASE_PATH = 'ai_tutor.db'
    
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-change-in-production'
    
    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
    
    # Security
    WTF_CSRF_ENABLED = True
    
    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}