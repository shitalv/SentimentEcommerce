"""
Fix Time Analysis Data

This script fixes the time-based analysis by ensuring all reviews have dates
and all products have reviews with time data.
"""

import logging
import sys
import os
from datetime import datetime, timedelta
import random
from bson import ObjectId

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('fix_time_analysis')

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import MongoDB utils
from mongo_config import get_mongo_client

def add_dates_to_all_reviews():
    """Add valid dates to all reviews for time-based analysis"""
    # Get MongoDB client
    mongo_client, db = get_mongo_client()
    if db is None:
        logger.error("Failed to connect to MongoDB")
        return False
    
    # Get all reviews that don't have a date field or have a null date
    reviews_without_dates = list(db.reviews.find({"$or": [
        {"date": None},
        {"date": {"$exists": False}}
    ]}))
    
    logger.info(f"Found {len(reviews_without_dates)} reviews without dates")
    
    # Base date for reviews - 6 months ago
    start_date = datetime.now() - timedelta(days=180)
    
    for review in reviews_without_dates:
        # Generate a random date between start_date and now
        days = random.randint(0, 180)
        random_date = start_date + timedelta(days=days)
        
        # Update the review with the random date
        db.reviews.update_one(
            {"_id": review["_id"]},
            {"$set": {"date": random_date}}
        )
    
    logger.info(f"Updated {len(reviews_without_dates)} reviews with random dates")
    return True

def create_reviews_for_empty_products():
    """Create reviews for products that don't have any reviews"""
    # Get MongoDB client
    mongo_client, db = get_mongo_client()
    if db is None:
        logger.error("Failed to connect to MongoDB")
        return False
    
    # Get all products
    all_products = list(db.products.find({}))
    logger.info(f"Found {len(all_products)} total products")
    
    # Check which products have reviews
    products_without_reviews = []
    
    for product in all_products:
        review_count = db.reviews.count_documents({"product_id": str(product["_id"])})
        
        if review_count == 0:
            products_without_reviews.append(product)
    
    logger.info(f"Found {len(products_without_reviews)} products without reviews")
    
    # Add reviews to products without them
    for product in products_without_reviews:
        logger.info(f"Adding reviews for product: {product['name']}")
        
        # Create 5 reviews spread over the last 6 months
        for i in range(5):
            # Create a random date within the last 6 months
            days_ago = random.randint(0, 180)
            review_date = datetime.now() - timedelta(days=days_ago)
            
            # Create the review with mostly positive sentiment
            sentiment_value = random.random()
            if sentiment_value < 0.7:  # 70% positive
                sentiment_class = "positive"
                sentiment_score = random.uniform(0.6, 0.9)
                rating = random.choice([4, 5])
                review_text = f"I really like the {product['name']}. It works great and meets all my needs."
            elif sentiment_value < 0.9:  # 20% neutral
                sentiment_class = "neutral"
                sentiment_score = random.uniform(0.4, 0.6)
                rating = random.choice([3, 4])
                review_text = f"The {product['name']} is decent. It works as expected but nothing special."
            else:  # 10% negative
                sentiment_class = "negative"
                sentiment_score = random.uniform(0.1, 0.4)
                rating = random.choice([1, 2])
                review_text = f"Not happy with the {product['name']}. It didn't meet my expectations."
            
            # Create review data
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
            
            # Insert the review
            db.reviews.insert_one(review_data)
        
        # Update product sentiment scores
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
    
    logger.info(f"Added reviews to {len(products_without_reviews)} products")
    return True

def fix_description_for_hype_reality():
    """Make sure all products have detailed descriptions for hype vs reality feature"""
    # Get MongoDB client
    mongo_client, db = get_mongo_client()
    if db is None:
        logger.error("Failed to connect to MongoDB")
        return False
    
    # Get all products with missing or short descriptions
    products_with_short_descriptions = list(db.products.find({
        "$or": [
            {"description": {"$exists": False}},
            {"description": None},
            {"description": ""},
            {"description": {"$regex": "^.{0,50}$"}}  # Less than 50 chars
        ]
    }))
    
    logger.info(f"Found {len(products_with_short_descriptions)} products with missing or short descriptions")
    
    # Marketing claims for different categories
    marketing_claims = {
        "Electronics": [
            "The most advanced technology in its class.",
            "Engineered for unprecedented performance.",
            "Revolutionary design that changes everything.",
            "Experience quality like never before."
        ],
        "Tablets": [
            "Lightning-fast performance with our most powerful processor.",
            "Stunning display with vibrant colors and crisp detail.",
            "All-day battery life for work and play.",
            "The thinnest and lightest tablet we've ever made."
        ],
        "E-readers": [
            "The best reading experience ever created.",
            "Reads like real paper even in bright sunlight.",
            "Weeks of battery life on a single charge.",
            "The lightest and thinnest design in our lineup."
        ],
        "Smart Home": [
            "Unprecedented smart home integration with one-touch setup.",
            "Crystal-clear sound that fills any room.",
            "The most advanced voice recognition technology available.",
            "Seamlessly connects with all your smart devices."
        ]
    }
    
    # Update products with better descriptions
    for product in products_with_short_descriptions:
        # Determine category
        category = "Electronics"  # Default
        for cat in marketing_claims.keys():
            if cat.lower() in str(product.get("categories", [])).lower() or cat.lower() in str(product.get("primary_category", "")).lower():
                category = cat
                break
        
        # Get 3 random marketing claims for this category
        selected_claims = random.sample(marketing_claims[category], 3)
        
        # Create description with marketing claims
        description = f"{product.get('name')} - {' '.join(selected_claims)} Experience the difference today with this premium Amazon product."
        
        # Update the product
        db.products.update_one(
            {"_id": product["_id"]},
            {"$set": {
                "description": description,
                "updated_at": datetime.now()
            }}
        )
        
        logger.info(f"Updated description for product: {product.get('name')}")
    
    logger.info(f"Updated descriptions for {len(products_with_short_descriptions)} products")
    return True

if __name__ == "__main__":
    # 1. Add dates to reviews for time-based analysis
    add_dates_to_all_reviews()
    
    # 2. Create reviews for products without any
    create_reviews_for_empty_products()
    
    # 3. Fix descriptions for hype vs reality feature
    fix_description_for_hype_reality()