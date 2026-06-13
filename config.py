import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-dev-key')
    
    # Database configuration placeholders
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI', 'sqlite:///rnic_dev.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Gemini API configuration placeholders
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    ENV = 'development'

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    ENV = 'production'
    # Ensure secure cookies and stricter settings in production
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True

# Configuration map used by the application factory
config_by_name = dict(
    development=DevelopmentConfig,
    production=ProductionConfig
)
