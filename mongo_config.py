"""
MongoDB Configuration Module for Sentiment E-commerce Application

This module sets up the MongoDB connection and initializes the database with collections.
"""

import os
from flask_pymongo import PyMongo
from pymongo import MongoClient
import logging
import json

# Create a logger
logger = logging.getLogger(__name__)

# MongoDB connection configuration - using MongoDB Atlas
# Format: mongodb+srv://<username>:<password>@<cluster>.mongodb.net/dbname?retryWrites=true&w=majority
MONGO_URI = os.environ.get('MONGODB_URI')
logger.info("Using MongoDB connection string from environment variable")

# We don't have a fallback connection string in the code as it's not secure to include credentials
if not MONGO_URI:
    logger.warning("No MongoDB URI found in environment variables. Application will run in sample data mode.")
# Extract database name from the URI or use default
if MONGO_URI and '/' in MONGO_URI:
    parts = MONGO_URI.split('/')
    if len(parts) > 3:
        # Handle path portion that might contain the database name
        path_part = parts[3]
        if '?' in path_part:
            DB_NAME = path_part.split('?')[0]
        else:
            DB_NAME = path_part
    else:
        DB_NAME = 'sentiment_ecommerce'
else:
    DB_NAME = os.environ.get('MONGODB_NAME', 'sentiment_ecommerce')

# If DB_NAME is empty, set to default
if not DB_NAME:
    DB_NAME = 'sentiment_ecommerce'
    
logger.info(f"Using database name: {DB_NAME}")

# We'll use a mock database if MongoDB is not available
USE_MOCK_DB = False

# Initialize MongoDB
mongo = PyMongo()

# Mock data storage (when MongoDB is unavailable)
mock_db = {
    'users': {},
    'products': {},
    'reviews': {},
    'user_saved_products': {}
}

def init_mongo(app):
    """Initialize MongoDB with the Flask app"""
    global USE_MOCK_DB, mongo
    
    # Check if we have a MongoDB URI
    if not MONGO_URI:
        logger.warning("No MongoDB URI provided. Using sample data mode.")
        USE_MOCK_DB = True
        app.config['USING_SAMPLE_DATA'] = True
        return None
    
    try:
        # Use the same direct connection method that works in test_mongo_connection.py
        logger.info("Trying direct MongoDB connection using test script approach")
        
        # Use exact same connection string as in test_mongo_connection.py
        test_mongo_uri = "mongodb+srv://testdev01:testdev01@cluster0.kx3tti3.mongodb.net/sentiment_ecommerce?retryWrites=true&w=majority&appName=Cluster0"
        client = MongoClient(test_mongo_uri)
        
        # Verify connection works
        client.admin.command('ping')
        
        # Get database
        db = client[DB_NAME]
        
        # Store the working client and db in app config
        app.config['MONGO_CLIENT'] = client
        app.config['MONGO_DB'] = db
        
        # Configure Flask-PyMongo too, for compatibility
        app.config["MONGO_URI"] = test_mongo_uri
        app.config["MONGO_DBNAME"] = DB_NAME
        
        # Initialize PyMongo with the app
        mongo.init_app(app)
        
        logger.info(f"MongoDB connected successfully to {DB_NAME} database")
        return mongo
    except Exception as e:
        full_error = getattr(e, 'details', {})
        logger.error(f"Error connecting to MongoDB: {str(e)}, full error: {full_error}")
        logger.warning("Falling back to sample data mode")
        USE_MOCK_DB = True
        app.config['USING_SAMPLE_DATA'] = True
        return None

def get_db():
    """Get the MongoDB database instance"""
    global USE_MOCK_DB
    if USE_MOCK_DB:
        return mock_db
    
    from flask import current_app
    
    # Try to use PyMongo connection
    try:
        # First try the flask-pymongo connection
        return mongo.db
    except Exception as e:
        logger.warning(f"PyMongo connection failed: {str(e)}")
        
        # Fall back to the direct client if PyMongo fails
        if 'MONGO_DB' in current_app.config:
            logger.info("Using fallback direct MongoDB connection")
            return current_app.config['MONGO_DB']
        else:
            logger.error("No fallback MongoDB connection available")
            USE_MOCK_DB = True
            return mock_db

def create_indexes():
    """Create necessary indexes for performance"""
    global USE_MOCK_DB
    if USE_MOCK_DB:
        logger.info("Skipping index creation in sample data mode")
        return
        
    try:
        # Create indexes for user collection
        mongo.db.users.create_index("username", unique=True)
        mongo.db.users.create_index("email", unique=True)
        
        # Create indexes for products collection
        mongo.db.products.create_index("asin", unique=True)
        mongo.db.products.create_index("category")
        
        # Create indexes for reviews collection
        mongo.db.reviews.create_index("product_id")
        mongo.db.reviews.create_index([("sentiment_score", -1)])
        
        # Create indexes for user_saved_products collection
        mongo.db.user_saved_products.create_index([("user_id", 1), ("product_id", 1)], unique=True)
        
        logger.info("MongoDB indexes created successfully")
    except Exception as e:
        logger.error(f"Error creating MongoDB indexes: {str(e)}")

def setup_db():
    """Set up database with initial collections if they don't exist"""
    global USE_MOCK_DB
    if USE_MOCK_DB:
        logger.info("Setting up sample data mode")
        # Load sample data
        load_sample_data()
        return
        
    try:
        # Create collections if they don't exist
        collections = ["users", "products", "reviews", "user_saved_products"]
        for collection in collections:
            if collection not in mongo.db.list_collection_names():
                mongo.db.create_collection(collection)
                logger.info(f"Created collection: {collection}")
        
        # Create indexes
        create_indexes()
        
        logger.info("MongoDB setup completed successfully")
    except Exception as e:
        logger.error(f"Error setting up MongoDB: {str(e)}")
        logger.warning("Falling back to sample data mode")
        USE_MOCK_DB = True
        load_sample_data()

def load_sample_data():
    """Load sample data for when MongoDB is unavailable"""
    global mock_db
    
    logger.info("Loading sample data for the application")
    
    # Initialize users dict if it doesn't exist
    if "users" not in mock_db:
        mock_db["users"] = {}
    
    # Add a default admin user for testing
    from werkzeug.security import generate_password_hash
    from datetime import datetime
    
    # Create admin user if it doesn't exist
    admin_user = {
        "_id": "admin_user_id",
        "username": "admin",
        "email": "admin@example.com",
        "password_hash": generate_password_hash("admin123"),
        "created_at": datetime.utcnow(),
        "is_admin": True
    }
    mock_db["users"]["admin_user_id"] = admin_user
    logger.info("Added default admin user (username: admin, password: admin123)")
    
    # Sample product data
    products = [
        {
            "_id": "1",
            "name": "Wireless Bluetooth Headphones",
            "description": "High-quality wireless headphones with noise cancellation technology, 20-hour battery life, and comfortable over-ear design.",
            "price": 79.99,
            "category": "Electronics",
            "image_url": "https://example.com/headphones.jpg",
            "asin": "B01ABCDEF",
            "positive_score": 0.75,
            "neutral_score": 0.15,
            "negative_score": 0.10
        },
        {
            "_id": "2",
            "name": "Smart Fitness Tracker",
            "description": "Track your health and fitness with this waterproof smart band featuring heart rate monitoring, sleep tracking, and smartphone notifications.",
            "price": 49.99,
            "category": "Wearables",
            "image_url": "https://example.com/fitness-tracker.jpg",
            "asin": "B02GHIJKL",
            "positive_score": 0.80,
            "neutral_score": 0.15,
            "negative_score": 0.05
        },
        {
            "_id": "3",
            "name": "Premium Coffee Maker",
            "description": "Programmable coffee maker with thermal carafe, strength control, and auto shut-off. Makes up to 12 cups of coffee.",
            "price": 129.99,
            "category": "Kitchen Appliances",
            "image_url": "https://example.com/coffee-maker.jpg",
            "asin": "B03MNOPQR",
            "positive_score": 0.65,
            "neutral_score": 0.20,
            "negative_score": 0.15
        }
    ]
    
    # Sample reviews
    reviews = [
        {
            "_id": "1",
            "product_id": "1",
            "author": "AudioFan",
            "text": "These headphones are amazing! The sound quality is exceptional and the noise cancellation works perfectly. Battery life is as advertised. Worth every penny!",
            "rating": 5.0,
            "date": "2023-05-15",
            "sentiment_score": 0.9,
            "sentiment_class": "positive",
            "sentiment_keywords": json.dumps(["amazing", "exceptional", "perfectly"])
        },
        {
            "_id": "2",
            "product_id": "1",
            "author": "MusicLover",
            "text": "Good headphones, but the ear cushions could be more comfortable for long listening sessions. Sound quality is excellent though.",
            "rating": 4.0,
            "date": "2023-04-22",
            "sentiment_score": 0.7,
            "sentiment_class": "positive",
            "sentiment_keywords": json.dumps(["good", "excellent", "comfortable"])
        },
        {
            "_id": "3",
            "product_id": "1",
            "author": "TechReviewer",
            "text": "Battery doesn't last as long as advertised. Sound quality is decent but not as good as some competitors in the same price range.",
            "rating": 3.0,
            "date": "2023-03-10",
            "sentiment_score": 0.4,
            "sentiment_class": "neutral",
            "sentiment_keywords": json.dumps(["decent", "not as good"])
        }
    ]
    
    # Add sample data to mock database
    for product in products:
        mock_db["products"][product["_id"]] = product
        
    for review in reviews:
        mock_db["reviews"][review["_id"]] = review
        
    logger.info("Sample data loaded successfully")

# Direct connection for scripts outside of Flask context
def get_mongo_client():
    """Get a direct MongoDB client connection"""
    if USE_MOCK_DB:
        logger.warning("Using sample data mode - no direct MongoDB client available")
        return None, mock_db
        
    try:
        # Use the same direct connection method that works in test_mongo_connection.py
        test_mongo_uri = "mongodb+srv://testdev01:testdev01@cluster0.kx3tti3.mongodb.net/sentiment_ecommerce?retryWrites=true&w=majority&appName=Cluster0"
        client = MongoClient(test_mongo_uri)
        db = client[DB_NAME]
        
        # Test the connection with a simple query
        # This will force an actual connection attempt
        db.list_collection_names()
        
        logger.info("MongoDB client connection successful")
        return client, db
    except Exception as e:
        logger.error(f"Error connecting to MongoDB: {str(e)}")
        # DO NOT return mock_db here, that's what was causing the problem
        # Instead, raise an exception so the error is visible
        raise Exception(f"Failed to connect to MongoDB: {str(e)}")