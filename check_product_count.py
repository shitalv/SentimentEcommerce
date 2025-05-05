"""
Check Product Count

This script checks the number of products and reviews in the MongoDB database.
"""

import logging
import sys
import os

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('check_product_count')

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import MongoDB utils
from mongo_config import get_mongo_client

def check_counts():
    """Check the number of products and reviews in the database"""
    # Get MongoDB client
    mongo_client, db = get_mongo_client()
    if db is None:
        logger.error("Failed to connect to MongoDB")
        return
    
    # Count products
    product_count = db.products.count_documents({})
    logger.info(f"Total products in database: {product_count}")
    
    # Count reviews
    review_count = db.reviews.count_documents({})
    logger.info(f"Total reviews in database: {review_count}")
    
    # List all products with their review counts
    logger.info("\nProducts and their review counts:")
    products = list(db.products.find({}, {"name": 1, "asin": 1}))
    
    for product in products:
        product_id = str(product["_id"])
        product_reviews = db.reviews.count_documents({"product_id": product_id})
        logger.info(f"- {product['name']} (ASIN: {product.get('asin', 'N/A')}): {product_reviews} reviews")
    
    return {
        "product_count": product_count,
        "review_count": review_count,
        "products": products
    }

if __name__ == "__main__":
    check_counts()