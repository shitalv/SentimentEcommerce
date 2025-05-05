"""
Test MongoDB connection directly
"""

import pymongo
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB connection string
MONGO_URI = "mongodb+srv://testdev01:testdev01@cluster0.kx3tti3.mongodb.net/sentiment_ecommerce?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME = "sentiment_ecommerce"

try:
    # Connect directly without Flask
    logger.info(f"Attempting to connect to MongoDB with URI: {MONGO_URI}")
    client = pymongo.MongoClient(MONGO_URI)
    
    # Verify connection
    client.admin.command('ping')
    logger.info("Successfully connected to MongoDB!")
    
    # Get database
    db = client[DB_NAME]
    logger.info(f"Connected to database: {DB_NAME}")
    
    # List collections
    collections = db.list_collection_names()
    logger.info(f"Available collections: {collections}")
    
    # Create a test collection if not exists
    if "test_collection" not in collections:
        logger.info("Creating test collection...")
        db.create_collection("test_collection")
    
    # Insert a test document
    test_collection = db["test_collection"]
    result = test_collection.insert_one({"test_key": "test_value", "timestamp": "2025-04-27"})
    logger.info(f"Inserted test document with ID: {result.inserted_id}")
    
    # Query the test document
    test_doc = test_collection.find_one({"test_key": "test_value"})
    logger.info(f"Retrieved test document: {test_doc}")
    
except Exception as e:
    logger.error(f"Error connecting to MongoDB: {str(e)}")