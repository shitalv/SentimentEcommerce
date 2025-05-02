"""
Fix Admin User Script

This script ensures the user with username 'admin' has is_admin set to True.
"""

import logging
from mongo_config import get_mongo_client

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_admin_user():
    """Set is_admin=True for the user with username 'admin'"""
    try:
        mongo_client, db = get_mongo_client()
        if db is None:
            logger.error("Failed to connect to MongoDB")
            return False
        
        # Update the admin user
        result = db.users.update_one(
            {"username": "admin"},
            {"$set": {"is_admin": True}}
        )
        
        if result.matched_count > 0:
            logger.info(f"Successfully set is_admin=True for user 'admin'")
            return True
        else:
            logger.warning(f"No user with username 'admin' found")
            return False
    
    except Exception as e:
        logger.error(f"Error updating admin user: {str(e)}")
        return False

if __name__ == "__main__":
    fix_admin_user()