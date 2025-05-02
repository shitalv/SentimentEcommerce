"""
Direct Admin Access

This script provides a direct way to access the admin dashboard with no authentication.
"""

import os
import logging
from flask import Flask, render_template, jsonify, redirect
from mongo_config import get_mongo_client
from datetime import datetime, timedelta

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a standalone Flask app for direct admin access
app = Flask(__name__, 
            template_folder="./templates",
            static_folder="./static")

# Simple home route
@app.route('/')
def home():
    return render_template('admin/dashboard.html')

# Analytics API route
@app.route('/admin/analytics')
def analytics():
    """Get analytics data for admin dashboard"""
    try:
        mongo_client, db = get_mongo_client()
        if db is None:
            return jsonify({"error": "Database connection failed"}), 500
        
        # Get product count
        product_count = db.products.count_documents({})
        
        # Get review count
        review_count = db.reviews.count_documents({})
        
        # Get user count
        user_count = db.users.count_documents({})
        
        # Get sentiment statistics
        products = list(db.products.find({}, {"_id": 1, "positive_score": 1, "neutral_score": 1, "negative_score": 1}))
        
        # Calculate average sentiment
        sentiment_stats = {
            "positive": 0,
            "neutral": 0,
            "negative": 0
        }
        
        if products:
            for product in products:
                sentiment_stats["positive"] += product.get("positive_score", 0)
                sentiment_stats["neutral"] += product.get("neutral_score", 0)
                sentiment_stats["negative"] += product.get("negative_score", 0)
            
            # Calculate averages
            count = len(products)
            sentiment_stats["positive"] = round(sentiment_stats["positive"] / count, 2)
            sentiment_stats["neutral"] = round(sentiment_stats["neutral"] / count, 2)
            sentiment_stats["negative"] = round(sentiment_stats["negative"] / count, 2)
        
        # Get recent reviews (last 7 days)
        week_ago = datetime.now() - timedelta(days=7)
        recent_reviews = db.reviews.count_documents({"created_at": {"$gte": week_ago}})
        
        # Get top categories
        pipeline = [
            {"$group": {"_id": "$category", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 5}
        ]
        top_categories = list(db.products.aggregate(pipeline))
        
        # Get top products by sentiment
        top_products = list(db.products.find().sort("positive_score", -1).limit(5))
        top_products_data = []
        
        for product in top_products:
            top_products_data.append({
                "id": str(product.get("_id")),
                "name": product.get("name"),
                "sentiment_score": product.get("positive_score", 0),
                "review_count": db.reviews.count_documents({"product_id": str(product.get("_id"))})
            })
        
        # Return all analytics data
        return jsonify({
            "product_count": product_count,
            "review_count": review_count,
            "user_count": user_count,
            "sentiment_stats": sentiment_stats,
            "recent_reviews": recent_reviews,
            "top_categories": top_categories,
            "top_products": top_products_data
        })
    
    except Exception as e:
        logger.error(f"Error getting admin analytics: {str(e)}")
        return jsonify({"error": f"Failed to get analytics data: {str(e)}"}), 500

# Add routes for other admin sections
@app.route('/admin/reports/sentiment')
def sentiment_reports():
    return render_template('admin/reports/sentiment.html')

@app.route('/admin/reports/hype-reality')
def hype_reality():
    return render_template('admin/reports/hype_reality.html')

@app.route('/admin/products')
def products():
    return render_template('admin/products.html')

@app.route('/admin/reviews')
def reviews():
    return render_template('admin/reviews.html')

@app.route('/admin/users')
def users():
    return render_template('admin/users.html')

if __name__ == "__main__":
    # Use a port different from the main app
    port = 8000
    print(f"======================================================")
    print(f"  DIRECT ADMIN ACCESS")
    print(f"  Access the admin dashboard at http://localhost:{port}")
    print(f"======================================================")
    
    # Run the app
    app.run(host="0.0.0.0", port=port, debug=True)