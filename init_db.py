"""
Database Initialization Script for Sentiment E-commerce Application
Run this script once to set up your database tables.
"""
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# On Replit, DATABASE_URL is already set as an environment variable
# We don't need to set it manually
# If you're running this locally, you'll need to set the DATABASE_URL environment variable
if not os.environ.get("DATABASE_URL"):
    logger.warning("DATABASE_URL environment variable not set! Using Replit's DATABASE_URL...")
# Set a default secret key
os.environ["SESSION_SECRET"] = "development_secret_key_change_me_later"

logger.info("Environment variables set")

# Import the Flask app after setting environment variables
from app import app, db
from models import User

logger.info("Imported Flask app and models")

# Create database tables
with app.app_context():
    logger.info("Creating database tables...")
    db.create_all()
    logger.info("Database tables created successfully!")
    
    # Check if User table exists and was created properly
    try:
        user_count = User.query.count()
        logger.info(f"User table exists with {user_count} records")
    except Exception as e:
        logger.error(f"Error accessing User table: {str(e)}")

logger.info("Database initialization complete!")