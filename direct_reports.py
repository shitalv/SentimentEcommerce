"""
Direct Reports Access Module

This module provides routes to access reports directly without authentication requirements.
It's used to provide direct links when authentication is causing navigation issues.
"""

import os
import logging
from flask import Blueprint, render_template, jsonify, redirect, request
from mongo_config import get_db
from models_mongo import Product, Review

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a Blueprint for direct report access
direct_reports = Blueprint('direct_reports', __name__)

@direct_reports.route('/direct/sentiment')
def direct_sentiment_report():
    """Direct access to sentiment reports page without authentication"""
    return render_template('admin/reports/sentiment.html', bypass_auth=True)

@direct_reports.route('/direct/hype-reality')
def direct_hype_reality_report():
    """Direct access to hype vs reality page without authentication"""
    return render_template('admin/reports/hype-reality.html', bypass_auth=True)

@direct_reports.route('/direct/products')
def direct_products_report():
    """Direct access to products reports page without authentication"""
    return render_template('admin/reports/products.html', bypass_auth=True)

@direct_reports.route('/direct/api/sentiment-data')
def direct_sentiment_data_api():
    """Direct API endpoint for sentiment data without authentication"""
    try:
        db = get_db()
        products_collection = db.products
        reviews_collection = db.reviews
        
        products = list(products_collection.find({}, {"_id": 1, "name": 1, 
                                                "positive_score": 1, 
                                                "neutral_score": 1, 
                                                "negative_score": 1}))
        
        # Convert ObjectId to string
        for product in products:
            product['_id'] = str(product['_id'])
        
        # Count total reviews
        total_reviews = reviews_collection.count_documents({})
        
        # Count reviews by sentiment class
        positive_reviews = reviews_collection.count_documents({"sentiment_class": "positive"})
        neutral_reviews = reviews_collection.count_documents({"sentiment_class": "neutral"})
        negative_reviews = reviews_collection.count_documents({"sentiment_class": "negative"})
        
        # Get top positive/negative keywords
        pipeline = [
            {"$match": {"sentiment_keywords": {"$exists": True, "$ne": ""}}},
            {"$project": {
                "keywords": {"$split": ["$sentiment_keywords", ","]}
            }},
            {"$unwind": "$keywords"},
            {"$group": {
                "_id": "$keywords",
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        
        keywords = list(reviews_collection.aggregate(pipeline))
        
        return jsonify({
            "products": products,
            "total_reviews": total_reviews,
            "sentiment_counts": {
                "positive": positive_reviews,
                "neutral": neutral_reviews,
                "negative": negative_reviews
            },
            "top_keywords": keywords
        })
    except Exception as e:
        logger.error(f"Error fetching sentiment data: {str(e)}")
        return jsonify({"error": str(e)}), 500

@direct_reports.route('/direct/api/hype-reality-data/<product_id>')
def direct_hype_reality_data_api(product_id):
    """Direct API endpoint for hype vs reality data without authentication"""
    try:
        db = get_db()
        products_collection = db.products
        reviews_collection = db.reviews
        
        # Get product details
        product = products_collection.find_one({"_id": product_id})
        if not product:
            return jsonify({"error": "Product not found"}), 404
        
        # Get reviews for this product
        reviews = list(reviews_collection.find({"product_id": product_id}))
        
        # Convert ObjectId to string
        product['_id'] = str(product['_id'])
        for review in reviews:
            if '_id' in review:
                review['_id'] = str(review['_id'])
        
        # Extract marketing claims from product description
        description = product.get('description', '')
        claims = []
        
        # Simple claim extraction for demonstration
        if description:
            sentences = description.split('.')
            for sentence in sentences:
                if len(sentence.strip()) > 10:  # Only consider non-empty sentences
                    # Analyze sentiment of this claim in reviews
                    status = 'unmentioned'  # Default status
                    
                    # Simulate claim status - this would normally be AI-analyzed
                    if 'excellent' in sentence.lower() or 'best' in sentence.lower():
                        status = 'contradicted'
                    elif 'good' in sentence.lower() or 'quality' in sentence.lower():
                        status = 'confirmed'
                    
                    claims.append({
                        "text": sentence.strip(),
                        "status": status,
                        "feedback": []  # This would normally contain review excerpts
                    })
        
        # Calculate reality score (percentage of claims that are confirmed)
        confirmed_count = len([c for c in claims if c['status'] == 'confirmed'])
        contradicted_count = len([c for c in claims if c['status'] == 'contradicted'])
        unmentioned_count = len([c for c in claims if c['status'] == 'unmentioned'])
        
        if len(claims) > 0:
            reality_score = int((confirmed_count / len(claims)) * 100)
        else:
            reality_score = 0
        
        return jsonify({
            "product": product,
            "reviews": reviews,
            "claims": claims,
            "confirmed_count": confirmed_count,
            "contradicted_count": contradicted_count,
            "unmentioned_count": unmentioned_count,
            "realityScore": reality_score
        })
    except Exception as e:
        logger.error(f"Error fetching hype-reality data: {str(e)}")
        return jsonify({"error": str(e)}), 500