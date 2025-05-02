"""
Admin Dashboard Module

This module contains functions and routes for the admin dashboard.
"""

import logging
import json
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps
from mongo_config import get_mongo_client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('admin')

# Create blueprint
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Admin-only decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login_page'))
            
        if not getattr(current_user, 'is_admin', False):
            return render_template('error.html', 
                                 error_title="Access Denied", 
                                 error_message="Administrator access required")
                                 
        return f(*args, **kwargs)
    return decorated_function

# Special helper route - no auth required
@admin_bp.route('/nav-helper')
def admin_nav_helper():
    """Admin navigation helper page without authentication"""
    return render_template('admin/nav_helper.html')

# Direct access portal to all admin functions
@admin_bp.route('/direct-access')
@login_required
@admin_required
def admin_direct_access():
    """Direct access portal to all admin pages"""
    return render_template('admin_direct_access.html')

# Admin dashboard home
@admin_bp.route('/')
@login_required
@admin_required
def admin_dashboard():
    """Admin dashboard homepage"""
    return render_template('admin/dashboard.html')

# Get admin analytics data
@admin_bp.route('/analytics')
@login_required
@admin_required
def admin_analytics():
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

# Get all products for admin
@admin_bp.route('/products')
@login_required
@admin_required
def admin_products():
    """Get all products for admin management"""
    # Check if this is a JSON API request or HTML page request
    if request.headers.get('Accept') == 'application/json' or request.args.get('format') == 'json':
        try:
            mongo_client, db = get_mongo_client()
            if db is None:
                return jsonify({"error": "Database connection failed"}), 500
            
            # Get all products with pagination
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 10))
            skip = (page - 1) * per_page
            
            # Get products
            products = list(db.products.find().skip(skip).limit(per_page))
            
            # Format product data
            product_data = []
            for product in products:
                product_data.append({
                    "id": str(product.get("_id")),
                    "name": product.get("name"),
                    "category": product.get("category"),
                    "price": product.get("price"),
                    "review_count": db.reviews.count_documents({"product_id": str(product.get("_id"))}),
                    "positive_score": product.get("positive_score", 0),
                    "neutral_score": product.get("neutral_score", 0),
                    "negative_score": product.get("negative_score", 0),
                    "created_at": product.get("created_at")
                })
            
            # Get total count for pagination
            total_products = db.products.count_documents({})
            total_pages = (total_products + per_page - 1) // per_page
            
            return jsonify({
                "products": product_data,
                "pagination": {
                    "current_page": page,
                    "per_page": per_page,
                    "total_products": total_products,
                    "total_pages": total_pages
                }
            })
        
        except Exception as e:
            logger.error(f"Error getting admin products: {str(e)}")
            return jsonify({"error": f"Failed to get products: {str(e)}"}), 500
    else:
        # Render the HTML template for the admin products page
        return render_template('admin/products.html')

# Get all reviews for admin
@admin_bp.route('/reviews')
@login_required
@admin_required
def admin_reviews():
    """Get all reviews for admin moderation"""
    # Check if this is a JSON API request or HTML page request
    if request.headers.get('Accept') == 'application/json' or request.args.get('format') == 'json':
        try:
            mongo_client, db = get_mongo_client()
            if db is None:
                return jsonify({"error": "Database connection failed"}), 500
            
            # Get all reviews with pagination
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 20))
            skip = (page - 1) * per_page
            
            # Get filter parameters
            product_id = request.args.get('product_id')
            sentiment = request.args.get('sentiment')
            search_term = request.args.get('search')
            
            # Build query
            query = {}
            if product_id:
                query["product_id"] = product_id
            if sentiment:
                query["sentiment_class"] = sentiment
            if search_term:
                query["$text"] = {"$search": search_term}
            
            # Get reviews
            reviews = list(db.reviews.find(query).sort("created_at", -1).skip(skip).limit(per_page))
            
            # Format review data
            review_data = []
            for review in reviews:
                # Get product information
                product_id = review.get("product_id")
                product = db.products.find_one({"_id": product_id}) if product_id else None
                
                review_data.append({
                    "id": str(review.get("_id")),
                    "product_id": review.get("product_id"),
                    "product_name": product.get("name") if product else "Unknown Product",
                    "author": review.get("author"),
                    "text": review.get("text"),
                    "rating": review.get("rating"),
                    "sentiment_score": review.get("sentiment_score"),
                    "sentiment_class": review.get("sentiment_class"),
                    "date": review.get("date"),
                    "created_at": review.get("created_at")
                })
            
            # Get total count for pagination
            total_reviews = db.reviews.count_documents(query)
            total_pages = (total_reviews + per_page - 1) // per_page
            
            return jsonify({
                "reviews": review_data,
                "pagination": {
                    "current_page": page,
                    "per_page": per_page,
                    "total_reviews": total_reviews,
                    "total_pages": total_pages
                }
            })
        
        except Exception as e:
            logger.error(f"Error getting admin reviews: {str(e)}")
            return jsonify({"error": f"Failed to get reviews: {str(e)}"}), 500
    else:
        # Render the HTML template for the admin reviews page
        return render_template('admin/reviews.html')

# User management for admin
@admin_bp.route('/users')
@login_required
@admin_required
def admin_users():
    """Get all users for admin management"""
    # Check if this is a JSON API request or HTML page request
    if request.headers.get('Accept') == 'application/json' or request.args.get('format') == 'json':
        try:
            mongo_client, db = get_mongo_client()
            if db is None:
                return jsonify({"error": "Database connection failed"}), 500
            
            # Get all users with pagination
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 10))
            skip = (page - 1) * per_page
            
            # Get filter parameters
            search_term = request.args.get('search')
            is_admin = request.args.get('is_admin')
            
            # Build query
            query = {}
            if search_term:
                query["$or"] = [
                    {"username": {"$regex": search_term, "$options": "i"}},
                    {"email": {"$regex": search_term, "$options": "i"}}
                ]
            if is_admin is not None:
                query["is_admin"] = is_admin.lower() == 'true'
            
            # Get users
            users = list(db.users.find(query).skip(skip).limit(per_page))
            
            # Format user data (excluding password hash)
            user_data = []
            for user in users:
                user_data.append({
                    "id": str(user.get("_id")),
                    "username": user.get("username"),
                    "email": user.get("email"),
                    "is_admin": user.get("is_admin", False),
                    "created_at": user.get("created_at"),
                    # Count saved products
                    "saved_products_count": db.user_saved_products.count_documents({"user_id": str(user.get("_id"))})
                })
            
            # Get total count for pagination
            total_users = db.users.count_documents(query)
            total_pages = (total_users + per_page - 1) // per_page
            
            return jsonify({
                "users": user_data,
                "pagination": {
                    "current_page": page,
                    "per_page": per_page,
                    "total_users": total_users,
                    "total_pages": total_pages
                }
            })
        
        except Exception as e:
            logger.error(f"Error getting admin users: {str(e)}")
            return jsonify({"error": f"Failed to get users: {str(e)}"}), 500
    else:
        # Render the HTML template for the admin users page
        return render_template('admin/users.html')

# Sentiment analysis reports for admin
@admin_bp.route('/reports/sentiment')
@login_required
@admin_required
def sentiment_reports():
    """Sentiment analysis reports for admin"""
    return render_template('admin/reports/sentiment.html')

# API endpoint for sentiment report data
@admin_bp.route('/api/reports/sentiment')
@login_required
@admin_required
def sentiment_report_data():
    """Get sentiment report data for admin dashboard"""
    try:
        mongo_client, db = get_mongo_client()
        if db is None:
            return jsonify({"error": "Database connection failed"}), 500
        
        # Get time period from request
        time_period = request.args.get('period', 'all')
        
        # Build query for the time period
        query = {}
        if time_period != 'all':
            days = int(time_period)
            date_threshold = datetime.now() - timedelta(days=days)
            query["created_at"] = {"$gte": date_threshold}
        
        # Get all products matching the time period
        products = list(db.products.find(query))
        
        # Calculate overall sentiment distribution
        overall_sentiment = {
            "positive": 0,
            "neutral": 0,
            "negative": 0
        }
        
        product_data = []
        category_sentiment = {}
        
        # Process each product
        for product in products:
            if not product:
                continue
                
            # Get product reviews count
            product_id = str(product.get("_id"))
            reviews_count = db.reviews.count_documents({"product_id": product_id})
            
            # Get sentiment scores
            pos_score = product.get("positive_score", 0)
            neut_score = product.get("neutral_score", 0)
            neg_score = product.get("negative_score", 0)
            
            # Skip products with no sentiment data
            if pos_score == 0 and neut_score == 0 and neg_score == 0:
                continue
                
            # Add to overall sentiment
            overall_sentiment["positive"] += pos_score
            overall_sentiment["neutral"] += neut_score
            overall_sentiment["negative"] += neg_score
            
            # Add to product data
            product_data.append({
                "id": product_id,
                "name": product.get("name", "Unknown Product"),
                "category": product.get("category", "Uncategorized"),
                "reviews_count": reviews_count,
                "positive_score": pos_score,
                "neutral_score": neut_score,
                "negative_score": neg_score,
                "overall_score": (pos_score * 5 + neut_score * 3 + neg_score * 1) / 
                                 max(1, (pos_score + neut_score + neg_score))
            })
            
            # Add to category sentiment
            category = product.get("category", "Uncategorized")
            if category not in category_sentiment:
                category_sentiment[category] = {
                    "positive": 0,
                    "neutral": 0,
                    "negative": 0,
                    "count": 0
                }
            
            category_sentiment[category]["positive"] += pos_score
            category_sentiment[category]["neutral"] += neut_score
            category_sentiment[category]["negative"] += neg_score
            category_sentiment[category]["count"] += 1
        
        # Calculate average sentiment per category
        categories_data = []
        for category, data in category_sentiment.items():
            if data["count"] > 0:
                categories_data.append({
                    "category": category,
                    "positive": data["positive"] / data["count"],
                    "neutral": data["neutral"] / data["count"],
                    "negative": data["negative"] / data["count"]
                })
        
        # Normalize overall sentiment to percentages
        total_sentiment = sum(overall_sentiment.values())
        if total_sentiment > 0:
            overall_sentiment = {
                k: round(v * 100 / total_sentiment, 1) 
                for k, v in overall_sentiment.items()
            }
        
        # Get trend data - create a time series of sentiment scores
        trend_data = []
        if time_period != 'all' and days <= 90:  # Only for reasonable time periods
            for day in range(days):
                date = datetime.now() - timedelta(days=days-day-1)
                date_str = date.strftime('%Y-%m-%d')
                
                # Calculate sentiment for this day
                day_query = {
                    "created_at": {
                        "$gte": datetime.combine(date, datetime.min.time()),
                        "$lt": datetime.combine(date + timedelta(days=1), datetime.min.time())
                    }
                }
                
                day_reviews = list(db.reviews.find(day_query))
                day_sentiment = {"positive": 0, "neutral": 0, "negative": 0, "total": 0}
                
                for review in day_reviews:
                    sentiment_class = review.get("sentiment_class", "neutral")
                    day_sentiment[sentiment_class] += 1
                    day_sentiment["total"] += 1
                
                # Normalize to percentages
                if day_sentiment["total"] > 0:
                    trend_data.append({
                        "date": date_str,
                        "positive": round(day_sentiment["positive"] * 100 / day_sentiment["total"], 1),
                        "neutral": round(day_sentiment["neutral"] * 100 / day_sentiment["total"], 1),
                        "negative": round(day_sentiment["negative"] * 100 / day_sentiment["total"], 1)
                    })
                else:
                    trend_data.append({
                        "date": date_str,
                        "positive": 0,
                        "neutral": 0,
                        "negative": 0
                    })
        
        # Get keyword data
        positive_keywords = {}
        negative_keywords = {}
        
        # Find all sentiment keywords in reviews
        reviews = list(db.reviews.find({}, {"sentiment_keywords": 1, "sentiment_class": 1}))
        for review in reviews:
            keywords = review.get("sentiment_keywords")
            sentiment = review.get("sentiment_class")
            
            # Skip if no keywords or sentiment
            if not keywords or not sentiment:
                continue
            
            # Convert from JSON string if needed
            if isinstance(keywords, str):
                try:
                    keywords = json.loads(keywords)
                except:
                    keywords = []
            
            # Add keywords to appropriate list
            keywords_dict = positive_keywords if sentiment == "positive" else negative_keywords
            for keyword in keywords:
                if keyword in keywords_dict:
                    keywords_dict[keyword] += 1
                else:
                    keywords_dict[keyword] = 1
        
        # Sort and limit keywords
        top_positive = sorted(positive_keywords.items(), key=lambda x: x[1], reverse=True)[:50]
        top_negative = sorted(negative_keywords.items(), key=lambda x: x[1], reverse=True)[:50]
        
        # Return all data
        return jsonify({
            "overall_sentiment": overall_sentiment,
            "trend_data": trend_data,
            "categories": categories_data,
            "products": product_data,
            "positive_keywords": [{"text": k, "weight": v} for k, v in top_positive],
            "negative_keywords": [{"text": k, "weight": v} for k, v in top_negative]
        })
        
    except Exception as e:
        logger.error(f"Error getting sentiment report data: {str(e)}")
        return jsonify({"error": f"Failed to get sentiment report data: {str(e)}"}), 500

# Hype vs. Reality analysis for admin
@admin_bp.route('/reports/hype-reality')
@login_required
@admin_required
def hype_reality_reports():
    """Hype vs. Reality analysis for admin"""
    return render_template('admin/reports/hype_reality.html')

# Product performance reports for admin
@admin_bp.route('/reports/products')
@login_required
@admin_required
def product_reports():
    """Product performance reports for admin"""
    return render_template('admin/reports/products.html')

# Settings page for admin
@admin_bp.route('/settings')
@login_required
@admin_required
def admin_settings():
    """Admin settings page"""
    return render_template('admin/settings.html')

# Add is_admin field to user model in the database
def add_admin_field_to_users():
    """Add is_admin field to users who don't have it"""
    try:
        mongo_client, db = get_mongo_client()
        if db is None:
            logger.error("Failed to connect to MongoDB")
            return False
        
        # Check if any users exist
        result = db.users.update_many(
            {"is_admin": {"$exists": False}},
            {"$set": {"is_admin": False}}
        )
        
        logger.info(f"Added is_admin field to {result.modified_count} users")
        
        # Make the first user an admin if no admins exist
        admin_count = db.users.count_documents({"is_admin": True})
        if admin_count == 0:
            first_user = db.users.find_one({})
            if first_user:
                db.users.update_one(
                    {"_id": first_user.get("_id")},
                    {"$set": {"is_admin": True}}
                )
                logger.info(f"Made user {first_user.get('username')} an admin")
        
        return True
    
    except Exception as e:
        logger.error(f"Error adding admin field to users: {str(e)}")
        return False