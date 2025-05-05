"""
Simple MongoDB Flask App
"""

import os
import logging
import pymongo
from flask import Flask

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB connection string
MONGO_URI = "mongodb+srv://testdev01:testdev01@cluster0.kx3tti3.mongodb.net/sentiment_ecommerce?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME = "sentiment_ecommerce"

# Create a Flask app
app = Flask(__name__)

# Routes
@app.route('/')
def index():
    """Home page that displays MongoDB connection status"""
    try:
        # Connect to MongoDB
        client = pymongo.MongoClient(MONGO_URI)
        
        # Verify connection works
        client.admin.command('ping')
        
        # Get database
        db = client[DB_NAME]
        
        # List collections
        collections = db.list_collection_names()
        
        return f"Connected to MongoDB!<br>Database: {DB_NAME}<br>Collections: {collections}"
    except Exception as e:
        logger.error(f"Error connecting to MongoDB: {str(e)}")
        return f"Failed to connect to MongoDB: {str(e)}"

if __name__ == "__main__":
    print("Starting simple MongoDB test server...")
    print(f"Using MongoDB URI: {MONGO_URI}")
    print(f"Database name: {DB_NAME}")
    app.run(host="0.0.0.0", port=5001, debug=True)