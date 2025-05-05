"""
Quick Add Products

This script adds a few missing products directly to the database.
"""

import logging
import sys
import os
import json
from datetime import datetime
from bson import ObjectId

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('quick_add_products')

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import MongoDB utils
from mongo_config import get_mongo_client

def add_missing_products():
    """Add a select few products that are missing from the database"""
    # Get MongoDB client
    mongo_client, db = get_mongo_client()
    if db is None:
        logger.error("Failed to connect to MongoDB")
        return False
    
    # List of products to add
    products_to_add = [
        {
            "asin": "B01BH83OOM",
            "name": "Amazon Tap - Alexa-Enabled Portable Bluetooth Speaker",
            "brand": "Amazon",
            "categories": ["Electronics", "Audio"],
            "primary_category": "Electronics",
            "image_url": "https://m.media-amazon.com/images/I/71vPpQPXxuL._AC_SL1500_.jpg",
            "manufacturer": "Amazon",
            "description": "Amazon Tap is a portable Bluetooth and Wi-Fi enabled speaker that gives you rich, full-range sound. Tap provides up to 9 hours of playback.",
            "positive_score": 0.7,
            "neutral_score": 0.2,
            "negative_score": 0.1,
            "sentiment_score": 0.65,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "asin": "B0189XYY0Q",
            "name": "Fire HD 10 Tablet, 10.1 HD Display, Wi-Fi, 16 GB - Silver Aluminum",
            "brand": "Amazon",
            "categories": ["Electronics", "Tablets"],
            "primary_category": "Electronics",
            "image_url": "https://m.media-amazon.com/images/I/61jIPz0vzjL._AC_SL1000_.jpg",
            "manufacturer": "Amazon",
            "description": "Brilliant 10.1\" HD display (1280 x 800), up to 1.5 GHz quad-core processor, 1 GB RAM, and Dolby Audio. 16 or 32 GB of internal storage and a microSD slot for up to 128 GB of expandable storage.",
            "positive_score": 0.65,
            "neutral_score": 0.25,
            "negative_score": 0.1,
            "sentiment_score": 0.6,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "asin": "B00VINDBJK",
            "name": "Kindle Oasis E-reader with Leather Charging Cover - Merlot",
            "brand": "Amazon",
            "categories": ["Electronics", "E-readers"],
            "primary_category": "Electronics",
            "image_url": "https://m.media-amazon.com/images/I/61-6UL21XVL._AC_SL1000_.jpg",
            "manufacturer": "Amazon",
            "description": "Our thinnest and lightest Kindle ever. High-resolution 300 ppi display with crisp, laser-quality text. Ergonomic design with dedicated page turn buttons.",
            "positive_score": 0.75,
            "neutral_score": 0.15,
            "negative_score": 0.1,
            "sentiment_score": 0.7,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "asin": "B00IOY8XWQ",
            "name": "Amazon - Kindle Voyage - 6\" - 4GB - Black",
            "brand": "Amazon",
            "categories": ["Electronics", "E-readers"],
            "primary_category": "Electronics",
            "image_url": "https://m.media-amazon.com/images/I/61dEzJVlhCL._AC_SL1000_.jpg",
            "manufacturer": "Amazon",
            "description": "Kindle Voyage features a high-resolution 300 ppi display for crisp, laser-quality text. PagePress sensors allow you to turn the page without lifting a finger.",
            "positive_score": 0.8,
            "neutral_score": 0.1,
            "negative_score": 0.1,
            "sentiment_score": 0.75,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "asin": "B01AHB9CN2",
            "name": "All-New Fire HD 8 Tablet, 8\" HD Display, Wi-Fi, 16 GB - Magenta",
            "brand": "Amazon",
            "categories": ["Electronics", "Tablets"],
            "primary_category": "Electronics",
            "image_url": "https://m.media-amazon.com/images/I/61zfLsXuPDL._AC_SL1000_.jpg",
            "manufacturer": "Amazon",
            "description": "8\" HD display, 2x the storage (32 or 64 GB of internal storage and up to 400 GB with microSD card) + 2 GB RAM. All-day battery life - Up to 10 hours of reading, browsing the web, watching videos, and listening to music.",
            "positive_score": 0.7,
            "neutral_score": 0.2,
            "negative_score": 0.1,
            "sentiment_score": 0.65,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "asin": "B018Y225IA",
            "name": "Amazon Kindle Fire 16GB 7\" IPS Display Tablet",
            "brand": "Amazon",
            "categories": ["Electronics", "Tablets"],
            "primary_category": "Electronics",
            "image_url": "https://m.media-amazon.com/images/I/71I4y4B6sZL._AC_SL1500_.jpg",
            "manufacturer": "Amazon",
            "description": "Beautiful 7\" IPS display (171 ppi / 1024 x 600) and fast 1.3 GHz quad-core processor. Rear and front-facing cameras. 16 GB internal storage.",
            "positive_score": 0.6,
            "neutral_score": 0.3,
            "negative_score": 0.1,
            "sentiment_score": 0.6,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "asin": "B017JG41PC",
            "name": "Kindle E-reader - White, 6 Glare-Free Touchscreen Display, Wi-Fi",
            "brand": "Amazon",
            "categories": ["Electronics", "E-readers"],
            "primary_category": "Electronics",
            "image_url": "https://m.media-amazon.com/images/I/61%2BFppkPrQL._AC_SL1000_.jpg",
            "manufacturer": "Amazon",
            "description": "Kindle uses actual ink particles and proprietary hand-built fonts to create crisp text similar to what you see in a physical book. Reads like a book on paper with no annoying glare, even in bright sunlight.",
            "positive_score": 0.75,
            "neutral_score": 0.15,
            "negative_score": 0.1,
            "sentiment_score": 0.7,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "asin": "B018Y22C2Y",
            "name": "Fire Kids Edition Tablet, 7 Display, Wi-Fi, 16 GB, Blue Kid-Proof Case",
            "brand": "Amazon",
            "categories": ["Electronics", "Tablets"],
            "primary_category": "Electronics",
            "image_url": "https://m.media-amazon.com/images/I/71nvEy4dRWL._AC_SL1500_.jpg",
            "manufacturer": "Amazon",
            "description": "Up to 10 hours of battery life. 8 or 16 GB of internal storage and a microSD card slot for up to 200 GB of expandable storage. Designed with kids in mind, with 1 year of Amazon Kids+ (FreeTime Unlimited), a Kid-Proof Case, and a 2-year worry-free guarantee.",
            "positive_score": 0.8,
            "neutral_score": 0.1,
            "negative_score": 0.1,
            "sentiment_score": 0.75,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "asin": "B01J24C0TI",
            "name": "Amazon Echo Show Alexa-enabled Bluetooth Speaker with 7\" Screen",
            "brand": "Amazon",
            "categories": ["Electronics", "Smart Home"],
            "primary_category": "Electronics,Hardware",
            "image_url": "https://m.media-amazon.com/images/I/61Xm9HCoBkL._AC_SL1000_.jpg",
            "manufacturer": "Amazon",
            "description": "Echo Show brings you everything you love about Alexa, and now she can show you things. Watch video flash briefings, Amazon Video content, see music lyrics, smart home cameras, photos, weather forecasts, to-do and shopping lists, browse and listen to Audible audiobooks, and more.",
            "positive_score": 0.7,
            "neutral_score": 0.2,
            "negative_score": 0.1,
            "sentiment_score": 0.65,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "asin": "B06XB29FPF",
            "name": "Amazon - Echo Plus w/ Built-In Hub - Silver",
            "brand": "Amazon",
            "categories": ["Electronics", "Smart Home"],
            "primary_category": "Electronics,Hardware",
            "image_url": "https://m.media-amazon.com/images/I/61gCOMiXrpL._AC_SL1000_.jpg",
            "manufacturer": "Amazon",
            "description": "Echo Plus connects to Alexa to play music, answer questions, make calls, provide information, news, sports scores, weather, and more. Just ask. Echo Plus has 7 microphones and beamforming technology so it can hear you from across the room, even when music is playing.",
            "positive_score": 0.75,
            "neutral_score": 0.15,
            "negative_score": 0.1,
            "sentiment_score": 0.7,
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
    
    logger.info(f"Added {products_added} new products")
    logger.info(f"Skipped {products_skipped} existing products")
    return True

if __name__ == "__main__":
    add_missing_products()