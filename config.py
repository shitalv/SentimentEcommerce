import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration class"""
    SECRET_KEY = os.environ.get("SESSION_SECRET", "development_secret_key")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    # Use environment variable DATABASE_URL for Replit (if available)
    # Otherwise fall back to local PostgreSQL for local development
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/sentiment_ecommerce")

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    # Use environment variable for production
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    # Use in-memory SQLite for testing
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"

# Configuration dictionary
config_dict = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig
}

# Get configuration based on environment
def get_config():
    env = os.environ.get("FLASK_ENV", "development")
    return config_dict.get(env, DevelopmentConfig)