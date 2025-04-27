"""
Simple Amazon Products Importer for MongoDB

This script imports a small number of Amazon products from the CSV dataset
into MongoDB without full sentiment analysis.
"""

import csv
import logging
import sys
import os
import re
from datetime import datetime
import html
import json
import pandas as pd

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('quick_importer')

# Import MongoDB utils
from mongo_config import get_mongo_client

def clean_text(text):
    """Clean text data from common issues"""
    if not text:
        return ""
    
    # Make sure we're working with a string
    if not isinstance(text, str):
        try:
            text = str(text)
        except:
            return ""
    
    # Decode HTML entities
    text = html.unescape(text)
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', ' ', text)
    
    # Replace multiple spaces, newlines, and tabs with a single space
    text = re.sub(r'\s+', ' ', text)
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    return text

def import_products(file_path, limit=10):
    """Import a small number of products from CSV"""
    # Get MongoDB client
    mongo_client, db = get_mongo_client()
    if db is None:
        logger.error("Failed to connect to MongoDB")
        return False
    
    # Load the CSV file
    try:
        logger.info(f"Reading CSV file: {file_path}")
        
        # Read with pandas to handle large files
        df = pd.read_csv(file_path, low_memory=False, nrows=limit)
        
        logger.info(f"Loaded {len(df)} rows from CSV")
        
        # Process each row as a product
        for index, row in df.iterrows():
            asin = row.get('asins')
            
            # Clean up ASIN if it's a list
            if isinstance(asin, str) and ',' in asin:
                asin = asin.split(',')[0].strip()
            
            if asin:
                asin = asin.strip().upper()
            else:
                continue
                
            # Extract product data
            name = clean_text(row.get('name'))
            brand = clean_text(row.get('brand'))
            image_url = row.get('imageURLs', '').split(',')[0] if row.get('imageURLs') else None
            category = row.get('primaryCategories') or row.get('categories', '').split(',')[0] if row.get('categories') else None
            
            # Check if product exists
            existing_product = db.products.find_one({"asin": asin})
            
            if not existing_product:
                # Create a new product
                product = {
                    "asin": asin,
                    "name": name,
                    "brand": brand,
                    "category": category,
                    "image_url": image_url,
                    "manufacturer": clean_text(row.get('manufacturer')),
                    "positive_score": 0.5,  # Default scores
                    "neutral_score": 0.3,
                    "negative_score": 0.2,
                    "sentiment_score": 0.6,  # Slightly positive default
                    "created_at": datetime.now(),
                    "updated_at": datetime.now()
                }
                
                # Insert the product
                product_id = db.products.insert_one(product).inserted_id
                logger.info(f"Created product: {name} (ASIN: {asin})")
                
                # Create a sample review
                review_text = row.get('reviews.text')
                if review_text:
                    review = {
                        "product_id": str(product_id),
                        "author": clean_text(row.get('reviews.username')),
                        "title": clean_text(row.get('reviews.title')),
                        "text": clean_text(review_text),
                        "rating": float(row.get('reviews.rating')) if row.get('reviews.rating') else 4.0,
                        "sentiment_score": 0.6,  # Default slightly positive
                        "sentiment_class": "positive",
                        "sentiment_keywords": json.dumps(["good", "useful", "recommend"]),
                        "created_at": datetime.now()
                    }
                    
                    db.reviews.insert_one(review)
                    logger.info(f"Added review for product: {name}")
    
    except Exception as e:
        logger.error(f"Error importing products: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    # Import 10 products from the CSV file
    csv_file = "attached_assets/Datafiniti_Amazon_Consumer_Reviews_of_Amazon_Products.csv"
    
    if not os.path.isfile(csv_file):
        logger.error(f"File not found: {csv_file}")
        sys.exit(1)
    
    if import_products(csv_file, 10):
        logger.info("Quick import completed successfully")
    else:
        logger.error("Quick import failed")