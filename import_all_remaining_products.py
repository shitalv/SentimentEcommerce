"""
Import All Remaining Products

This script imports all remaining products from the dataset that are not yet in the database.
"""

import logging
import sys
import os
import re
import json
from datetime import datetime
import pandas as pd
import html
from bson import ObjectId

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('import_remaining')

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import MongoDB utils
from mongo_config import get_mongo_client
from backend.sentiment_analyzer import analyze_sentiment, classify_sentiment, get_sentiment_keywords

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
    
    # Remove non-breaking spaces and other invisible characters
    text = text.replace('\xa0', ' ')
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    return text

def get_missing_products_info(file_path):
    """Get information about products that are in the dataset but not in the database"""
    # Get MongoDB client
    mongo_client, db = get_mongo_client()
    if db is None:
        logger.error("Failed to connect to MongoDB")
        return []
    
    # Get existing ASINs in the database
    existing_asins = [p.get('asin', '') for p in db.products.find({}, {'asin': 1})]
    existing_asins = [asin for asin in existing_asins if asin]  # Filter out empty ASINs
    
    logger.info(f"Found {len(existing_asins)} existing products in database")
    
    # Load the dataset
    df = pd.read_csv(file_path, low_memory=False)
    
    # Get unique ASINs from dataset
    all_asins = df['asins'].unique()
    all_asins = [asin for asin in all_asins if isinstance(asin, str) and asin.strip()]
    
    logger.info(f"Found {len(all_asins)} unique ASINs in dataset")
    
    # Find missing ASINs
    missing_asins = [asin for asin in all_asins if asin not in existing_asins]
    logger.info(f"Found {len(missing_asins)} ASINs that are not in the database")
    
    # Get information about missing products
    missing_products = []
    
    for asin in missing_asins:
        # Get rows for this ASIN
        product_rows = df[df['asins'] == asin]
        
        if len(product_rows) == 0:
            continue
        
        # Use the first row for product details
        first_row = product_rows.iloc[0]
        
        product_info = {
            "asin": asin,
            "name": clean_text(first_row.get('name')),
            "brand": clean_text(first_row.get('brand')),
            "categories": [cat.strip() for cat in str(first_row.get('categories', '')).split(',') if cat.strip()],
            "primary_category": clean_text(first_row.get('primaryCategories')),
            "image_url": first_row.get('imageURLs', '').split(',')[0] if first_row.get('imageURLs') else None,
            "description": clean_text(first_row.get('description')),
            "row_count": len(product_rows)
        }
        
        missing_products.append(product_info)
    
    return missing_products

def import_remaining_products(file_path):
    """Import all remaining products from the dataset"""
    # Get MongoDB client
    mongo_client, db = get_mongo_client()
    if db is None:
        logger.error("Failed to connect to MongoDB")
        return False
    
    # Get missing products info
    missing_products = get_missing_products_info(file_path)
    
    if not missing_products:
        logger.info("No missing products to import")
        return True
    
    # Import each missing product
    for product_info in missing_products:
        try:
            # Create product document
            product_data = {
                "asin": product_info["asin"],
                "name": product_info["name"],
                "brand": product_info["brand"],
                "categories": product_info["categories"],
                "primary_category": product_info["primary_category"],
                "image_url": product_info["image_url"],
                "description": product_info["description"],
                "positive_score": 0.7,  # Default values
                "neutral_score": 0.2,
                "negative_score": 0.1,
                "sentiment_score": 0.65,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            
            # Insert product
            product_id = db.products.insert_one(product_data).inserted_id
            logger.info(f"Imported product: {product_info['name']} (ASIN: {product_info['asin']})")
            
            # Import reviews for this product
            import_product_reviews(file_path, product_info["asin"], str(product_id), db)
            
        except Exception as e:
            logger.error(f"Error importing product {product_info['asin']}: {str(e)}")
    
    # Count products after import
    product_count = db.products.count_documents({})
    logger.info(f"Total products in database after import: {product_count}")
    
    return True

def import_product_reviews(file_path, asin, product_id, db):
    """Import reviews for a specific product"""
    # Load the dataset
    df = pd.read_csv(file_path, low_memory=False)
    
    # Get rows for this ASIN
    product_rows = df[df['asins'] == asin]
    
    if len(product_rows) == 0:
        return
    
    reviews_added = 0
    
    # Process each row as a review
    for idx, row in product_rows.iterrows():
        try:
            # Extract review data
            review_text = row.get('reviews.text')
            rating = row.get('reviews.rating')
            
            if not review_text or not rating:
                continue
            
            # Clean and process review
            review_data = {
                "product_id": product_id,
                "author": clean_text(row.get('reviews.username')),
                "title": clean_text(row.get('reviews.title')),
                "text": clean_text(review_text),
                "rating": float(rating) if rating else 3.0,
                "created_at": datetime.now()
            }
            
            # Add sentiment analysis
            sentiment_score = analyze_sentiment(review_data["text"])
            review_data["sentiment_score"] = sentiment_score
            review_data["sentiment_class"] = classify_sentiment(sentiment_score)
            
            # Check if review already exists
            existing_review = db.reviews.find_one({
                "product_id": product_id,
                "text": review_data["text"]
            })
            
            if existing_review:
                continue
            
            # Insert review
            db.reviews.insert_one(review_data)
            reviews_added += 1
            
        except Exception as e:
            logger.error(f"Error importing review: {str(e)}")
    
    logger.info(f"Added {reviews_added} reviews for product ASIN {asin}")
    
    # Update product sentiment scores if we added reviews
    if reviews_added > 0:
        update_product_sentiment(product_id, db)

def update_product_sentiment(product_id, db):
    """Update sentiment scores for a product based on its reviews"""
    # Get all reviews for this product
    product_reviews = list(db.reviews.find({"product_id": product_id}))
    
    if not product_reviews:
        return
    
    # Calculate sentiment distribution
    positive_count = sum(1 for r in product_reviews if r.get("sentiment_class") == "positive")
    neutral_count = sum(1 for r in product_reviews if r.get("sentiment_class") == "neutral")
    negative_count = sum(1 for r in product_reviews if r.get("sentiment_class") == "negative")
    total_count = len(product_reviews)
    
    # Calculate average sentiment score
    avg_score = sum(r.get("sentiment_score", 0.5) for r in product_reviews) / total_count
    
    # Update product
    db.products.update_one(
        {"_id": ObjectId(product_id)},
        {"$set": {
            "positive_score": positive_count / total_count,
            "neutral_score": neutral_count / total_count,
            "negative_score": negative_count / total_count,
            "sentiment_score": avg_score,
            "updated_at": datetime.now()
        }}
    )

if __name__ == "__main__":
    # Set default file path
    file_path = "attached_assets/Datafiniti_Amazon_Consumer_Reviews_of_Amazon_Products.csv"
    
    # Check if file exists
    if not os.path.isfile(file_path):
        logger.error(f"File not found: {file_path}")
        sys.exit(1)
    
    # Import remaining products
    import_remaining_products(file_path)