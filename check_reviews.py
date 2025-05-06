"""
Check Reviews

This script checks the reviews in the database to verify that our diverse reviews were added.
"""
import logging
from mongo_config import get_mongo_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_reviews():
    """Check reviews in the database"""
    client, db = get_mongo_client()
    
    if db is None:
        logger.error("MongoDB database not available")
        return
    
    # Count reviews by sentiment class
    positive_count = db["reviews"].count_documents({"sentiment_class": "positive"})
    neutral_count = db["reviews"].count_documents({"sentiment_class": "neutral"})
    negative_count = db["reviews"].count_documents({"sentiment_class": "negative"})
    
    total_reviews = db["reviews"].count_documents({})
    system_reviews = db["reviews"].count_documents({"user_id": "system_generated"})
    
    logger.info(f"Total reviews: {total_reviews}")
    logger.info(f"System-generated reviews: {system_reviews}")
    logger.info(f"Positive reviews: {positive_count}")
    logger.info(f"Neutral reviews: {neutral_count}")
    logger.info(f"Negative reviews: {negative_count}")
    
    # Get products with reviews
    products_with_reviews = db["reviews"].distinct("product_id")
    logger.info(f"Number of products with reviews: {len(products_with_reviews)}")
    
    # Get most recent reviews
    recent_reviews = list(db["reviews"].find({}).sort("date", -1).limit(5))
    logger.info("Most recent reviews:")
    for review in recent_reviews:
        logger.info(f"Date: {review.get('date')}, Sentiment: {review.get('sentiment_class')}, Score: {review.get('sentiment_score')}")

if __name__ == "__main__":
    check_reviews()