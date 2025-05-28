import os

class Config:
    # Database configuration
    DATABASE_PATH = os.path.join('data', 'tutor_ai.db')
    
    # Future: Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-change-in-production'
    
    # Future: OpenAI API
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    
    # Application settings
    DEBUG = True
    TESTING = False