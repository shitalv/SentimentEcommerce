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
import re
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from tqdm import tqdm  # For progress bar
import pandas as pd
import html

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
            except Exception as e:
                logger.error(f"Error processing row: {str(e)}")
                continue
    
    import_reviews(reviews)

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
        return float(value)
        
    if isinstance(value, str):
        # Remove currency symbols and commas
        value = re.sub(r'[$,£€]', '', value)
        
        # Extract the first number found
        match = re.search(r'([-+]?\d*\.?\d+)', value)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                return None
    
    return None

def import_reviews(reviews_data):
    """Process and import reviews into the database"""
    logger.info(f"Processing {len(reviews_data)} reviews")
    
    # Track stats
    stats = {
        'products_created': 0,
        'products_skipped': 0,
        'reviews_created': 0,
        'reviews_skipped': 0,
        'errors': 0,
        'cleaned_data': 0
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
                
                # Clean up data
                if asin:
                    asin = asin.strip().upper()  # ASINs are typically uppercase
                
                # Clean product title and description
                product_title = clean_text(product_title)
                product_description = clean_text(review_data.get('product_description') or review_data.get('description') or '')
                
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
                        description=product_description,
                        price=clean_number(review_data.get('price')),
                        category=clean_text(review_data.get('category') or '')
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
                
                # Extract and clean review data from various formats
                review_text = clean_text(review_data.get('reviews.text') or review_data.get('review_text') or review_data.get('reviewText') or review_data.get('text') or '')
                reviewer_name = clean_text(review_data.get('reviews.username') or review_data.get('reviewer_name') or review_data.get('reviewerName') or review_data.get('author') or 'Anonymous')
                
                # Clean rating value (1-5 stars)
                raw_rating = review_data.get('reviews.rating') or review_data.get('rating') or review_data.get('star_rating') or review_data.get('overall') or 0
                rating = clean_number(raw_rating)
                if rating is not None:
                    # Ensure rating is between 1-5
                    rating = max(1, min(5, rating))
                else:
                    rating = 3.0  # Default to neutral rating
                
                # Clean and parse review date
                review_date_str = review_data.get('reviews.date') or review_data.get('review_date') or review_data.get('reviewTime') or review_data.get('date')
                review_date = parse_date(review_date_str) if review_date_str else None
                
                if not review_text or len(review_text) < 5:  # Skip very short reviews
                    logger.warning(f"Missing or too short review text for product {asin}")
                    stats['errors'] += 1
                    continue
                    
                # Log that we cleaned some data
                stats['cleaned_data'] += 1
                
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

def normalize_reviews_text():
    """Clean and normalize existing review text in the database"""
    logger.info("Normalizing existing review text...")
    
    with app.app_context():
        reviews = Review.query.all()
        
        updated_count = 0
        for review in tqdm(reviews, desc="Normalizing reviews"):
            # Clean text and check if anything changed
            original_text = review.text
            cleaned_text = clean_text(original_text)
            
            if original_text != cleaned_text:
                review.text = cleaned_text
                
                # Recalculate sentiment with cleaned text
                sentiment_score = analyze_sentiment(cleaned_text)
                sentiment_class = classify_sentiment(sentiment_score)
                sentiment_keywords = get_sentiment_keywords(cleaned_text, sentiment_class)
                
                review.sentiment_score = sentiment_score
                review.sentiment_class = sentiment_class
                review.sentiment_keywords = json.dumps(sentiment_keywords)
                
                db.session.add(review)
                updated_count += 1
        
        if updated_count > 0:
            db.session.commit()
            logger.info(f"Normalized text for {updated_count} reviews")
        else:
            logger.info("No reviews needed text normalization")

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
    
    # Clean and normalize review text
    normalize_reviews_text()
    
    # Update sentiment scores
    update_sentiment_scores()