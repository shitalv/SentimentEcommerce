"""
Add Product Sentiment Shifts

This script adds reviews to a specific product with clear sentiment shifts 
over time to demonstrate the time-based analysis feature.
"""
import datetime
import random
import logging
from mongo_config import get_mongo_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# The product ID to add reviews to - will be overwritten with actual product ID
TARGET_PRODUCT_ID = None 

def add_product_sentiment_shifts():
    """Add reviews to a specific product with clear sentiment shifts"""
    client, db = get_mongo_client()
    
    if db is None:
        logger.error("MongoDB database not available")
        return False
        
    # Get the first product to use
    products = list(db["products"].find({}, {"_id": 1, "name": 1}).limit(1))
    if not products:
        logger.error("No products found in database")
        return False
        
    product = products[0]
    product_id = str(product["_id"])
    product_name = product["name"]
    
    logger.info(f"Adding sentiment shifts for product: {product_name} (ID: {product_id})")
    
    # Remove existing system-generated reviews for this product
    db["reviews"].delete_many({"product_id": product_id, "user_id": "system_generated"})
    
    # Define time periods with different sentiment patterns
    today = datetime.datetime.now()
    
    # Time periods with clear shifts
    periods = [
        {
            "name": "Initial positive period",
            "start": today - datetime.timedelta(days=21),
            "end": today - datetime.timedelta(days=14),
            "sentiment_distribution": {"positive": 0.8, "neutral": 0.1, "negative": 0.1},
            "reviews_count": 15
        },
        {
            "name": "Negative shift period",
            "start": today - datetime.timedelta(days=14),
            "end": today - datetime.timedelta(days=7),
            "sentiment_distribution": {"positive": 0.1, "neutral": 0.2, "negative": 0.7},
            "reviews_count": 15
        },
        {
            "name": "Recovery period",
            "start": today - datetime.timedelta(days=7),
            "end": today,
            "sentiment_distribution": {"positive": 0.6, "neutral": 0.3, "negative": 0.1},
            "reviews_count": 15
        }
    ]
    
    # Add reviews for each period
    total_added = 0
    for period in periods:
        logger.info(f"Adding reviews for period: {period['name']}")
        for _ in range(period["reviews_count"]):
            # Choose sentiment based on distribution
            r = random.random()
            cumulative = 0
            chosen_sentiment = "neutral"  # default
            
            for sentiment, prob in period["sentiment_distribution"].items():
                cumulative += prob
                if r <= cumulative:
                    chosen_sentiment = sentiment
                    break
                    
            # Generate a random date within the period
            delta = period["end"] - period["start"]
            random_days = random.random() * delta.days
            review_date = period["start"] + datetime.timedelta(days=random_days)
            
            # Create the review
            review = create_review(product_id, product_name, chosen_sentiment, review_date)
            db["reviews"].insert_one(review)
            total_added += 1
    
    logger.info(f"Added {total_added} reviews with clear sentiment shifts for product {product_name}")
    
    # Save the product ID to a global variable for future reference
    global TARGET_PRODUCT_ID
    TARGET_PRODUCT_ID = product_id
    
    # Print how to access this product in the time-based analysis
    logger.info(f"\nTo see the sentiment shifts:")
    logger.info(f"1. Go to the Time-Based Analysis report")
    logger.info(f"2. Select this product ID: {product_id}")
    logger.info(f"3. Change the period to 30 days")
    logger.info(f"4. Change granularity to week")
    
    return True

def create_review(product_id, product_name, sentiment_class, date):
    """Create a review with appropriate sentiment score and text based on class"""
    # Determine sentiment score based on class with more extreme values for clarity
    if sentiment_class == "positive":
        sentiment_score = random.uniform(0.75, 0.95)
        texts = [
            f"I absolutely love my {product_name}! It's been working perfectly.",
            f"This {product_name} is fantastic. Best purchase I've made in a long time.",
            f"Really impressed with the quality of this {product_name}.",
            f"The {product_name} exceeded all my expectations. Highly recommend!",
            f"Great product, great value. This {product_name} is worth every penny."
        ]
    elif sentiment_class == "neutral":
        sentiment_score = random.uniform(0.45, 0.55)
        texts = [
            f"The {product_name} is okay. Nothing special but it works.",
            f"Average product. The {product_name} does what it's supposed to do.",
            f"Neither impressed nor disappointed with this {product_name}.",
            f"The {product_name} is decent. Not amazing, not terrible.",
            f"Got what I expected with this {product_name}. It's fine."
        ]
    else:  # negative
        sentiment_score = random.uniform(0.05, 0.25)
        texts = [
            f"Not happy with this {product_name}. Wouldn't recommend it.",
            f"The {product_name} broke after just a few uses. Very disappointed.",
            f"Poor quality product. This {product_name} isn't worth the money.",
            f"Frustrated with my purchase of this {product_name}.",
            f"Returning this {product_name}. It doesn't work as advertised."
        ]
    
    # Choose a random text from the options
    review_text = random.choice(texts)
    
    # Return the review object
    return {
        "product_id": product_id,
        "text": review_text,
        "sentiment_score": sentiment_score,
        "sentiment_class": sentiment_class,
        "date": date,
        "user_id": "system_generated",
    }

if __name__ == "__main__":
    add_product_sentiment_shifts()