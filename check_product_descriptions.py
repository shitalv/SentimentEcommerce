"""
Check Product Descriptions

This script checks the descriptions of products in the database.
"""

import logging
import json
from mongo_config import get_mongo_client

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('check_product_descriptions')

def check_product_descriptions():
    """Check descriptions of products in the database"""
    # Get MongoDB client
    mongo_client, db = get_mongo_client()
    if db is None:
        logger.error("Failed to connect to MongoDB")
        return False
    
    try:
        # Get all products
        products = list(db.products.find())
        logger.info(f"Found {len(products)} products in the database")
        
        for product in products:
            # Extract product info
            product_name = product.get('name', 'Unknown')
            product_description = product.get('description', 'No description')
            
            # Trim long descriptions for readability
            if product_description and len(product_description) > 100:
                product_description = product_description[:100] + "..."
            
            # Log product info
            logger.info(f"Product: {product_name}")
            logger.info(f"  Description: {product_description}")
            logger.info("-" * 80)
        
        return True
    
    except Exception as e:
        logger.error(f"Error checking product descriptions: {str(e)}")
        return False

if __name__ == "__main__":
    if check_product_descriptions():
        logger.info("Product descriptions checked successfully")
    else:
        logger.error("Failed to check product descriptions")