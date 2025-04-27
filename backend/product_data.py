"""
Product Data Access Module for MongoDB

This module provides functions to access product data from MongoDB.
"""

import logging
import json
from models_mongo import Product, Review
from mongo_config import get_db, USE_MOCK_DB
from backend.sentiment_analyzer import analyze_sentiment, classify_sentiment, get_sentiment_keywords

# Set up logging
logger = logging.getLogger(__name__)

def get_products(query=None, category=None, min_sentiment=None, max_sentiment=None):
    """
    Return all products with basic sentiment analysis from database
    """
    try:
        # Get products from MongoDB
        products_list = []
        
        if USE_MOCK_DB:
            # Using sample data
            db = get_db()
            for product_id, product_data in db["products"].items():
                # Apply filters
                if category and product_data.get("category") != category:
                    continue
                    
                if query and query.lower() not in product_data.get("name", "").lower() and query.lower() not in product_data.get("description", "").lower():
                    continue
                    
                if min_sentiment and product_data.get("positive_score", 0) < min_sentiment:
                    continue
                    
                if max_sentiment and product_data.get("positive_score", 1) > max_sentiment:
                    continue
                
                # Add to results
                products_list.append({
                    "id": product_id,
                    "name": product_data.get("name"),
                    "price": product_data.get("price"),
                    "category": product_data.get("category"),
                    "image_url": product_data.get("image_url"),
                    "sentiment": {
                        "positive": product_data.get("positive_score", 0),
                        "neutral": product_data.get("neutral_score", 0),
                        "negative": product_data.get("negative_score", 0)
                    }
                })
        else:
            # Using real MongoDB
            products = Product.get_all(category=category, query=query)
            
            for product in products:
                # Filter by sentiment if needed
                if min_sentiment and product.positive_score < min_sentiment:
                    continue
                    
                if max_sentiment and product.positive_score > max_sentiment:
                    continue
                
                # Add to results
                products_list.append({
                    "id": product.id,
                    "name": product.name,
                    "price": product.price,
                    "category": product.category,
                    "image_url": product.image_url,
                    "sentiment": {
                        "positive": product.positive_score,
                        "neutral": product.neutral_score,
                        "negative": product.negative_score
                    }
                })
                
        return products_list
    except Exception as e:
        logger.error(f"Error getting products: {str(e)}")
        return []

def get_product_by_id(product_id):
    """
    Return product by ID with detailed sentiment analysis from database
    """
    try:
        # Get product from database
        product_data = None
        reviews_data = []
        
        if USE_MOCK_DB:
            # Using sample data
            db = get_db()
            if product_id not in db["products"]:
                return None
                
            p_data = db["products"][product_id]
            product_data = {
                "id": product_id,
                "name": p_data.get("name"),
                "price": p_data.get("price"),
                "category": p_data.get("category"),
                "description": p_data.get("description"),
                "image_url": p_data.get("image_url"),
                "sentiment": {
                    "positive": p_data.get("positive_score", 0),
                    "neutral": p_data.get("neutral_score", 0),
                    "negative": p_data.get("negative_score", 0)
                }
            }
            
            # Get reviews for this product
            for review_id, review_data in db["reviews"].items():
                if review_data.get("product_id") == product_id:
                    reviews_data.append({
                        "id": review_id,
                        "author": review_data.get("author"),
                        "text": review_data.get("text"),
                        "rating": review_data.get("rating"),
                        "date": review_data.get("date"),
                        "sentiment": {
                            "score": review_data.get("sentiment_score", 0),
                            "class": review_data.get("sentiment_class", "neutral"),
                            "keywords": json.loads(review_data.get("sentiment_keywords", "[]"))
                        }
                    })
        else:
            # Using real MongoDB
            product = Product.get_by_id(product_id)
            if not product:
                return None
                
            product_data = {
                "id": product.id,
                "name": product.name,
                "price": product.price,
                "category": product.category,
                "description": product.description,
                "image_url": product.image_url,
                "sentiment": {
                    "positive": product.positive_score,
                    "neutral": product.neutral_score,
                    "negative": product.negative_score
                }
            }
            
            # Get reviews for this product
            reviews = product.get_reviews()
            for review in reviews:
                reviews_data.append({
                    "id": review.id,
                    "author": review.author,
                    "text": review.text,
                    "rating": review.rating,
                    "date": review.date,
                    "sentiment": {
                        "score": review.sentiment_score,
                        "class": review.sentiment_class,
                        "keywords": json.loads(review.sentiment_keywords) if review.sentiment_keywords else []
                    }
                })
                
        # Add reviews to product data
        product_data["reviews"] = reviews_data
        
        return product_data
    except Exception as e:
        logger.error(f"Error getting product {product_id}: {str(e)}")
        return None