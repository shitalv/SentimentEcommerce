"""
Amazon Reviews Dataset Importer

This script imports real Amazon reviews from a dataset file into the application's database.
The dataset should be in CSV or JSON format with the required fields.

Common fields in Amazon reviews datasets:
- product_id/asin: Amazon Standard Identification Number
- product_title: Name of the product
- review_text: The actual review content
- star_rating: Numerical rating (usually 1-5)
- review_date: When the review was posted
- reviewer_name/reviewer_id: Information about the reviewer
"""

import json
import csv
import logging
import sys
import os
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from tqdm import tqdm  # For progress bar
import pandas as pd

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('amazon_importer')

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from models import Product, Review
from backend.sentiment_analyzer import analyze_sentiment, classify_sentiment, get_sentiment_keywords

def parse_date(date_str):
    """Parse date string into datetime object"""
    try:
        # Try different date formats
        formats = [
            '%Y-%m-%d',  # 2023-04-15
            '%m/%d/%Y',  # 04/15/2023
            '%B %d, %Y', # April 15, 2023
            '%d %B %Y',  # 15 April 2023
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
                
        # If none of the formats match, try a more flexible approach
        return pd.to_datetime(date_str).to_pydatetime()
    except Exception as e:
        logger.warning(f"Could not parse date: {date_str}, error: {str(e)}")
        return None

def import_json_reviews(file_path, limit=None):
    """Import reviews from a JSON file"""
    logger.info(f"Importing reviews from JSON file: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if limit and isinstance(data, list):
        data = data[:limit]
    
    import_reviews(data)

def import_csv_reviews(file_path, limit=None):
    """Import reviews from a CSV file"""
    logger.info(f"Importing reviews from CSV file: {file_path}")
    
    reviews = []
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if limit and i >= limit:
                break
            # Format review data from the Datafiniti CSV structure
            try:
                # Validate required fields
                if not row.get('reviews.text'):
                    logger.warning(f"Skipping review - missing review text for ASIN: {row.get('asins', 'unknown')}")
                    continue

                review = {
                    'asin': row.get('asins', '').split(',')[0].strip() if row.get('asins') else 'unknown',
                    'product_title': row.get('name', 'Untitled Product'),
                    'product_description': row.get('description', ''),
                    'price': float(row.get('price', 0)) if row.get('price') and row.get('price').strip() else None,
                    'category': row.get('categories', '').split(',')[0].strip() if row.get('categories') else 'Uncategorized',
                    'review_text': row.get('reviews.text', '').strip(),
                    'reviewer_name': row.get('reviews.username', 'Anonymous'),
                    'rating': float(row.get('reviews.rating', 3.0)),  # Default to neutral rating
                    'review_date': row.get('reviews.date', None)
                }

                # Skip if essential fields are missing
                if not review['asin'] or not review['product_title'] or not review['review_text']:
                    continue
            reviews.append(review)
    
    import_reviews(reviews)

def import_reviews(reviews_data):
    """Process and import reviews into the database"""
    logger.info(f"Processing {len(reviews_data)} reviews")
    
    # Track stats
    stats = {
        'products_created': 0,
        'products_skipped': 0,
        'reviews_created': 0,
        'reviews_skipped': 0,
        'errors': 0
    }
    
    with app.app_context():
        # Process each review
        for review_data in tqdm(reviews_data, desc="Importing reviews"):
            try:
                # Extract product data and handle BOM character
                asin = review_data.get('asins') or review_data.get('\ufeffasins') or review_data.get('asin') or review_data.get('product_id')
                product_title = review_data.get('name') or review_data.get('product_title') or review_data.get('product_name') or review_data.get('title')
                
                # Clean up ASIN if it's a list
                if isinstance(asin, str) and ',' in asin:
                    asin = asin.split(',')[0].strip()
                
                if not asin or not product_title:
                    logger.warning(f"Missing required product data. ASIN: {asin}, Title: {product_title}")
                    stats['errors'] += 1
                    continue
                
                # Check if product exists
                product = Product.query.filter_by(asin=asin).first()
                
                if not product:
                    # Create new product
                    product = Product(
                        asin=asin,
                        name=product_title,
                        description=review_data.get('product_description', ''),
                        price=float(review_data.get('price', 0)) if review_data.get('price') else None,
                        category=review_data.get('category', '')
                    )
                    db.session.add(product)
                    try:
                        db.session.commit()
                        stats['products_created'] += 1
                    except IntegrityError:
                        db.session.rollback()
                        logger.warning(f"Duplicate product: {asin}")
                        product = Product.query.filter_by(asin=asin).first()
                        stats['products_skipped'] += 1
                else:
                    stats['products_skipped'] += 1
                
                # Extract review data from CSV structure
                review_text = review_data.get('reviews.text')
                reviewer_name = review_data.get('reviews.username')
                rating = float(review_data.get('reviews.rating', 0))
                review_date_str = review_data.get('reviews.date')
                review_date = parse_date(review_date_str) if review_date_str else None
                
                if not review_text:
                    logger.warning(f"Missing required review data: {review_data}")
                    stats['errors'] += 1
                    continue
                
                # Check if review already exists (simple check - real implementation might be more complex)
                existing_review = Review.query.filter_by(
                    product_id=product.id, 
                    author=reviewer_name, 
                    text=review_text
                ).first()
                
                if existing_review:
                    logger.debug(f"Duplicate review for product {asin}")
                    stats['reviews_skipped'] += 1
                    continue
                
                # Analyze sentiment
                sentiment_score = analyze_sentiment(review_text)
                sentiment_class = classify_sentiment(sentiment_score)
                sentiment_keywords = get_sentiment_keywords(review_text, sentiment_class)
                
                # Create new review
                review = Review(
                    product_id=product.id,
                    author=reviewer_name,
                    text=review_text,
                    rating=rating,
                    date=review_date,
                    sentiment_score=sentiment_score,
                    sentiment_class=sentiment_class,
                    sentiment_keywords=json.dumps(sentiment_keywords)
                )
                
                db.session.add(review)
                try:
                    db.session.commit()
                    stats['reviews_created'] += 1
                except IntegrityError:
                    db.session.rollback()
                    logger.warning(f"Error saving review: {sys.exc_info()[0]}")
                    stats['reviews_skipped'] += 1
                
            except Exception as e:
                db.session.rollback()
                logger.error(f"Error processing review: {str(e)}")
                stats['errors'] += 1
    
    logger.info(f"Import complete. Stats: {stats}")
    return stats

def update_sentiment_scores():
    """Update sentiment score caches for all products"""
    logger.info("Updating product sentiment scores")
    
    with app.app_context():
        products = Product.query.all()
        
        for product in tqdm(products, desc="Updating sentiment scores"):
            reviews = Review.query.filter_by(product_id=product.id).all()
            
            if not reviews:
                continue
            
            # Calculate sentiment distribution
            positive = sum(1 for r in reviews if r.sentiment_class == 'positive')
            neutral = sum(1 for r in reviews if r.sentiment_class == 'neutral')
            negative = sum(1 for r in reviews if r.sentiment_class == 'negative')
            total = len(reviews)
            
            # Update product sentiment scores
            product.positive_score = positive / total if total > 0 else 0
            product.neutral_score = neutral / total if total > 0 else 0
            product.negative_score = negative / total if total > 0 else 0
            
            db.session.add(product)
        
        db.session.commit()
        logger.info(f"Updated sentiment scores for {len(products)} products")

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Import Amazon reviews data')
    parser.add_argument('file_path', type=str, help='Path to the reviews data file (CSV or JSON)')
    parser.add_argument('--format', type=str, choices=['csv', 'json'], help='File format (csv or json)')
    parser.add_argument('--limit', type=int, help='Limit the number of reviews to import')
    
    args = parser.parse_args()
    
    # Determine format from file extension if not specified
    file_format = args.format
    if not file_format:
        if args.file_path.lower().endswith('.json'):
            file_format = 'json'
        elif args.file_path.lower().endswith('.csv'):
            file_format = 'csv'
        else:
            print("Error: Could not determine file format. Please specify --format")
            sys.exit(1)
    
    # Import reviews
    if file_format == 'json':
        import_json_reviews(args.file_path, args.limit)
    else:
        import_csv_reviews(args.file_path, args.limit)
    
    # Update sentiment scores
    update_sentiment_scores()