"""
Add Product Descriptions

This script adds detailed product descriptions to existing products in the database.
These descriptions contain marketing claims that will be used by the Hype vs. Reality feature.
"""

import logging
import json
from datetime import datetime
from mongo_config import get_mongo_client

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('add_product_descriptions')

# Dictionary of product descriptions with marketing claims for common product types
PRODUCT_DESCRIPTIONS = {
    "kindle": {
        "description": """The all-new Kindle e-reader is our best yet, featuring a high-resolution display with excellent contrast for crisp, clear text. The perfect reading experience with no screen glare, even in bright sunlight. 
        With innovative built-in adjustable light for reading day and night. Enjoy a fantastic battery life that lasts for weeks on a single charge. Lightweight and comfortable to hold for hours of effortless reading.
        Our advanced page-turning technology makes navigation intuitive and responsive. The perfect companion for book lovers!"""
    },
    "echo": {
        "description": """Experience the revolutionary Echo with Alexa, featuring premium sound quality for an immersive listening experience. 
        The most advanced voice recognition technology responds instantly to your commands. Expertly designed with high-quality speakers for rich, detailed audio that fills the room.
        Control your smart home with superior reliability and performance. The sleek, modern design complements any room decor. 
        The best smart speaker on the market, with unparalleled voice recognition accuracy and response time."""
    },
    "fire": {
        "description": """The Fire tablet delivers exceptional performance at an incredible value. Experience lightning-fast processing speeds for smooth multitasking.
        Featuring a stunning high-definition display with vivid colors and outstanding clarity. The perfect balance of power and portability for on-the-go entertainment.
        Incredibly durable construction with excellent battery life that lasts all day. Award-winning customer service and support.
        The best tablet experience in its price range, with unmatched reliability and versatility."""
    },
    "headphones": {
        "description": """Premium wireless headphones with exceptional sound quality. Industry-leading noise cancellation technology blocks out distractions for immersive listening.
        Expertly engineered drivers deliver crystal-clear highs and deep, rich bass. Supremely comfortable design for extended listening sessions.
        Outstanding battery life with quick charging capability. The perfect headphones for music lovers who demand the best audio experience.
        Superior Bluetooth connectivity with excellent range and reliability."""
    },
    "camera": {
        "description": """Professional-grade camera with revolutionary sensor technology for stunning image quality. Capture perfect moments with exceptional detail and clarity.
        Advanced autofocus system delivers lightning-fast, reliable performance in any lighting condition. Outstanding low-light capability for excellent nighttime photography.
        Expertly designed ergonomics for comfortable handling during extended shooting sessions. The best value in its class, with features typically found in much more expensive models.
        Innovative technology makes this the perfect camera for both beginners and experienced photographers."""
    },
    "laptop": {
        "description": """Ultrafast, ultra-thin laptop featuring exceptional performance and battery life. Revolutionary processor technology delivers incredible speed for demanding applications.
        Stunning high-resolution display with vibrant colors and excellent viewing angles. Premium build quality with superior materials for outstanding durability.
        The perfect laptop for professionals who demand reliability and performance. Excellent keyboard with responsive, comfortable typing experience.
        Best-in-class cooling system for sustained performance under heavy workloads."""
    },
    "watch": {
        "description": """Innovative smartwatch with advanced health monitoring features. Industry-leading technology tracks your fitness metrics with exceptional accuracy.
        Stunning always-on display with perfect visibility in any lighting condition. Outstanding battery life that easily lasts all day.
        Premium materials and excellent build quality for superior comfort and durability. The perfect companion for fitness enthusiasts and busy professionals.
        Best-in-class water resistance for worry-free use during any activity."""
    },
    "speaker": {
        "description": """Premium wireless speaker with exceptional sound quality. Revolutionary acoustic design delivers immersive, room-filling sound with incredible clarity.
        Outstanding battery life for all-day listening enjoyment. Superior Bluetooth connectivity with excellent range and stability.
        Expertly engineered drivers produce rich, detailed audio across the entire frequency spectrum. The perfect speaker for music enthusiasts who demand the best listening experience.
        Best-in-class water and dust resistance for worry-free use in any environment."""
    },
    "default": {
        "description": """This high-quality product features exceptional design and superior performance. Expertly crafted with premium materials for outstanding durability and reliability.
        Innovative technology makes this the perfect choice for demanding users. The best value in its category, offering features typically found in much more expensive alternatives.
        Backed by excellent customer service and support for complete peace of mind."""
    }
}

def add_product_descriptions():
    """Add detailed descriptions to products in the database"""
    # Get MongoDB client
    mongo_client, db = get_mongo_client()
    if db is None:
        logger.error("Failed to connect to MongoDB")
        return False
    
    try:
        # Get all products
        products = list(db.products.find())
        logger.info(f"Found {len(products)} products to update with descriptions")
        
        updated_count = 0
        
        for product in products:
            # Extract product ID and name
            product_id = product.get('_id')
            product_name = product.get('name', '').lower()
            
            # Check if product has a description
            has_description = product.get('description') not in [None, '', 'No description available']
            if has_description:
                logger.info(f"Product '{product.get('name')}' already has a description, replacing it")
            
            # Determine which description to use based on product name
            description_key = 'default'
            for key in PRODUCT_DESCRIPTIONS.keys():
                if key in product_name:
                    description_key = key
                    break
            
            # Get the appropriate description
            description = PRODUCT_DESCRIPTIONS[description_key]['description']
            
            # Update the product with the description
            db.products.update_one(
                {"_id": product_id},
                {"$set": {
                    "description": description,
                    "updated_at": datetime.now()
                }}
            )
            
            updated_count += 1
            logger.info(f"Added description to product '{product.get('name')}'")
        
        logger.info(f"Added descriptions to {updated_count} products")
        return True
    
    except Exception as e:
        logger.error(f"Error adding product descriptions: {str(e)}")
        return False

if __name__ == "__main__":
    if add_product_descriptions():
        logger.info("Product descriptions added successfully")
    else:
        logger.error("Failed to add product descriptions")