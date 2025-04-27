"""
Check MongoDB Data

This script checks if we have products and reviews in the MongoDB database.
"""

import logging
from mongo_config import get_mongo_client

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('mongo_data_check')

def main():
    # Get MongoDB client
    mongo_client, db = get_mongo_client()
    if db is None:
        logger.error("Failed to connect to MongoDB")
        return
    
    # Check for products
    product_count = db.products.count_documents({})
    logger.info(f"Found {product_count} products in the database")
    
    # Check for reviews
    review_count = db.reviews.count_documents({})
    logger.info(f"Found {review_count} reviews in the database")
    
    # List some products
    logger.info("Here are the first 5 products:")
    for product in db.products.find().limit(5):
        logger.info(f"Product: {product.get('name')} (ASIN: {product.get('asin')})")
        logger.info(f"  Category: {product.get('category')}")
        logger.info(f"  Sentiment score: {product.get('sentiment_score')}")

if __name__ == "__main__":
    main()