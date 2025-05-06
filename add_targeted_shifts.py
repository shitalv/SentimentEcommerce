"""
Add Targeted Shift Pattern

This script adds a very specific pattern of reviews to show clear sentiment shifts.
It uses direct MongoDB insertion for speed and efficiency.
"""
import datetime
import random
import logging
from mongo_config import get_mongo_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def add_targeted_shift_pattern():
    """Add a specific pattern of reviews to clearly show sentiment shifts"""
    client, db = get_mongo_client()
    
    if db is None:
        logger.error("MongoDB database not available")
        return
    
    # Get a specific product - using the first one for simplicity
    products = list(db["products"].find().limit(1))
    if not products:
        logger.error("No products found in database")
        return
    
    product = products[0]
    product_id = str(product["_id"])
    product_name = product["name"]
    
    logger.info(f"Adding targeted shift pattern for product: {product_name} (ID: {product_id})")
    
    # Clear existing system-generated reviews for this product
    result = db["reviews"].delete_many({"product_id": product_id, "user_id": "system_generated"})
    logger.info(f"Removed {result.deleted_count} previous reviews for this product")
    
    # Today's date
    today = datetime.datetime.now()
    
    # Create pattern with exact dates: positive → negative → positive
    pattern = [
        # Week 3: Strongly positive (18-21 days ago)
        {"days_ago": 21, "sentiment": "positive", "count": 5},
        {"days_ago": 20, "sentiment": "positive", "count": 5},
        {"days_ago": 19, "sentiment": "positive", "count": 5},
        {"days_ago": 18, "sentiment": "positive", "count": 5},
        
        # Week 2: Major negative shift (10-14 days ago)
        {"days_ago": 14, "sentiment": "negative", "count": 5},
        {"days_ago": 13, "sentiment": "negative", "count": 5},
        {"days_ago": 12, "sentiment": "negative", "count": 5},
        {"days_ago": 11, "sentiment": "negative", "count": 5},
        {"days_ago": 10, "sentiment": "negative", "count": 5},
        
        # Week 1: Recovery to positive (recent 7 days)
        {"days_ago": 7, "sentiment": "positive", "count": 5},
        {"days_ago": 5, "sentiment": "positive", "count": 5},
        {"days_ago": 3, "sentiment": "positive", "count": 5},
        {"days_ago": 1, "sentiment": "positive", "count": 5},
    ]
    
    reviews_to_insert = []
    total_count = 0
    
    # Generate reviews based on pattern
    for item in pattern:
        days_ago = item["days_ago"]
        sentiment = item["sentiment"]
        count = item["count"]
        
        date = today - datetime.timedelta(days=days_ago)
        date_str = date.strftime("%Y-%m-%d")
        
        logger.info(f"Adding {count} {sentiment} reviews for {date_str}")
        
        for i in range(count):
            # Create sentiment values with clear separation
            if sentiment == "positive":
                sentiment_score = 0.9  # Very high for clarity
                sentiment_class = "positive"
                text = f"Excellent {product_name}! Very happy with my purchase."
            elif sentiment == "neutral":
                sentiment_score = 0.5
                sentiment_class = "neutral"
                text = f"The {product_name} is okay. Nothing special."
            else:  # negative
                sentiment_score = 0.1  # Very low for clarity
                sentiment_class = "negative"
                text = f"Very disappointed with this {product_name}. Do not recommend."
            
            # Add small random variation
            sentiment_score += random.uniform(-0.05, 0.05)
            sentiment_score = max(0.01, min(0.99, sentiment_score))
            
            # Spread reviews throughout the day
            hour_offset = random.randint(0, 23)
            minute_offset = random.randint(0, 59)
            review_date = datetime.datetime(
                date.year, date.month, date.day, 
                hour_offset, minute_offset
            )
            
            # Add the review
            review = {
                "product_id": product_id,
                "text": text,
                "sentiment_score": sentiment_score,
                "sentiment_class": sentiment_class,
                "date": review_date,
                "user_id": "system_generated"
            }
            
            reviews_to_insert.append(review)
            total_count += 1
    
    # Bulk insert for efficiency
    if reviews_to_insert:
        db["reviews"].insert_many(reviews_to_insert)
    
    logger.info(f"Added {total_count} reviews with clear sentiment shifts for {product_name}")
    logger.info(f"To see the shifts:")
    logger.info(f"1. Go to Time-Based Analysis")
    logger.info(f"2. Select product ID: {product_id}")
    logger.info(f"3. Set period to 30 days")
    logger.info(f"4. Set granularity to week")
    
    # Save details to a file
    with open("target_product.txt", "w") as f:
        f.write(f"Product ID: {product_id}\n")
        f.write(f"Product Name: {product_name}\n")
        f.write(f"Total reviews added: {total_count}\n")
    
    return product_id

if __name__ == "__main__":
    add_targeted_shift_pattern()