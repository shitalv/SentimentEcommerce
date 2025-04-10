"""
Database Initialization Script for Sentiment E-commerce Application
Run this script once to set up your database tables.
"""
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Check for DATABASE_URL
database_url = os.environ.get("DATABASE_URL")
if not database_url:
    # Will use the default in app.py (postgresql://postgres:postgres@localhost:5432/sentiment_ecommerce)
    logger.info("DATABASE_URL not set. Will use default local PostgreSQL configuration from app.py")
else:
    logger.info(f"Using database from environment: {database_url}")

# Set a default secret key
if not os.environ.get("SESSION_SECRET"):
    os.environ["SESSION_SECRET"] = "development_secret_key_change_me_later"
    logger.info("Using default development secret key")

logger.info("Environment variables checked")

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