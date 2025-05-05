"""
Import All Products from Amazon Dataset

This script imports all unique products from the Amazon reviews dataset 
with proper product categorization and sentiment calculation.
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
logger = logging.getLogger('amazon_importer_complete')

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

def get_clean_image_url(url_str):
    """Get clean image URL from string that might contain multiple URLs"""
    if not url_str:
        return None
        
    # If it's already a valid URL, return it
    if isinstance(url_str, str) and url_str.startswith('http'):
        return url_str.strip()
        
    # If it's a comma-separated list, take the first one
    if isinstance(url_str, str) and ',' in url_str:
        urls = url_str.split(',')
        for url in urls:
            url = url.strip()
            if url and url.startswith('http'):
                return url
                
    return None

def import_all_products(file_path):
    """Import all unique products from the dataset with reviews"""
    stats = {
        'products_created': 0,
        'products_skipped': 0,
        'reviews_created': 0,
        'reviews_skipped': 0,
        'errors': 0,
        'total_products_with_reviews': 0
    }
    
    # Get MongoDB client
    mongo_client, db = get_mongo_client()
    if db is None:
        logger.error("Failed to connect to MongoDB")
        return stats
    
    # Load the CSV file
    try:
        logger.info(f"Reading CSV file: {file_path}")
        
        # Read with pandas to handle large files
        df = pd.read_csv(file_path, low_memory=False)
            
        logger.info(f"Loaded {len(df)} rows from CSV")
        
        # Get a list of unique ASINs
        asins = df['asins'].unique()
        logger.info(f"Found {len(asins)} unique ASIN values")
        
        # Process each unique product
        for asin in tqdm(asins, desc="Importing products"):
            try:
                # Skip empty ASIN
                if not isinstance(asin, str) or not asin.strip():
                    continue
                    
                # Clean ASIN
                clean_asin = asin.strip().upper()
                
                # Get all rows for this ASIN
                product_rows = df[df['asins'] == asin]
                
                if len(product_rows) == 0:
                    continue
                    
                # Use the first row for product details
                first_row = product_rows.iloc[0]
                
                # Extract product data
                product_data = {
                    "asin": clean_asin,
                    "name": clean_text(first_row.get('name')),
                    "brand": clean_text(first_row.get('brand')),
                    "categories": [clean_text(cat) for cat in str(first_row.get('categories', '')).split(',') if clean_text(cat)],
                    "primary_category": clean_text(first_row.get('primaryCategories')),
                    "image_url": get_clean_image_url(first_row.get('imageURLs')),
                    "manufacturer": clean_text(first_row.get('manufacturer')),
                    "created_at": datetime.now(),
                    "updated_at": datetime.now(),
                    # Add additional product details
                    "description": clean_text(first_row.get('description')),
                    "price": clean_number(first_row.get('price')),
                    "currency": first_row.get('currency'),
                }
                
                # Check if required fields are present
                if not product_data["name"]:
                    logger.warning(f"Missing product name for ASIN: {clean_asin}")
                    stats['errors'] += 1
                    continue
                
                # Check if product exists in MongoDB
                existing_product = db.products.find_one({"asin": clean_asin})
                
                if not existing_product:
                    # Create sentiment score placeholders
                    product_data["positive_score"] = 0.0
                    product_data["neutral_score"] = 0.0
                    product_data["negative_score"] = 0.0
                    product_data["sentiment_score"] = 0.5  # Default neutral
                    
                    # Insert the product
                    product_id = db.products.insert_one(product_data).inserted_id
                    stats['products_created'] += 1
                    logger.info(f"Created product: {product_data['name']} (ASIN: {clean_asin})")
                else:
                    product_id = existing_product["_id"]
                    stats['products_skipped'] += 1
                
                # Import reviews for this product
                reviews_created = 0
                
                for idx, row in product_rows.iterrows():
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
                        "source_url": get_clean_image_url(row.get('reviews.sourceURLs')),
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
                    reviews_created += 1
                
                # Only update product sentiment if we have reviews
                if reviews_created > 0:
                    # Update product sentiment scores
                    product_reviews = list(db.reviews.find({"product_id": str(product_id)}))
                    
                    if product_reviews:
                        # Calculate sentiment counts
                        positive_count = sum(1 for r in product_reviews if r.get("sentiment_class") == "positive")
                        neutral_count = sum(1 for r in product_reviews if r.get("sentiment_class") == "neutral")
                        negative_count = sum(1 for r in product_reviews if r.get("sentiment_class") == "negative")
                        total_count = len(product_reviews)
                        
                        # Calculate weighted average sentiment score
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
                                "positive_score": positive_count / total_count,
                                "neutral_score": neutral_count / total_count,
                                "negative_score": negative_count / total_count,
                                "sentiment_score": weighted_score,
                                "updated_at": datetime.now()
                            }}
                        )
                        
                        stats['total_products_with_reviews'] += 1
            
            except Exception as e:
                logger.error(f"Error processing ASIN {asin}: {str(e)}")
                stats['errors'] += 1
    
    except Exception as e:
        logger.error(f"Error reading CSV file: {str(e)}")
        return stats
    
    return stats

if __name__ == "__main__":
    # Set default file path
    file_path = "attached_assets/Datafiniti_Amazon_Consumer_Reviews_of_Amazon_Products.csv"
    
    # Check if file path is provided
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    
    # Check if file exists
    if not os.path.isfile(file_path):
        logger.error(f"File not found: {file_path}")
        sys.exit(1)
    
    # Import reviews
    stats = import_all_products(file_path)
    
    # Print import stats
    logger.info(f"Import completed with the following statistics:")
    logger.info(f"Products created: {stats['products_created']}")
    logger.info(f"Products skipped: {stats['products_skipped']}")
    logger.info(f"Reviews created: {stats['reviews_created']}")
    logger.info(f"Reviews skipped: {stats['reviews_skipped']}")
    logger.info(f"Products with reviews: {stats['total_products_with_reviews']}")
    logger.info(f"Errors: {stats['errors']}")