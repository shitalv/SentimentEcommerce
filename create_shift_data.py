"""
Create Target Product Data with Clear Shifts

This script creates a set of reviews with very clear sentiment shifts 
for a specific product to demonstrate the time-based analysis functionality.
"""
import datetime
import random
import logging
from mongo_config import get_mongo_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_shift_data():
    """Create reviews data with clear sentiment shifts for time-based analysis"""
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
    
    logger.info(f"Creating sentiment shift data for product: {product_name} (ID: {product_id})")
    
    # First, clean up any existing test reviews for this product
    db["reviews"].delete_many({"product_id": product_id, "user_id": "system_generated"})
    
    # Create dates with explicit 3-day periods to ensure reviews fall within our analysis windows
    today = datetime.datetime.now()
    
    # Create very explicit sentiment shifts with dense data
    data_structure = [
        # Week 1 (very positive)
        {"start_day": 21, "end_day": 18, "sentiment": "positive", "count": 10},
        {"start_day": 18, "end_day": 15, "sentiment": "positive", "count": 10},
        
        # Week 2 (transition to negative - THE SHIFT)
        {"start_day": 15, "end_day": 12, "sentiment": "neutral", "count": 10},
        {"start_day": 12, "end_day": 9, "sentiment": "negative", "count": 10},
        
        # Week 3 (very negative)
        {"start_day": 9, "end_day": 6, "sentiment": "negative", "count": 10},
        {"start_day": 6, "end_day": 3, "sentiment": "negative", "count": 10},
        
        # Most recent days (recovering to positive - ANOTHER SHIFT)
        {"start_day": 3, "end_day": 0, "sentiment": "positive", "count": 10},
    ]
    
    total_count = 0
    
    # Create reviews for each period
    for period in data_structure:
        start_date = today - datetime.timedelta(days=period["start_day"])
        end_date = today - datetime.timedelta(days=period["end_day"])
        sentiment = period["sentiment"]
        count = period["count"]
        
        logger.info(f"Adding {count} {sentiment} reviews from {start_date.date()} to {end_date.date()}")
        
        for i in range(count):
            # Distribute evenly within the period
            days_range = (period["start_day"] - period["end_day"])
            point = period["start_day"] - (i * days_range / count)
            review_date = today - datetime.timedelta(days=point)
            
            # Create sentiment values with clear separation
            if sentiment == "positive":
                sentiment_score = random.uniform(0.80, 0.95)
                sentiment_class = "positive"
            elif sentiment == "neutral":
                sentiment_score = random.uniform(0.45, 0.55)
                sentiment_class = "neutral"
            else:  # negative
                sentiment_score = random.uniform(0.05, 0.20)
                sentiment_class = "negative"
            
            # Create review text with appropriate sentiment
            if sentiment == "positive":
                text = f"Excellent {product_name}! I'm very happy with this purchase."
            elif sentiment == "neutral":
                text = f"The {product_name} is just okay. Neither great nor terrible."
            else:
                text = f"Disappointed with this {product_name}. Would not recommend."
            
            # Add the review
            review = {
                "product_id": product_id,
                "text": text,
                "sentiment_score": sentiment_score,
                "sentiment_class": sentiment_class,
                "date": review_date,
                "user_id": "system_generated"
            }
            
            db["reviews"].insert_one(review)
            total_count += 1
    
    logger.info(f"Created {total_count} reviews with clear sentiment shifts for {product_name}")
    logger.info(f"To see results:")
    logger.info(f"1. Go to Time-Based Analysis")
    logger.info(f"2. Select product ID: {product_id}")
    logger.info(f"3. Set period to 30 days")
    logger.info(f"4. Set granularity to week")
    
    # Save product ID to a file for future reference
    with open("target_product.txt", "w") as f:
        f.write(f"Product ID: {product_id}\nProduct Name: {product_name}")
    
    return product_id

if __name__ == "__main__":
    create_shift_data()