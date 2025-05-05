"""
Import Specific Products from Amazon Dataset

This script imports specific products from the Amazon reviews dataset 
that aren't already in the database.
"""

import logging
import sys
import os
import re
import json
from datetime import datetime
import pandas as pd
import html
from bson import ObjectId
from tqdm import tqdm

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('amazon_specific_products')

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import MongoDB utils
from mongo_config import get_mongo_client
from backend.sentiment_analyzer import analyze_sentiment, classify_sentiment, get_sentiment_keywords

def clean_text(text):
    """Clean text data from common issues"""
    if not text:
        return ""
    
    # Make sure we're working with a string
    if not isinstance(text, str):
        try:
            text = str(text)
        except:
            return ""
    
    # Decode HTML entities
    text = html.unescape(text)
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', ' ', text)
    
    # Replace multiple spaces, newlines, and tabs with a single space
    text = re.sub(r'\s+', ' ', text)
    
    # Remove BOM character
    text = text.replace('\ufeff', '')
    
    # Remove non-breaking spaces and other invisible characters
    text = text.replace('\xa0', ' ')
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    return text

def parse_date(date_str):
    """Parse date string into datetime object"""
    if not date_str:
        return None
        
    try:
        # Check if it's already a datetime
        if isinstance(date_str, datetime):
            return date_str
            
        # Try various date formats
        formats = [
            '%Y-%m-%d',
            '%d/%m/%Y',
            '%m/%d/%Y',
            '%b %d, %Y',
            '%B %d, %Y',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%d %H:%M:%S'
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(str(date_str).strip(), fmt)
            except:
                continue
                
        # If none of the formats work, try to extract just the date portion
        match = re.search(r'(\d{4}-\d{2}-\d{2})', str(date_str))
        if match:
            return datetime.strptime(match.group(1), '%Y-%m-%d')
            
        return None
    except Exception as e:
        logger.error(f"Error parsing date {date_str}: {str(e)}")
        return None

def clean_number(value):
    """Clean and convert numeric values"""
    if not value:
        return None
        
    if isinstance(value, (int, float)):
        return value
        
    if isinstance(value, str):
        # Remove non-numeric characters
        value = re.sub(r'[^\d.]+', '', value)
        try:
            return float(value)
        except:
            return None
    
    return None

def import_specific_asins(file_path, target_asins):
    """Import specific products by ASIN with their reviews"""
    stats = {
        'products_created': 0,
        'reviews_created': 0,
        'errors': 0
    }
    
    # Get MongoDB client
    mongo_client, db = get_mongo_client()
    if db is None:
        logger.error("Failed to connect to MongoDB")
        return stats
    
    # Load the CSV file
    try:
        logger.info(f"Reading CSV file: {file_path}")
        df = pd.read_csv(file_path, low_memory=False)
        logger.info(f"Loaded {len(df)} rows from CSV")
        
        # Filter for the target ASINs
        filtered_df = df[df['asins'].isin(target_asins)]
        logger.info(f"Found {len(filtered_df)} rows for the target ASINs")
        
        # Process each ASIN
        for asin in target_asins:
            try:
                # Get rows for this ASIN
                product_rows = filtered_df[filtered_df['asins'] == asin]
                
                if len(product_rows) == 0:
                    logger.warning(f"No data found for ASIN: {asin}")
                    continue
                
                # Use the first row for product details
                first_row = product_rows.iloc[0]
                
                # Extract and clean product data
                product_data = {
                    "asin": asin,
                    "name": clean_text(first_row.get('name')),
                    "brand": clean_text(first_row.get('brand')),
                    "categories": [cat.strip() for cat in str(first_row.get('categories', '')).split(',') if cat.strip()],
                    "primary_category": clean_text(first_row.get('primaryCategories')),
                    "image_url": first_row.get('imageURLs', '').split(',')[0] if first_row.get('imageURLs') else None,
                    "manufacturer": clean_text(first_row.get('manufacturer')),
                    "created_at": datetime.now(),
                    "updated_at": datetime.now(),
                    # Add description if available
                    "description": clean_text(first_row.get('description')),
                    # Initialize sentiment scores
                    "positive_score": 0.0,
                    "neutral_score": 0.0,
                    "negative_score": 0.0,
                    "sentiment_score": 0.5
                }
                
                # Skip if missing critical data
                if not product_data["name"]:
                    logger.warning(f"Missing name for ASIN: {asin}")
                    continue
                
                # Check if product exists
                existing_product = db.products.find_one({"asin": asin})
                
                if existing_product:
                    logger.info(f"Product already exists: {product_data['name']} (ASIN: {asin})")
                    product_id = existing_product["_id"]
                else:
                    # Insert the product
                    product_id = db.products.insert_one(product_data).inserted_id
                    stats['products_created'] += 1
                    logger.info(f"Created product: {product_data['name']} (ASIN: {asin})")
                
                # Import reviews for this product
                review_count = 0
                
                for idx, row in tqdm(product_rows.iterrows(), total=len(product_rows), desc=f"Importing reviews for {asin}"):
                    # Extract review data
                    review_text = row.get('reviews.text')
                    rating = row.get('reviews.rating')
                    
                    if not review_text or not rating:
                        continue
                    
                    # Clean review data
                    review_data = {
                        "product_id": str(product_id),
                        "author": clean_text(row.get('reviews.username')),
                        "title": clean_text(row.get('reviews.title')),
                        "text": clean_text(review_text),
                        "rating": clean_number(rating),
                        "date": parse_date(row.get('reviews.date')),
                        "created_at": datetime.now()
                    }
                    
                    # Check if review already exists
                    existing_review = db.reviews.find_one({
                        "product_id": str(product_id),
                        "text": review_data["text"]
                    })
                    
                    if existing_review:
                        continue
                    
                    # Add sentiment analysis
                    sentiment_score = analyze_sentiment(review_data["text"])
                    review_data["sentiment_score"] = sentiment_score
                    review_data["sentiment_class"] = classify_sentiment(sentiment_score)
                    
                    # Extract keywords
                    keywords = get_sentiment_keywords(review_data["text"], sentiment_score)
                    review_data["sentiment_keywords"] = json.dumps(keywords)
                    
                    # Insert the review
                    db.reviews.insert_one(review_data)
                    stats['reviews_created'] += 1
                    review_count += 1
                
                # Update product sentiment scores if we added reviews
                if review_count > 0:
                    # Get all reviews for this product
                    product_reviews = list(db.reviews.find({"product_id": str(product_id)}))
                    
                    if product_reviews:
                        # Calculate sentiment distribution
                        positive_count = sum(1 for r in product_reviews if r.get("sentiment_class") == "positive")
                        neutral_count = sum(1 for r in product_reviews if r.get("sentiment_class") == "neutral")
                        negative_count = sum(1 for r in product_reviews if r.get("sentiment_class") == "negative")
                        total_count = len(product_reviews)
                        
                        # Calculate average sentiment score
                        avg_score = sum(r.get("sentiment_score", 0.5) for r in product_reviews) / total_count
                        
                        # Update product
                        db.products.update_one(
                            {"_id": product_id},
                            {"$set": {
                                "positive_score": positive_count / total_count,
                                "neutral_score": neutral_count / total_count,
                                "negative_score": negative_count / total_count,
                                "sentiment_score": avg_score,
                                "updated_at": datetime.now()
                            }}
                        )
                        logger.info(f"Updated sentiment scores for {product_data['name']}")
            
            except Exception as e:
                logger.error(f"Error processing ASIN {asin}: {str(e)}")
                stats['errors'] += 1
    
    except Exception as e:
        logger.error(f"Error reading CSV file: {str(e)}")
        return stats
    
    return stats

def get_missing_products(file_path):
    """Find ASINs that are in the dataset but not in the database"""
    # Get MongoDB client
    mongo_client, db = get_mongo_client()
    if db is None:
        logger.error("Failed to connect to MongoDB")
        return []
    
    # Get existing ASINs in the database
    existing_asins = set(p['asin'] for p in db.products.find({}, {'asin': 1}))
    logger.info(f"Found {len(existing_asins)} existing products in database")
    
    # Load the dataset
    df = pd.read_csv(file_path, low_memory=False)
    dataset_asins = set(df['asins'].unique())
    logger.info(f"Found {len(dataset_asins)} unique ASINs in dataset")
    
    # Find missing ASINs
    missing_asins = [asin for asin in dataset_asins if asin not in existing_asins]
    logger.info(f"Found {len(missing_asins)} ASINs that are not in the database")
    
    return missing_asins

if __name__ == "__main__":
    # Set default file path
    file_path = "attached_assets/Datafiniti_Amazon_Consumer_Reviews_of_Amazon_Products.csv"
    
    # Check if file exists
    if not os.path.isfile(file_path):
        logger.error(f"File not found: {file_path}")
        sys.exit(1)
    
    # Option 1: Import specific ASINs
    specific_asins = [
        'B01AHBBG04',  # Fire HD 8 Tablet
        'B01BH83OOM',  # Amazon Tap - Alexa-Enabled Portable Bluetooth Speaker
        'B0189XYY0Q',  # Fire HD 10 Tablet
        'B00VINDBJK',  # Kindle Oasis
        'B00IOY8XWQ',  # Kindle Voyage
        'B01AHB9CN2'   # Fire HD 8 Tablet (Magenta)
    ]
    
    # Option 2: Find ASINs that aren't in the database yet
    missing_asins = get_missing_products(file_path)
    
    # Choose ASINs to import (missing ASINs or specific list)
    target_asins = specific_asins
    
    # Import the selected ASINs
    if target_asins:
        logger.info(f"Importing {len(target_asins)} products...")
        stats = import_specific_asins(file_path, target_asins)
        
        # Print import stats
        logger.info(f"Import completed with the following statistics:")
        logger.info(f"Products created: {stats['products_created']}")
        logger.info(f"Reviews created: {stats['reviews_created']}")
        logger.info(f"Errors: {stats['errors']}")
    else:
        logger.info("No products selected for import")