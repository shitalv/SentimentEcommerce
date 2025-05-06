"""
Add Diverse Review Data with Significant Shifts

This script adds reviews with varying sentiment scores to create more
diverse data for the time-based analysis features to work with. It deliberately
creates shifts in sentiment over time to demonstrate the sentiment shift detection.
"""
import datetime
import random
import logging
from mongo_config import get_mongo_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_diverse_reviews_with_shifts():
    """Add reviews with clear shifts in sentiment over time periods"""
    client, db = get_mongo_client()
    
    if db is None:
        logger.error("MongoDB database not available")
        return False
    
    # First, clean up any previously generated test data
    result = db["reviews"].delete_many({"user_id": "system_generated"})
    logger.info(f"Removed {result.deleted_count} previously generated test reviews")
    
    # Get all products
    products = list(db["products"].find({}, {"_id": 1, "name": 1}))
    
    if not products:
        logger.error("No products found in database")
        return False
    
    logger.info(f"Found {len(products)} products in database")
    
    # Select products to add diverse reviews to
    selected_products = products[:5]  # Use first 5 products
    logger.info(f"Selected {len(selected_products)} products for diverse reviews")
    
    today = datetime.datetime.now()
    review_count = 0
    
    # Just focus on one product for quick testing
    if selected_products:
        product = selected_products[0]
        product_id = str(product["_id"])
        product_name = product["name"]
        
        logger.info(f"Adding reviews with shifts for product: {product_name} (ID: {product_id})")
        
        # Time period 1 (30-20 days ago): Mostly positive reviews
        period1_start = today - datetime.timedelta(days=30)
        period1_end = today - datetime.timedelta(days=20)
        
        # Add 6 positive reviews in this period
        for _ in range(6):
            review_date = random_date(period1_start, period1_end)
            review = create_review(product_id, product_name, "positive", review_date)
            db["reviews"].insert_one(review)
            review_count += 1
        
        # Add a few neutral and negative for realism
        for _ in range(2):
            review_date = random_date(period1_start, period1_end)
            review = create_review(product_id, product_name, "neutral", review_date)
            db["reviews"].insert_one(review)
            review_count += 1
            
        for _ in range(1):
            review_date = random_date(period1_start, period1_end)
            review = create_review(product_id, product_name, "negative", review_date)
            db["reviews"].insert_one(review)
            review_count += 1
        
        # Time period 2 (20-10 days ago): Shift to more negative reviews
        period2_start = today - datetime.timedelta(days=20)
        period2_end = today - datetime.timedelta(days=10)
        
        # Add 6 negative reviews in this period (significant shift)
        for _ in range(6):
            review_date = random_date(period2_start, period2_end)
            review = create_review(product_id, product_name, "negative", review_date)
            db["reviews"].insert_one(review)
            review_count += 1
        
        # Add a few positive and neutral for realism
        for _ in range(2):
            review_date = random_date(period2_start, period2_end)
            review = create_review(product_id, product_name, "positive", review_date)
            db["reviews"].insert_one(review)
            review_count += 1
            
        for _ in range(1):
            review_date = random_date(period2_start, period2_end)
            review = create_review(product_id, product_name, "neutral", review_date)
            db["reviews"].insert_one(review)
            review_count += 1
        
        # Time period 3 (10-0 days ago): Recovery to mixed reviews
        period3_start = today - datetime.timedelta(days=10)
        period3_end = today
        
        # Add mixed reviews with slight positive trend
        for _ in range(4):
            review_date = random_date(period3_start, period3_end)
            review = create_review(product_id, product_name, "positive", review_date)
            db["reviews"].insert_one(review)
            review_count += 1
            
        for _ in range(3):
            review_date = random_date(period3_start, period3_end)
            review = create_review(product_id, product_name, "neutral", review_date)
            db["reviews"].insert_one(review)
            review_count += 1
            
        for _ in range(2):
            review_date = random_date(period3_start, period3_end)
            review = create_review(product_id, product_name, "negative", review_date)
            db["reviews"].insert_one(review)
            review_count += 1
    
    logger.info(f"Added {review_count} reviews with clear sentiment shifts for time-based analysis")
    return True

def random_date(start, end):
    """Generate a random date between start and end dates"""
    delta = end - start
    random_days = random.randrange(delta.days)
    return start + datetime.timedelta(days=random_days)

def create_review(product_id, product_name, sentiment_class, date):
    """Create a review with appropriate sentiment score and text based on class"""
    # Determine sentiment score based on class with some variation
    if sentiment_class == "positive":
        sentiment_score = random.uniform(0.65, 0.95)
        texts = [
            f"I absolutely love my {product_name}! It's been working perfectly.",
            f"This {product_name} is fantastic. Best purchase I've made in a long time.",
            f"Really impressed with the quality of this {product_name}.",
            f"The {product_name} exceeded all my expectations. Highly recommend!",
            f"Great product, great value. This {product_name} is worth every penny."
        ]
    elif sentiment_class == "neutral":
        sentiment_score = random.uniform(0.4, 0.6)
        texts = [
            f"The {product_name} is okay. Nothing special but it works.",
            f"Average product. The {product_name} does what it's supposed to do.",
            f"Neither impressed nor disappointed with this {product_name}.",
            f"The {product_name} is decent. Not amazing, not terrible.",
            f"Got what I expected with this {product_name}. It's fine."
        ]
    else:  # negative
        sentiment_score = random.uniform(0.05, 0.35)
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
    add_diverse_reviews_with_shifts()