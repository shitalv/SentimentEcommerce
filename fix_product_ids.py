"""
Quick Fix for Product IDs in Reviews

This script ensures product_id field in reviews is in the correct format.
"""

import logging
from mongo_config import get_mongo_client
from bson import ObjectId

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_product_ids():
    """Fix the product_id field in reviews to ensure it's consistent"""
    # Get MongoDB client
    mongo_client, db = get_mongo_client()
    if db is None:
        logger.error("Failed to connect to MongoDB")
        return

    # Get all reviews
    reviews = list(db.reviews.find())
    logger.info(f"Found {len(reviews)} reviews")

    # Count issues
    string_ids = 0
    object_ids = 0
    non_objectid_strings = 0
    
    # First, see what we have
    for review in reviews:
        product_id = review.get("product_id")
        if isinstance(product_id, str):
            string_ids += 1
            try:
                # Check if it's a valid ObjectId string
                ObjectId(product_id)
            except:
                non_objectid_strings += 1
        elif isinstance(product_id, ObjectId):
            object_ids += 1
    
    logger.info(f"String IDs: {string_ids}, ObjectId instances: {object_ids}, Non-ObjectId strings: {non_objectid_strings}")
    
    # Now fix any issues
    updated = 0
    
    for review in reviews:
        product_id = review.get("product_id")
        
        if isinstance(product_id, ObjectId):
            # Convert to string for consistency
            db.reviews.update_one(
                {"_id": review["_id"]},
                {"$set": {"product_id": str(product_id)}}
            )
            updated += 1
        elif isinstance(product_id, str):
            try:
                # Just try to validate it's a proper ObjectId string
                ObjectId(product_id)
                # It's valid, no need to change
            except:
                logger.warning(f"Invalid product_id format: {product_id}")
                # Try to find product by name if available
                product_name = review.get("product_name")
                if product_name:
                    product = db.products.find_one({"name": product_name})
                    if product:
                        db.reviews.update_one(
                            {"_id": review["_id"]},
                            {"$set": {"product_id": str(product["_id"])}}
                        )
                        updated += 1
                        logger.info(f"Fixed product_id for review of {product_name}")
    
    logger.info(f"Updated {updated} reviews with corrected product_id format")

if __name__ == "__main__":
    fix_product_ids()