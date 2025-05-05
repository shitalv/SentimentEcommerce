"""
Direct MongoDB Connection Flask App

This is a simplified version of our application that uses
the direct connection approach that we've verified works in the test script.
"""

import os
import logging
import pymongo
import json
from flask import Flask, jsonify

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# MongoDB connection string - hardcode the verified working connection string
MONGO_URI = "mongodb+srv://testdev01:testdev01@cluster0.kx3tti3.mongodb.net/sentiment_ecommerce?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME = "sentiment_ecommerce"

# Create a Flask app
app = Flask(__name__)

# Initialize MongoDB connection
try:
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
except Exception as e:
    logger.error(f"Error connecting to MongoDB: {str(e)}")
    client = None
    db = None

# Routes
@app.route('/')
def index():
    """Home page"""
    if not db:
        return "MongoDB connection failed. Check logs for details."
    
    collections = db.list_collection_names()
    return f"Connected to MongoDB!<br>Database: {DB_NAME}<br>Collections: {collections}"

@app.route('/products')
def products():
    """List products from MongoDB"""
    if not db:
        return jsonify({"error": "MongoDB connection failed"})
    
    try:
        products_list = list(db["products"].find({}).limit(10))
        
        # Convert ObjectId to string for JSON serialization
        for product in products_list:
            if '_id' in product:
                product['_id'] = str(product['_id'])
        
        return jsonify(products_list)
    except Exception as e:
        logger.error(f"Error fetching products: {str(e)}")
        return jsonify({"error": str(e)})

@app.route('/reviews')
def reviews():
    """List reviews from MongoDB"""
    if not db:
        return jsonify({"error": "MongoDB connection failed"})
    
    try:
        reviews_list = list(db["reviews"].find({}).limit(10))
        
        # Convert ObjectId to string for JSON serialization
        for review in reviews_list:
            if '_id' in review:
                review['_id'] = str(review['_id'])
        
        return jsonify(reviews_list)
    except Exception as e:
        logger.error(f"Error fetching reviews: {str(e)}")
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)