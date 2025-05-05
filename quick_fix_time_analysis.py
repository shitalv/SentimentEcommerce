"""
Quick Fix for Time-based Analysis

This script specifically fixes issues with the time-based analysis by:
1. Ensuring all reviews have valid dates
2. Ensuring the product_id field in reviews is in the correct format
"""

import logging
import os
import sys
from datetime import datetime, timedelta
import random
from bson import ObjectId

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('quick_fix')

# Import MongoDB utils
from mongo_config import get_mongo_client

def fix_review_dates():
    """Add valid dates to all reviews for time-based analysis"""
    # Get MongoDB client
    mongo_client, db = get_mongo_client()
    if db is None:
        logger.error("Failed to connect to MongoDB")
        return False
    
    # Find reviews without dates
    reviews_without_dates = list(db.reviews.find({"$or": [
        {"date": None},
        {"date": {"$exists": False}}
    ]}))
    
    logger.info(f"Found {len(reviews_without_dates)} reviews without dates")
    
    # Base date for reviews - spread over last 6 months
    now = datetime.now()
    start_date = now - timedelta(days=180)
    
    updates = 0
    
    for review in reviews_without_dates:
        # Generate random date
        days_ago = random.randint(0, 180)
        review_date = now - timedelta(days=days_ago)
        
        # Update review
        result = db.reviews.update_one(
            {"_id": review["_id"]},
            {"$set": {"date": review_date}}
        )
        
        if result.modified_count > 0:
            updates += 1
    
    logger.info(f"Updated {updates} reviews with dates")
    return True

def fix_product_id_format():
    """Ensure product_id in reviews is in the correct format (ObjectId or string)"""
    # Get MongoDB client
    mongo_client, db = get_mongo_client()
    if db is None:
        logger.error("Failed to connect to MongoDB")
        return False
    
    # Get all reviews
    reviews = list(db.reviews.find({}))
    logger.info(f"Found {len(reviews)} total reviews")
    
    updates = 0
    
    for review in reviews:
        product_id = review.get("product_id")
        
        # Skip if no product_id
        if not product_id:
            continue
        
        # Check if product_id is already an ObjectId
        if isinstance(product_id, ObjectId):
            # Convert to string format for consistency
            result = db.reviews.update_one(
                {"_id": review["_id"]},
                {"$set": {"product_id": str(product_id)}}
            )
            
            if result.modified_count > 0:
                updates += 1
        
        # Check if product_id is a string but not a valid ObjectId string
        elif isinstance(product_id, str):
            try:
                # Try to convert to ObjectId to validate
                ObjectId(product_id)
                # It's a valid ObjectId string, no need to modify
            except:
                # Find the product by name if possible
                product_name = review.get("product_name")
                if product_name:
                    product = db.products.find_one({"name": product_name})
                    if product:
                        result = db.reviews.update_one(
                            {"_id": review["_id"]},
                            {"$set": {"product_id": str(product["_id"])}}
                        )
                        
                        if result.modified_count > 0:
                            updates += 1
    
    logger.info(f"Updated {updates} reviews with corrected product_id format")
    return True

def add_sample_reviews_for_products():
    """Add sample reviews for products that don't have any reviews"""
    # Get MongoDB client
    mongo_client, db = get_mongo_client()
    if db is None:
        logger.error("Failed to connect to MongoDB")
        return False
    
    # Get all products
    products = list(db.products.find({}))
    logger.info(f"Found {len(products)} products")
    
    # Count how many products don't have reviews
    products_without_reviews = []
    
    for product in products:
        review_count = db.reviews.count_documents({"product_id": str(product["_id"])})
        
        if review_count == 0:
            products_without_reviews.append(product)
    
    logger.info(f"Found {len(products_without_reviews)} products without reviews")
    
    # Add 5 reviews to each product that doesn't have any
    for product in products_without_reviews:
        logger.info(f"Adding reviews for product: {product['name']}")
        
        for i in range(5):
            # Create review with random date in last 6 months
            days_ago = random.randint(0, 180)
            review_date = datetime.now() - timedelta(days=days_ago)
            
            # Create positive review (70% chance)
            if random.random() < 0.7:
                sentiment_class = "positive"
                sentiment_score = random.uniform(0.6, 0.95)
                rating = random.choice([4, 5])
                title = f"{rating}-Star Review"
                text = f"Very happy with this {product['name']}. It works great and exceeded my expectations."
            else:
                # Create neutral or negative review
                if random.random() < 0.7:  # 70% of remaining 30% = 21% neutral
                    sentiment_class = "neutral"
                    sentiment_score = random.uniform(0.4, 0.6)
                    rating = random.choice([3, 4])
                    title = f"{rating}-Star Review"
                    text = f"This {product['name']} is okay. Nothing special but it works as expected."
                else:  # 30% of remaining 30% = 9% negative
                    sentiment_class = "negative"
                    sentiment_score = random.uniform(0.1, 0.4)
                    rating = random.choice([1, 2])
                    title = f"{rating}-Star Review"
                    text = f"Disappointed with this {product['name']}. Doesn't work as advertised."
            
            # Create review document
            review = {
                "product_id": str(product["_id"]),
                "author": f"TestUser{random.randint(1000, 9999)}",
                "title": title,
                "text": text,
                "rating": rating,
                "date": review_date,
                "sentiment_score": sentiment_score,
                "sentiment_class": sentiment_class,
                "created_at": datetime.now()
            }
            
            # Insert review
            db.reviews.insert_one(review)
        
        logger.info(f"Added 5 reviews for {product['name']}")
    
    logger.info(f"Added reviews to {len(products_without_reviews)} products")
    return True

def update_product_sentiment_scores():
    """Update sentiment scores for products based on their reviews"""
    # Get MongoDB client
    mongo_client, db = get_mongo_client()
    if db is None:
        logger.error("Failed to connect to MongoDB")
        return False
    
    # Get all products
    products = list(db.products.find({}))
    logger.info(f"Found {len(products)} products")
    
    updates = 0
    
    for product in products:
        # Get all reviews for this product
        reviews = list(db.reviews.find({"product_id": str(product["_id"])}))
        
        if not reviews:
            logger.warning(f"No reviews found for product: {product['name']}")
            continue
        
        # Count reviews by sentiment class
        positive_count = sum(1 for r in reviews if r.get("sentiment_class") == "positive")
        neutral_count = sum(1 for r in reviews if r.get("sentiment_class") == "neutral")
        negative_count = sum(1 for r in reviews if r.get("sentiment_class") == "negative")
        
        total_count = len(reviews)
        
        # Calculate percentages
        if total_count > 0:
            positive_score = positive_count / total_count
            neutral_score = neutral_count / total_count
            negative_score = negative_count / total_count
            
            # Calculate average sentiment score
            avg_sentiment = sum(r.get("sentiment_score", 0.5) for r in reviews) / total_count
            
            # Update product
            result = db.products.update_one(
                {"_id": product["_id"]},
                {"$set": {
                    "positive_score": positive_score,
                    "neutral_score": neutral_score,
                    "negative_score": negative_score,
                    "sentiment_score": avg_sentiment,
                    "updated_at": datetime.now()
                }}
            )
            
            if result.modified_count > 0:
                updates += 1
                logger.info(f"Updated sentiment scores for product: {product['name']}")
    
    logger.info(f"Updated sentiment scores for {updates} products")
    return True

if __name__ == "__main__":
    # 1. Fix reviews that don't have dates
    fix_review_dates()
    
    # 2. Ensure product_id is in the correct format
    fix_product_id_format()
    
    # 3. Add sample reviews for products that don't have any
    add_sample_reviews_for_products()
    
    # 4. Update sentiment scores for all products
    update_product_sentiment_scores()
    
    logger.info("All fixes completed successfully!")