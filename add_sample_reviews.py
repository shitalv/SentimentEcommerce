"""
Add Sample Reviews

This script adds sample reviews to products that don't have any reviews yet.
"""

import logging
import sys
import os
import json
from datetime import datetime, timedelta
import random
from bson import ObjectId

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('add_sample_reviews')

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import MongoDB utils
from mongo_config import get_mongo_client
from backend.sentiment_analyzer import analyze_sentiment, classify_sentiment, get_sentiment_keywords

def generate_review_text(product_name, sentiment):
    """Generate sample review text based on sentiment"""
    # Positive reviews
    positive_templates = [
        f"I absolutely love my {product_name}! It exceeds all my expectations and works perfectly.",
        f"This {product_name} is fantastic. The quality is outstanding and it's very user-friendly.",
        f"Best purchase I've made in a long time! The {product_name} is worth every penny.",
        f"Really impressed with the {product_name}. Easy to use and very reliable.",
        f"Five stars for the {product_name}! It's exactly what I needed and works great."
    ]
    
    # Neutral reviews
    neutral_templates = [
        f"The {product_name} is okay. It does what it's supposed to do, nothing special.",
        f"Got the {product_name} a few weeks ago. It's decent but not mind-blowing.",
        f"Average product. The {product_name} meets basic expectations but has some room for improvement.",
        f"The {product_name} is fine for the price. Not amazing but gets the job done.",
        f"So far the {product_name} is working as expected. No issues but nothing exceptional either."
    ]
    
    # Negative reviews
    negative_templates = [
        f"Disappointed with the {product_name}. It doesn't work as advertised and feels cheaply made.",
        f"Had issues with my {product_name} right out of the box. Would not recommend.",
        f"The {product_name} broke after just a few weeks. Save your money and look elsewhere.",
        f"Not happy with this purchase. The {product_name} is difficult to use and unreliable.",
        f"Returning my {product_name}. Poor quality and doesn't perform as it should."
    ]
    
    if sentiment == "positive":
        return random.choice(positive_templates)
    elif sentiment == "neutral":
        return random.choice(neutral_templates)
    else:  # negative
        return random.choice(negative_templates)

def add_sample_reviews():
    """Add sample reviews to products that don't have any"""
    # Get MongoDB client
    mongo_client, db = get_mongo_client()
    if db is None:
        logger.error("Failed to connect to MongoDB")
        return False
    
    # Get all products
    products = list(db.products.find({}))
    logger.info(f"Found {len(products)} products in database")
    
    reviews_added = 0
    products_updated = 0
    
    for product in products:
        # Check if product has reviews
        review_count = db.reviews.count_documents({"product_id": str(product["_id"])})
        
        if review_count > 0:
            logger.info(f"Product '{product['name']}' already has {review_count} reviews, skipping")
            continue
        
        logger.info(f"Adding reviews for product: {product['name']}")
        
        # Generate sample reviews with different sentiments
        # Distribution: 70% positive, 20% neutral, 10% negative
        sentiment_distribution = {
            "positive": 7,
            "neutral": 2,
            "negative": 1
        }
        
        # Base date for reviews (spread over last 6 months)
        base_date = datetime.now() - timedelta(days=180)
        
        for sentiment, count in sentiment_distribution.items():
            for i in range(count):
                # Generate review text
                review_text = generate_review_text(product['name'], sentiment)
                
                # Generate rating based on sentiment
                if sentiment == "positive":
                    rating = random.choice([4, 5])
                elif sentiment == "neutral":
                    rating = random.choice([3, 4])
                else:  # negative
                    rating = random.choice([1, 2])
                
                # Generate random date within last 6 months
                days_ago = random.randint(0, 180)
                review_date = base_date + timedelta(days=days_ago)
                
                # Create review data
                review_data = {
                    "product_id": str(product["_id"]),
                    "author": f"User{random.randint(100, 999)}",
                    "title": f"{rating}-Star Review",
                    "text": review_text,
                    "rating": rating,
                    "date": review_date,
                    "created_at": datetime.now()
                }
                
                # Add sentiment analysis
                sentiment_score = analyze_sentiment(review_text)
                review_data["sentiment_score"] = sentiment_score
                review_data["sentiment_class"] = classify_sentiment(sentiment_score)
                
                # Extract keywords
                keywords = get_sentiment_keywords(review_text, sentiment_score)
                review_data["sentiment_keywords"] = json.dumps(keywords)
                
                # Insert review
                db.reviews.insert_one(review_data)
                reviews_added += 1
        
        # Update product sentiment scores
        product_reviews = list(db.reviews.find({"product_id": str(product["_id"])}))
        
        if product_reviews:
            # Calculate sentiment counts
            positive_count = sum(1 for r in product_reviews if r.get("sentiment_class") == "positive")
            neutral_count = sum(1 for r in product_reviews if r.get("sentiment_class") == "neutral")
            negative_count = sum(1 for r in product_reviews if r.get("sentiment_class") == "negative")
            total_count = len(product_reviews)
            
            # Calculate average sentiment score
            avg_score = sum(r.get("sentiment_score", 0.5) for r in product_reviews) / total_count
            
            # Update product
            db.products.update_one(
                {"_id": product["_id"]},
                {"$set": {
                    "positive_score": positive_count / total_count,
                    "neutral_score": neutral_count / total_count,
                    "negative_score": negative_count / total_count,
                    "sentiment_score": avg_score,
                    "updated_at": datetime.now()
                }}
            )
            products_updated += 1
    
    logger.info(f"Added {reviews_added} sample reviews to {products_updated} products")
    return True

if __name__ == "__main__":
    add_sample_reviews()