"""
Simple MongoDB connection test
"""

import pymongo
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try three different connection string formats
connection_strings = [
    # Standard format
    "mongodb+srv://testdev01:testdev01@cluster0.kx3tti3.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0",
    
    # With database name in path
    "mongodb+srv://testdev01:testdev01@cluster0.kx3tti3.mongodb.net/sentiment_ecommerce?retryWrites=true&w=majority&appName=Cluster0",
    
    # Simplified
    "mongodb+srv://testdev01:testdev01@cluster0.kx3tti3.mongodb.net/"
]

for idx, uri in enumerate(connection_strings):
    logger.info(f"Trying connection string {idx+1}...")
    
    try:
        # Connect to MongoDB
        logger.info(f"Attempting to connect with URI: {uri}")
        client = pymongo.MongoClient(uri)
        
        # Verify connection
        client.admin.command('ping')
        logger.info("Successfully connected to MongoDB!")
        
        # Get database info
        db_names = client.list_database_names()
        logger.info(f"Available databases: {db_names}")
        
        # Success!
        logger.info(f"Connection string {idx+1} works!")
        break
        
    except Exception as e:
        logger.error(f"Error connecting to MongoDB with connection string {idx+1}: {str(e)}")
        continue