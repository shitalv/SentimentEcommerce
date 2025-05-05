"""
Add Final Missing Products

This script adds the final remaining products from the dataset.
"""

import logging
import sys
import os
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('add_final_products')

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import MongoDB utils
from mongo_config import get_mongo_client

def add_final_products():
    """Add the remaining Amazon products"""
    # Get MongoDB client
    mongo_client, db = get_mongo_client()
    if db is None:
        logger.error("Failed to connect to MongoDB")
        return False
    
    # List of products to add (remaining Amazon products from dataset)
    products_to_add = [
        {
            "asin": "B010CEHQTG",
            "name": "Amazon Echo Show Alexa-enabled Bluetooth Speaker with 7\" Screen",
            "brand": "Amazon",
            "categories": ["Electronics", "Smart Home"],
            "primary_category": "Electronics,Hardware",
            "image_url": "https://m.media-amazon.com/images/I/61XiVO3ckgL._AC_SL1000_.jpg",
            "description": "Echo Show brings you everything you love about Alexa, and now she can show you things. Watch video flash briefings, see music lyrics, smart home cameras, photos, weather forecasts, to-do and shopping lists, and more.",
            "positive_score": 0.7,
            "neutral_score": 0.2,
            "negative_score": 0.1,
            "sentiment_score": 0.65,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "asin": "B01N32NCPM",
            "name": "Amazon Fire TV with 4K Ultra HD and Alexa Voice Remote (Pendant Design)",
            "brand": "Amazon",
            "categories": ["Electronics", "Streaming Media"],
            "primary_category": "Electronics",
            "image_url": "https://m.media-amazon.com/images/I/716CV9e5MHL._AC_SL1500_.jpg",
            "description": "With more power, a lightning-fast processor, and 4K Ultra HD, Fire TV delivers a more complete picture with access to vivid colors and beautiful detail. Find your favorite content with the included Alexa Voice Remote.",
            "positive_score": 0.75,
            "neutral_score": 0.15,
            "negative_score": 0.1,
            "sentiment_score": 0.7,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "asin": "B00QFQRELG",
            "name": "Amazon 9W PowerFast Official OEM USB Charger and Power Adapter for Fire Tablets and Kindle eReaders",
            "brand": "Amazon",
            "categories": ["Electronics", "Accessories"],
            "primary_category": "Electronics",
            "image_url": "https://m.media-amazon.com/images/I/41vLCHrE3yL._AC_SL1000_.jpg",
            "description": "Official Amazon 9W, 1.8A power adapter and USB cable compatible with most devices with a micro-USB port, although charging times may vary (requires micro-USB cable, included).",
            "positive_score": 0.8,
            "neutral_score": 0.1,
            "negative_score": 0.1,
            "sentiment_score": 0.75,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "asin": "B018Y22BI4",
            "name": "Fire Tablet, 7 Display, Wi-Fi, 16 GB - Includes Special Offers, Black",
            "brand": "Amazon",
            "categories": ["Electronics", "Tablets"],
            "primary_category": "Electronics",
            "image_url": "https://m.media-amazon.com/images/I/61plLZhXH9L._AC_SL1000_.jpg",
            "description": "The next generation of our best-selling Fire tablet ever - now thinner, lighter, and with longer battery life and an improved display.",
            "positive_score": 0.7,
            "neutral_score": 0.2,
            "negative_score": 0.1,
            "sentiment_score": 0.65,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "asin": "B018Y23MNM",
            "name": "Fire Kids Edition Tablet, 7 Display, Wi-Fi, 16 GB, Green Kid-Proof Case",
            "brand": "Amazon",
            "categories": ["Electronics", "Tablets"],
            "primary_category": "Electronics",
            "image_url": "https://m.media-amazon.com/images/I/81n6VzGLEaL._AC_SL1500_.jpg",
            "description": "Up to 8 hours of battery life. 16 GB of internal storage and a microSD card slot for up to 200 GB of expandable storage.",
            "positive_score": 0.75,
            "neutral_score": 0.15,
            "negative_score": 0.1,
            "sentiment_score": 0.7,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "asin": "B01AHBDCKQ",
            "name": "All-New Fire HD 8 Tablet, 8 HD Display, Wi-Fi, 32 GB - Includes Special Offers, Blue",
            "brand": "Amazon",
            "categories": ["Electronics", "Tablets"],
            "primary_category": "Electronics",
            "image_url": "https://m.media-amazon.com/images/I/61uJN0kGHSL._AC_SL1000_.jpg",
            "description": "8\" HD display; 16 or 32 GB of internal storage and a microSD slot for up to 200 GB of expandable storage.",
            "positive_score": 0.7,
            "neutral_score": 0.2,
            "negative_score": 0.1,
            "sentiment_score": 0.65,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "asin": "B00IOYAM4I",
            "name": "Amazon - Kindle Voyage - 4GB - Wi-Fi + 3G - Black",
            "brand": "Amazon",
            "categories": ["Electronics", "E-readers"],
            "primary_category": "Electronics",
            "image_url": "https://m.media-amazon.com/images/I/616h8pSVOQL._AC_SL1000_.jpg",
            "description": "High-resolution 300 ppi display with adaptive built-in light, PagePress enables you to turn the page without lifting a finger.",
            "positive_score": 0.8,
            "neutral_score": 0.1,
            "negative_score": 0.1,
            "sentiment_score": 0.75,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "asin": "B01AHB9C1E",
            "name": "Fire HD 8 Tablet with Alexa, 8\" HD Display, 32 GB, Tangerine - with Special Offers",
            "brand": "Amazon",
            "categories": ["Electronics", "Tablets"],
            "primary_category": "Electronics",
            "image_url": "https://m.media-amazon.com/images/I/61BxfhKAuNL._AC_SL1000_.jpg",
            "description": "8\" HD display, 2x the storage (32 or 64 GB of internal storage and up to 400 GB with microSD card) + 2 GB RAM.",
            "positive_score": 0.7,
            "neutral_score": 0.2,
            "negative_score": 0.1,
            "sentiment_score": 0.65,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
    ]
    
    products_added = 0
    products_skipped = 0
    
    for product in products_to_add:
        # Check if product already exists
        existing = db.products.find_one({"asin": product["asin"]})
        
        if existing:
            logger.info(f"Product already exists: {product['name']} (ASIN: {product['asin']})")
            products_skipped += 1
            continue
        
        # Insert new product
        db.products.insert_one(product)
        logger.info(f"Added product: {product['name']} (ASIN: {product['asin']})")
        products_added += 1
    
    # Count total products after adding
    product_count = db.products.count_documents({})
    
    logger.info(f"Added {products_added} new products")
    logger.info(f"Skipped {products_skipped} existing products")
    logger.info(f"Total products in database: {product_count}")
    
    return True

if __name__ == "__main__":
    add_final_products()