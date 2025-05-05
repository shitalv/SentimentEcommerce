"""
Add Time Data to Reviews

This script adds valid time data to reviews to enable time-based analysis.
"""

import logging
import sys
import os
from datetime import datetime, timedelta
import random
from bson import ObjectId

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('add_time_data')

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import MongoDB utils
from mongo_config import get_mongo_client

def add_dates_to_reviews():
    """Add valid dates to reviews for time-based analysis"""
    # Get MongoDB client
    mongo_client, db = get_mongo_client()
    if db is None:
        logger.error("Failed to connect to MongoDB")
        return False
    
    # Get all reviews
    reviews = list(db.reviews.find({}))
    logger.info(f"Found {len(reviews)} reviews in database")
    
    reviews_updated = 0
    
    # Base date for spreading reviews over time
    now = datetime.now()
    start_date = now - timedelta(days=180)  # 6 months ago
    
    for review in reviews:
        # Skip if already has a valid date
        if review.get("date") and isinstance(review.get("date"), datetime):
            continue
        
        # Generate random date between start_date and now
        days_ago = random.randint(0, 180)
        review_date = now - timedelta(days=days_ago)
        
        # Update review with date
        db.reviews.update_one(
            {"_id": review["_id"]},
            {"$set": {"date": review_date}}
        )
        
        reviews_updated += 1
    
    logger.info(f"Updated {reviews_updated} reviews with valid dates")
    return True

def get_products_with_reviews():
    """Get list of products that have reviews"""
    # Get MongoDB client
    mongo_client, db = get_mongo_client()
    if db is None:
        logger.error("Failed to connect to MongoDB")
        return []
    
    # Get all products
    products = list(db.products.find({}, {"_id": 1, "name": 1}))
    logger.info(f"Found {len(products)} products in database")
    
    # Check which products have reviews
    products_with_reviews = []
    
    for product in products:
        review_count = db.reviews.count_documents({"product_id": str(product["_id"])})
        
        if review_count > 0:
            products_with_reviews.append({
                "id": product["_id"],
                "name": product["name"],
                "review_count": review_count
            })
    
    logger.info(f"Found {len(products_with_reviews)} products with reviews")
    
    # Products without reviews will need sample reviews
    products_without_reviews = len(products) - len(products_with_reviews)
    logger.info(f"Found {products_without_reviews} products without reviews")
    
    return products_with_reviews

def add_sample_reviews_with_dates(missing_products=5):
    """Add sample reviews with dates to products that don't have any reviews yet"""
    # Get MongoDB client
    mongo_client, db = get_mongo_client()
    if db is None:
        logger.error("Failed to connect to MongoDB")
        return False
    
    # Find products without reviews
    products_with_reviews = set(p["product_id"] for p in db.reviews.distinct("product_id"))
    all_products = list(db.products.find({}))
    
    products_without_reviews = [p for p in all_products if str(p["_id"]) not in products_with_reviews]
    
    if not products_without_reviews:
        logger.info("All products have reviews")
        return True
    
    # Limit to requested number
    products_to_update = products_without_reviews[:missing_products]
    logger.info(f"Adding sample reviews to {len(products_to_update)} products")
    
    for product in products_to_update:
        logger.info(f"Adding reviews for product: {product['name']}")
        
        # Create 5 reviews with different dates and sentiments
        for i in range(5):
            # Calculate date - spread over last 6 months
            days_ago = random.randint(0, 180)
            review_date = datetime.now() - timedelta(days=days_ago)
            
            # Determine sentiment (mostly positive)
            sentiment_roll = random.random()
            if sentiment_roll < 0.7:  # 70% positive
                sentiment_class = "positive"
                sentiment_score = random.uniform(0.6, 0.9)
                rating = random.choice([4, 5])
                prefix = "Love"
            elif sentiment_roll < 0.9:  # 20% neutral
                sentiment_class = "neutral"
                sentiment_score = random.uniform(0.4, 0.6)
                rating = random.choice([3, 4])
                prefix = "Like"
            else:  # 10% negative
                sentiment_class = "negative"
                sentiment_score = random.uniform(0.1, 0.4)
                rating = random.choice([1, 2])
                prefix = "Disappointed with"
            
            # Create review text
            review_text = f"{prefix} this {product['name']}. Review #{i+1} created on {review_date.strftime('%Y-%m-%d')}."
            
            # Create review
            review_data = {
                "product_id": str(product["_id"]),
                "author": f"User{random.randint(1000, 9999)}",
                "title": f"{rating}-Star Review",
                "text": review_text,
                "rating": rating,
                "date": review_date,
                "sentiment_score": sentiment_score,
                "sentiment_class": sentiment_class,
                "created_at": datetime.now()
            }
            
            # Insert review
            db.reviews.insert_one(review_data)
        
        # Update product sentiment scores
        positive_count = 0
        neutral_count = 0
        negative_count = 0
        
        # Count by sentiment class
        if sentiment_class == "positive":
            positive_count += 1
        elif sentiment_class == "neutral":
            neutral_count += 1
        else:
            negative_count += 1
        
        # Update product
        db.products.update_one(
            {"_id": product["_id"]},
            {"$set": {
                "positive_score": 0.7,  # Default distribution
                "neutral_score": 0.2,
                "negative_score": 0.1,
                "sentiment_score": 0.65,
                "updated_at": datetime.now()
            }}
        )
    
    return True

if __name__ == "__main__":
    # First add dates to existing reviews
    add_dates_to_reviews()
    
    # Then get list of products with reviews
    products_with_reviews = get_products_with_reviews()
    
    # Add sample reviews to products that don't have any
    add_sample_reviews_with_dates(missing_products=10)