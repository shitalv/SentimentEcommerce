"""
Amazon Reviews Dataset Importer for MongoDB

This script imports Amazon reviews from a CSV dataset file into the MongoDB database.
"""

import csv
import logging
import sys
import os
import re
import json
from datetime import datetime
from tqdm import tqdm
import pandas as pd
import html
from bson import ObjectId

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('amazon_importer_mongo')

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import MongoDB utils
from mongo_config import get_mongo_client
from backend.sentiment_analyzer import analyze_sentiment, classify_sentiment, get_sentiment_keywords

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

def clean_text(text):
    """Clean text data from common issues in Amazon reviews datasets"""
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
    
    # Replace escaped quotes
    text = text.replace('\\"', '"')
    
    # Remove excessive punctuation repetition
    text = re.sub(r'([!?.])\\1+', r'\1', text)
    
    # Remove weird control characters
    text = ''.join(c if ord(c) >= 32 else ' ' for c in text)
    
    return text

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

def import_csv_reviews(file_path, limit=None):
    """Import reviews from a CSV file into MongoDB"""
    stats = {
        'products_created': 0,
        'products_skipped': 0,
        'reviews_created': 0,
        'reviews_skipped': 0,
        'errors': 0
    }
    
    # Get MongoDB client
    mongo_client, db = get_mongo_client()
    if not db:
        logger.error("Failed to connect to MongoDB")
        return stats
    
    # Load the CSV file
    try:
        logger.info(f"Reading CSV file: {file_path}")
        
        # Read with pandas to handle large files
        df = pd.read_csv(file_path, low_memory=False)
        
        if limit:
            df = df.head(limit)
            
        logger.info(f"Loaded {len(df)} rows from CSV")
            
        # Process each row
        for index, row in tqdm(df.iterrows(), total=len(df), desc="Importing products and reviews"):
            try:
                # Extract product data
                product_data = {
                    "asin": row.get('asins'),
                    "name": row.get('name'),
                    "brand": row.get('brand'),
                    "categories": row.get('categories', '').split(',') if row.get('categories') else [],
                    "primary_category": row.get('primaryCategories'),
                    "image_url": row.get('imageURLs', '').split(',')[0] if row.get('imageURLs') else None,
                    "manufacturer": row.get('manufacturer'),
                    "created_at": datetime.now(),
                    "updated_at": datetime.now()
                }
                
                # Clean text fields
                product_data["name"] = clean_text(product_data["name"])
                product_data["brand"] = clean_text(product_data["brand"])
                product_data["manufacturer"] = clean_text(product_data["manufacturer"])
                
                # Clean up ASIN
                asin = product_data["asin"]
                if isinstance(asin, str) and ',' in asin:
                    asin = asin.split(',')[0].strip()
                
                if asin:
                    asin = asin.strip().upper()  # ASINs are typically uppercase
                    product_data["asin"] = asin
                
                if not asin or not product_data["name"]:
                    logger.warning(f"Missing required product data. ASIN: {asin}, Name: {product_data['name']}")
                    stats['errors'] += 1
                    continue
                
                # Check if product exists
                existing_product = db.products.find_one({"asin": asin})
                
                if not existing_product:
                    # Create sentiment score placeholders
                    product_data["positive_score"] = 0.0
                    product_data["neutral_score"] = 0.0
                    product_data["negative_score"] = 0.0
                    product_data["sentiment_score"] = 0.5  # Default neutral
                    
                    # Insert the product
                    product_id = db.products.insert_one(product_data).inserted_id
                    stats['products_created'] += 1
                    logger.info(f"Created product: {product_data['name']} (ASIN: {asin})")
                else:
                    product_id = existing_product["_id"]
                    stats['products_skipped'] += 1
                
                # Extract review data
                rating = row.get('reviews.rating')
                review_text = row.get('reviews.text')
                
                if not rating or not review_text:
                    continue
                
                # Parse and clean review data
                review_data = {
                    "product_id": str(product_id),
                    "author": clean_text(row.get('reviews.username')),
                    "title": clean_text(row.get('reviews.title')),
                    "text": clean_text(review_text),
                    "rating": clean_number(rating),
                    "date": parse_date(row.get('reviews.date')),
                    "do_recommend": row.get('reviews.doRecommend'),
                    "helpful_count": clean_number(row.get('reviews.numHelpful')),
                    "source_url": row.get('reviews.sourceURLs', '').split(',')[0] if row.get('reviews.sourceURLs') else None,
                    "created_at": datetime.now()
                }
                
                # Check for required fields
                if not review_data["text"] or not review_data["rating"]:
                    stats['reviews_skipped'] += 1
                    continue
                
                # Check if review already exists (by text and product_id)
                existing_review = db.reviews.find_one({
                    "product_id": str(product_id),
                    "text": review_data["text"]
                })
                
                if existing_review:
                    stats['reviews_skipped'] += 1
                    continue
                
                # Add sentiment analysis
                sentiment_score = analyze_sentiment(review_data["text"])
                review_data["sentiment_score"] = sentiment_score
                review_data["sentiment_class"] = classify_sentiment(sentiment_score)
                
                # Extract keywords
                keywords = get_sentiment_keywords(review_data["text"], sentiment_score)
                review_data["sentiment_keywords"] = json.dumps(keywords)
                
                # Insert the review
                review_id = db.reviews.insert_one(review_data).inserted_id
                stats['reviews_created'] += 1
                
                # Update product sentiment scores
                # Get all reviews for this product
                product_reviews = list(db.reviews.find({"product_id": str(product_id)}))
                
                if product_reviews:
                    # Calculate sentiment counts
                    positive_count = sum(1 for r in product_reviews if r.get("sentiment_class") == "positive")
                    neutral_count = sum(1 for r in product_reviews if r.get("sentiment_class") == "neutral")
                    negative_count = sum(1 for r in product_reviews if r.get("sentiment_class") == "negative")
                    
                    # Calculate weighted average sentiment score
                    # More recent reviews get higher weight
                    sorted_reviews = sorted(product_reviews, key=lambda x: x.get("date", datetime(1970, 1, 1)), reverse=True)
                    
                    weights = []
                    scores = []
                    
                    for i, review in enumerate(sorted_reviews):
                        # Weight based on recency (higher index = older review)
                        recency_weight = max(0.5, 1.0 - (i * 0.1))
                        
                        # Weight based on review length (longer reviews get more weight)
                        length_weight = min(1.5, max(0.5, len(review.get("text", "")) / 100))
                        
                        total_weight = recency_weight * length_weight
                        weights.append(total_weight)
                        scores.append(review.get("sentiment_score", 0.5))
                    
                    # Calculate weighted average
                    if weights and scores:
                        weighted_score = sum(w * s for w, s in zip(weights, scores)) / sum(weights)
                    else:
                        weighted_score = 0.5  # Default neutral
                    
                    # Update product with sentiment scores
                    db.products.update_one(
                        {"_id": product_id},
                        {"$set": {
                            "positive_score": positive_count / len(product_reviews),
                            "neutral_score": neutral_count / len(product_reviews),
                            "negative_score": negative_count / len(product_reviews),
                            "sentiment_score": weighted_score,
                            "updated_at": datetime.now()
                        }}
                    )
            
            except Exception as e:
                logger.error(f"Error processing row {index}: {str(e)}")
                stats['errors'] += 1
    
    except Exception as e:
        logger.error(f"Error reading CSV file: {str(e)}")
        return stats
    
    return stats

if __name__ == "__main__":
    # Check if file path is provided
    if len(sys.argv) < 2:
        logger.error("Usage: python import_amazon_reviews_mongo.py <file_path> [limit]")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    # Check if limit is provided
    limit = None
    if len(sys.argv) > 2:
        try:
            limit = int(sys.argv[2])
        except:
            logger.warning("Invalid limit parameter, using no limit")
    
    # Check if file exists
    if not os.path.isfile(file_path):
        logger.error(f"File not found: {file_path}")
        sys.exit(1)
    
    # Import reviews based on file type
    if file_path.endswith('.csv'):
        stats = import_csv_reviews(file_path, limit)
    else:
        logger.error("Unsupported file format. Please use CSV files.")
        sys.exit(1)
    
    # Print import stats
    logger.info(f"Import completed with the following statistics:")
    logger.info(f"Products created: {stats['products_created']}")
    logger.info(f"Products skipped: {stats['products_skipped']}")
    logger.info(f"Reviews created: {stats['reviews_created']}")
    logger.info(f"Reviews skipped: {stats['reviews_skipped']}")
    logger.info(f"Errors: {stats['errors']}")