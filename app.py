import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default_secret_key")

# Configure database - use environment variable if set, otherwise use local PostgreSQL
database_url = os.environ.get("DATABASE_URL")
if not database_url:
    # Default to local PostgreSQL for development
    database_url = "postgresql://postgres:postgres@localhost:5432/sentiment_ecommerce"
    logger.info(f"DATABASE_URL not set, using local PostgreSQL: {database_url}")
else:
    logger.info(f"Using database from environment: {database_url}")

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the app with the extension
db.init_app(app)

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Import models after db initialization
with app.app_context():
    # Import models to create tables
    import models  # noqa: F401
    
    # User loader function for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        from models import User
        return User.query.get(int(user_id))
    
    # Create tables if they don't exist
    db.create_all()

# Import routes
try:
    from backend.app import *  # noqa: F401
    logger.info("Backend routes imported successfully")
except ImportError as e:
    logger.warning(f"Failed to import backend routes: {e}")

# Development server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)