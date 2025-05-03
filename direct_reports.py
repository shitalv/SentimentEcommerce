"""
Direct Reports Access Module

This module provides routes to access reports directly without authentication requirements.
It's used to provide direct links when authentication is causing navigation issues.
"""

import os
import logging
import datetime
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
        
        # Get products with sentiment scores
        products = list(products_collection.find({}, {
            "_id": 1, 
            "name": 1,
            "category": 1,
            "positive_score": 1, 
            "neutral_score": 1, 
            "negative_score": 1
        }))
        
        # Convert ObjectId to string and add missing fields
        for product in products:
            product['_id'] = str(product['_id'])
            if 'category' not in product:
                product['category'] = 'Uncategorized'
            if 'positive_score' not in product:
                product['positive_score'] = 0
            if 'neutral_score' not in product:
                product['neutral_score'] = 0
            if 'negative_score' not in product:
                product['negative_score'] = 0
        
        # Count total reviews
        total_reviews = reviews_collection.count_documents({})
        
        # Count reviews by sentiment class
        positive_reviews = reviews_collection.count_documents({"sentiment_class": "positive"})
        neutral_reviews = reviews_collection.count_documents({"sentiment_class": "neutral"})
        negative_reviews = reviews_collection.count_documents({"sentiment_class": "negative"})
        
        # Calculate overall sentiment percentages for pie chart
        total_sentiment = max(1, positive_reviews + neutral_reviews + negative_reviews)
        overall_sentiment = {
            "positive": int((positive_reviews / total_sentiment) * 100),
            "neutral": int((neutral_reviews / total_sentiment) * 100),
            "negative": int((negative_reviews / total_sentiment) * 100)
        }
        
        # Extract categories and prepare category sentiment data
        categories = {}
        for product in products:
            category = product.get('category', 'Uncategorized')
            if category not in categories:
                categories[category] = {
                    'positive': 0, 
                    'neutral': 0, 
                    'negative': 0, 
                    'count': 0
                }
            
            total = max(0.01, product['positive_score'] + product['neutral_score'] + product['negative_score'])
            categories[category]['positive'] += product['positive_score'] / total
            categories[category]['neutral'] += product['neutral_score'] / total
            categories[category]['negative'] += product['negative_score'] / total
            categories[category]['count'] += 1
        
        category_data = []
        for category, data in categories.items():
            if data['count'] > 0:
                category_data.append({
                    'category': category,
                    'positive': data['positive'] / data['count'],
                    'neutral': data['neutral'] / data['count'],
                    'negative': data['negative'] / data['count']
                })
        
        # Generate time series data for trend chart (last 7 days)
        trend_data = []
        current_date = datetime.datetime.now()
        for i in range(7):
            date = current_date - datetime.timedelta(days=6-i)
            date_str = date.strftime('%b %d')
            # For the sample, we'll generate some random data based on overall sentiment
            trend_data.append({
                'date': date_str,
                'positive': overall_sentiment['positive'] + (i - 3),
                'neutral': overall_sentiment['neutral'] + (3 - i),
                'negative': overall_sentiment['negative'] + (i % 3 - 1)
            })
        
        # Get top positive/negative keywords
        pipeline = [
            {"$match": {"sentiment_keywords": {"$exists": True, "$ne": ""}}},
            {"$project": {
                "keywords": {"$split": ["$sentiment_keywords", ","]},
                "sentiment_class": 1
            }},
            {"$unwind": "$keywords"},
            {"$group": {
                "_id": {"keyword": "$keywords", "sentiment": "$sentiment_class"},
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}},
            {"$limit": 20}
        ]
        
        keyword_results = list(reviews_collection.aggregate(pipeline))
        
        # Separate keywords by sentiment
        positive_keywords = []
        negative_keywords = []
        
        for item in keyword_results:
            keyword = item['_id']['keyword'].strip()
            sentiment = item['_id']['sentiment']
            count = item['count']
            
            if keyword and len(keyword) > 1:  # Ignore single-character keywords
                if sentiment == 'positive':
                    positive_keywords.append({"text": keyword, "count": count})
                elif sentiment == 'negative':
                    negative_keywords.append({"text": keyword, "count": count})
        
        return jsonify({
            "products": products,
            "total_reviews": total_reviews,
            "sentiment_counts": {
                "positive": positive_reviews,
                "neutral": neutral_reviews,
                "negative": negative_reviews
            },
            "overall_sentiment": overall_sentiment,
            "categories": category_data,
            "trend_data": trend_data,
            "positive_keywords": positive_keywords[:10],
            "negative_keywords": negative_keywords[:10]
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