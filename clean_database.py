"""
Database Cleaning and Maintenance Script

This script performs various data cleaning operations on the existing database:
1. Normalizes and cleans review text
2. Updates sentiment scores
3. Identifies and fixes inconsistencies
4. Repairs broken relationships

Run this script periodically to maintain data quality.
"""

import logging
import sys
import os
from tqdm import tqdm
import re
import html

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('database_cleaner')

from app import app, db
from models import Product, Review
from backend.sentiment_analyzer import analyze_sentiment, classify_sentiment, get_sentiment_keywords
import json

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

def fix_broken_reviews():
    """Find and fix reviews with broken data"""
    logger.info("Finding and fixing broken review data...")
    
    with app.app_context():
        reviews = Review.query.all()
        
        fixed_count = 0
        for review in tqdm(reviews, desc="Fixing broken reviews"):
            needs_update = False
            
            # Fix missing sentiment classification
            if not review.sentiment_class:
                if review.sentiment_score is not None:
                    review.sentiment_class = classify_sentiment(review.sentiment_score)
                    needs_update = True
                else:
                    # Both are missing, recalculate
                    review.sentiment_score = analyze_sentiment(review.text)
                    review.sentiment_class = classify_sentiment(review.sentiment_score)
                    needs_update = True
                    
            # Fix missing sentiment score
            elif review.sentiment_score is None:
                review.sentiment_score = analyze_sentiment(review.text)
                needs_update = True
                
            # Fix missing sentiment keywords
            if not review.sentiment_keywords:
                keywords = get_sentiment_keywords(review.text, review.sentiment_class)
                review.sentiment_keywords = json.dumps(keywords)
                needs_update = True
            
            # Ensure valid rating
            if review.rating is None or review.rating < 1 or review.rating > 5:
                review.rating = 3.0  # Default to neutral
                needs_update = True
            
            if needs_update:
                db.session.add(review)
                fixed_count += 1
        
        if fixed_count > 0:
            db.session.commit()
            logger.info(f"Fixed {fixed_count} reviews with data issues")
        else:
            logger.info("No reviews needed data fixes")

def fix_product_scores():
    """Find and fix products with invalid sentiment scores"""
    logger.info("Finding and fixing products with invalid sentiment scores...")
    
    with app.app_context():
        products = Product.query.all()
        
        fixed_count = 0
        for product in tqdm(products, desc="Fixing product scores"):
            needs_update = False
            
            # Check for invalid scores
            scores_invalid = (
                product.positive_score is None or 
                product.neutral_score is None or 
                product.negative_score is None or
                product.positive_score < 0 or product.positive_score > 1 or
                product.neutral_score < 0 or product.neutral_score > 1 or
                product.negative_score < 0 or product.negative_score > 1
            )
            
            # Check if scores add up to approximately 1.0
            scores_sum = (product.positive_score or 0) + (product.neutral_score or 0) + (product.negative_score or 0)
            scores_dont_add_up = abs(scores_sum - 1.0) > 0.01 if scores_sum > 0 else True
            
            if scores_invalid or scores_dont_add_up:
                reviews = Review.query.filter_by(product_id=product.id).all()
                
                if reviews:
                    # Calculate sentiment distribution
                    positive = sum(1 for r in reviews if r.sentiment_class == 'positive')
                    neutral = sum(1 for r in reviews if r.sentiment_class == 'neutral')
                    negative = sum(1 for r in reviews if r.sentiment_class == 'negative')
                    total = len(reviews)
                    
                    # Update product sentiment scores
                    product.positive_score = positive / total if total > 0 else 0
                    product.neutral_score = neutral / total if total > 0 else 0
                    product.negative_score = negative / total if total > 0 else 0
                    needs_update = True
                else:
                    # No reviews, set to neutral
                    product.positive_score = 0
                    product.neutral_score = 1
                    product.negative_score = 0
                    needs_update = True
            
            if needs_update:
                db.session.add(product)
                fixed_count += 1
        
        if fixed_count > 0:
            db.session.commit()
            logger.info(f"Fixed {fixed_count} products with invalid sentiment scores")
        else:
            logger.info("No products needed score fixes")

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

def run_cleanup():
    """Run all cleanup operations"""
    try:
        logger.info("Starting database cleanup...")
        
        # Fix all issues
        normalize_reviews_text()
        fix_broken_reviews()
        fix_product_scores()
        
        logger.info("Database cleanup completed successfully")
    except Exception as e:
        logger.error(f"Database cleanup failed: {str(e)}")

if __name__ == "__main__":
    run_cleanup()