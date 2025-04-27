"""
Create Admin User Script

This script creates an admin user in the database for testing the admin dashboard.
"""

import sys
import logging
from datetime import datetime
from werkzeug.security import generate_password_hash
from bson.objectid import ObjectId

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import from app context
try:
    from mongo_config import get_mongo_client
except ImportError:
    logger.error("Failed to import mongo_config. Make sure you're running this from the project root.")
    sys.exit(1)

def create_admin_user(username, email, password):
    """Create an admin user in the database"""
    try:
        # Connect to MongoDB
        mongo_client, db = get_mongo_client()
        if db is None:
            logger.error("Failed to connect to MongoDB")
            return False
        
        # Check if user already exists
        existing_user = db.users.find_one({"$or": [{"username": username}, {"email": email}]})
        if existing_user:
            logger.info(f"User {username} or email {email} already exists.")
            
            # Make the user an admin if they're not already
            if not existing_user.get("is_admin", False):
                db.users.update_one(
                    {"_id": existing_user["_id"]},
                    {"$set": {"is_admin": True}}
                )
                logger.info(f"Made existing user {username} an admin.")
            else:
                logger.info(f"User {username} is already an admin.")
                
            return True
            
        # Create new admin user
        user_data = {
            "_id": ObjectId(),
            "username": username,
            "email": email,
            "password_hash": generate_password_hash(password),
            "created_at": datetime.utcnow(),
            "is_admin": True
        }
        
        # Insert the user into the database
        db.users.insert_one(user_data)
        logger.info(f"Created new admin user: {username}")
        
        return True
    
    except Exception as e:
        logger.error(f"Error creating admin user: {str(e)}")
        return False

if __name__ == "__main__":
    # Default admin credentials
    admin_username = "admin"
    admin_email = "admin@example.com"
    admin_password = "admin123"
    
    # Allow command-line arguments for custom credentials
    if len(sys.argv) > 1:
        admin_username = sys.argv[1]
    if len(sys.argv) > 2:
        admin_email = sys.argv[2]
    if len(sys.argv) > 3:
        admin_password = sys.argv[3]
    
    # Create the admin user
    logger.info(f"Creating admin user: {admin_username} <{admin_email}>")
    success = create_admin_user(admin_username, admin_email, admin_password)
    
    if success:
        logger.info("Admin user created or updated successfully.")
    else:
        logger.error("Failed to create admin user.")