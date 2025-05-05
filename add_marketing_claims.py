"""
Add Marketing Claims to Product Descriptions

This script ensures all products have marketing claims in their descriptions
for the Hype vs. Reality feature to analyze.
"""

import logging
import sys
import os
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('add_marketing_claims')

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import MongoDB utils
from mongo_config import get_mongo_client

def generate_marketing_claims(product_name, category):
    """Generate marketing claims based on product name and category"""
    # Base marketing claims by category
    category_claims = {
        "E-readers": [
            "Our best e-reader experience ever",
            "Crisp, laser-quality text with no glare - even in bright sunlight",
            "Weeks of battery life on a single charge",
            "The lightest and thinnest design in our lineup",
            "Distraction-free reading experience unlike any tablet"
        ],
        "Tablets": [
            "Lightning-fast performance with our most powerful processor yet",
            "Stunning display with vibrant colors and crisp detail",
            "All-day battery life for work and play",
            "Ultra-responsive touch screen for smooth navigation",
            "The thinnest and lightest tablet we've ever made"
        ],
        "Smart Home": [
            "Unprecedented smart home integration with one-touch setup",
            "Crystal-clear sound that fills the room from any angle",
            "The most advanced voice recognition technology available",
            "Seamlessly connects with all your smart devices",
            "The smartest AI assistant that learns your preferences"
        ],
        "Streaming Media": [
            "Blazing-fast streaming with no buffering",
            "The most channels and apps available on any streaming device",
            "4K Ultra HD with vibrant colors and incredible clarity",
            "Voice search that understands even the most complex requests",
            "The most powerful streaming device we've ever built"
        ],
        "Accessories": [
            "Specifically engineered for optimal performance",
            "The fastest charging technology available",
            "Rigorously tested for ultimate durability",
            "Premium materials that outlast the competition",
            "Designed for perfect compatibility with all devices"
        ]
    }
    
    # Get claims for the product category
    product_category = None
    for cat in category_claims.keys():
        if cat.lower() in str(category).lower():
            product_category = cat
            break
    
    # Use generic claims if no specific category found
    if not product_category:
        product_category = "Tablets"  # Default category
    
    # Get 3 claims for this product
    claims = category_claims[product_category][:3]
    
    # Add product name to the end of the description
    claims.append(f"Experience the difference with {product_name} today.")
    
    return " ".join(claims)

def add_marketing_claims_to_products():
    """Add marketing claims to product descriptions"""
    # Get MongoDB client
    mongo_client, db = get_mongo_client()
    if db is None:
        logger.error("Failed to connect to MongoDB")
        return False
    
    # Get all products
    products = list(db.products.find({}))
    logger.info(f"Found {len(products)} products in database")
    
    products_updated = 0
    
    for product in products:
        # Check if product has description with marketing claims
        description = product.get("description", "")
        
        # Skip if description already has marketing claims
        if len(description) > 100 and ("best" in description.lower() or 
                                      "experience" in description.lower() or
                                      "ever" in description.lower()):
            logger.info(f"Product already has marketing claims: {product.get('name')}")
            continue
        
        # Generate marketing claims based on product data
        primary_category = product.get("primary_category", "")
        categories = product.get("categories", [])
        
        # Combine categories for better matching
        all_categories = primary_category + " " + " ".join(categories)
        
        marketing_claims = generate_marketing_claims(product.get("name", ""), all_categories)
        
        # Combine existing description with marketing claims
        if description:
            new_description = f"{description} {marketing_claims}"
        else:
            new_description = marketing_claims
        
        # Update product
        db.products.update_one(
            {"_id": product["_id"]},
            {"$set": {
                "description": new_description,
                "updated_at": datetime.now()
            }}
        )
        
        logger.info(f"Added marketing claims to product: {product.get('name')}")
        products_updated += 1
    
    logger.info(f"Updated {products_updated} products with marketing claims")
    return True

if __name__ == "__main__":
    add_marketing_claims_to_products()