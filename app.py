import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager

from config import Config
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = os.environ.get("SESSION_SECRET", "default_secret_key")
# Use environment variable for database connection
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get('DATABASE_URL', 'postgresql://postgres:root@localhost:5432/sentiment_ecommerce')
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# Add this before db.create_all()
# with app.app_context():
#     # Create a custom schema
#     db.session.execute('CREATE SCHEMA IF NOT EXISTS myschema')
#     db.session.commit()
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
            # Check if we can connect to the database
            db.engine.connect()
            db.create_all()
            logger.info("Database tables created successfully!")
        except Exception as e:
            logger.error(f"Error creating database tables: {str(e)}")
            logger.warning(
                "Database is unavailable. Running in limited mode with sample data."
            )

            # If this is a Neon database error about disabled endpoint, provide helpful message
            if "endpoint is disabled" in str(e):
                logger.error(
                    "Neon database endpoint is disabled. You may need to enable it through the Neon dashboard."
                )
                # Set a flag to indicate we're using sample data
                app.config['USING_SAMPLE_DATA'] = True

    # No need for create_app since we already created the app above
    pass

# Development server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
