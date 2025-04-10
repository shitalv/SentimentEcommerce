import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager
from config import get_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Load configuration based on environment
    app.config.from_object(get_config())
    
    # Initialize extensions
    db.init_app(app)
    
    # Initialize login manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'backend.login'
    
    # User loader function for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        from models import User
        return User.query.get(int(user_id))
    
    # Import and register blueprints
    try:
        from backend.app import bp as backend_bp
        app.register_blueprint(backend_bp)
        logger.info("Backend routes registered successfully")
    except ImportError as e:
        logger.warning(f"Failed to import backend routes: {e}")
    
    # Create database tables
    with app.app_context():
        import models  # noqa: F401
        try:
            db.create_all()
            logger.info("Database tables created successfully!")
        except Exception as e:
            logger.error(f"Error creating database tables: {str(e)}")
    
    return app

# Create the Flask application instance
app = create_app()

# Development server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)