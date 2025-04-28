"""
Backend routes for the Sentiment E-commerce API.

This module contains API route functions for the app_factory to import.
"""

from flask import jsonify, request, session
from flask_cors import CORS
from flask_login import login_user, logout_user, login_required, current_user
import logging
import os

from backend.sentiment_analyzer import analyze_sentiment, classify_sentiment, get_sentiment_keywords, analyze_hype_vs_reality
from backend.product_data import get_products, get_product_by_id
from backend.recommendations import get_recommendations_for_product, get_top_rated_products
from models_mongo import User

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def home():
    """Home endpoint"""
    return jsonify({"message": "Sentiment Analysis E-Commerce API"})

def register():
    """Register a new user"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        # Check required fields
        required_fields = ['username', 'email', 'password']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400
            
        # Check if username or email already exists
        if User.get_by_username(data['username']):
            return jsonify({"error": "Username already exists"}), 400
            
        if User.get_by_email(data['email']):
            return jsonify({"error": "Email already exists"}), 400
            
        # Create new user
        user = User(username=data['username'], email=data['email'])
        user.set_password(data['password'])
        user.save()
        
        return jsonify({
            "message": "User registered successfully",
            "user": {
                "id": user.get_id(),
                "username": user.username,
                "email": user.email
            }
        }), 201
        
    except Exception as e:
        logger.error(f"Error registering user: {str(e)}")
        return jsonify({"error": "An error occurred while registering"}), 500

def login():
    """Log in a user"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        # Check required fields
        if not all(field in data for field in ['username', 'password']):
            return jsonify({"error": "Missing username or password"}), 400
            
        # Get user by username
        user = User.get_by_username(data['username'])
        if not user:
            return jsonify({"error": "Invalid username or password"}), 401
            
        # Check password
        if not user.check_password(data['password']):
            return jsonify({"error": "Invalid username or password"}), 401
            
        # Log in user using Flask-Login
        login_user(user)
        
        return jsonify({
            "message": "Login successful",
            "user": {
                "id": user.id(),
                "username": user.username,
                "email": user.email
            }
        })
        
    except Exception as e:
        logger.error(f"Error logging in: {str(e)}")
        return jsonify({"error": "An error occurred while logging in"}), 500

@login_required
def logout():
    """Log out the current user"""
    try:
        logout_user()
        return jsonify({"message": "Logged out successfully"})
    except Exception as e:
        logger.error(f"Error logging out: {str(e)}")
        return jsonify({"error": "An error occurred while logging out"}), 500

def get_user():
    """Get the current user info"""
    try:
        if current_user.is_authenticated:
            return jsonify({
                "user": {
                    "id": current_user.id(),
                    "username": current_user.username,
                    "email": current_user.email
                }
            })
        return jsonify({"user": None})
    except Exception as e:
        logger.error(f"Error getting user: {str(e)}")
        return jsonify({"error": "An error occurred while getting user info"}), 500

def api_get_products():
    """
    Get all products with sentiment analysis
    """
    try:
        category = request.args.get('category')
        query = request.args.get('query')
        min_sentiment = request.args.get('min_sentiment')
        max_sentiment = request.args.get('max_sentiment')
        
        # Convert sentiment scores to float if provided
        if min_sentiment:
            min_sentiment = float(min_sentiment)
        if max_sentiment:
            max_sentiment = float(max_sentiment)
            
        # Get products with filters
        products = get_products(query, category, min_sentiment, max_sentiment)
        
        return jsonify({"products": products})
    except Exception as e:
        logger.error(f"Error getting products: {str(e)}")
        return jsonify({"error": "An error occurred while fetching products"}), 500

def api_get_product(product_id):
    """
    Get product details with sentiment analysis
    """
    try:
        logger.info(f"API get_product called with product_id: {product_id}")
        
        # Try to get the product directly first
        try:
            product = get_product_by_id(product_id)
        except Exception as e:
            logger.info(f"Error getting product by ID: {str(e)}")
            product = None
        
        # If exact product ID not found, try checking if it's a partial ID
        if not product and len(product_id) < 24:
            logger.info(f"Handling partial product ID: {product_id}")
            
            try:
                # Get all products and find a match by ID prefix
                from backend.product_data import get_products
                all_products = get_products()
                
                matching_product = None
                for p in all_products:
                    # Compare string representation of IDs
                    if str(p.get('id', '')).startswith(product_id):
                        logger.info(f"Found product with matching ID start: {p.get('id', 'unknown')}")
                        matching_product = p
                        break
                
                if matching_product:
                    product = matching_product
            except Exception as partial_id_error:
                logger.error(f"Error handling partial ID: {str(partial_id_error)}")
        
        if not product:
            logger.warning(f"Product not found for ID: {product_id}")
            return jsonify({"error": "Product not found"}), 404
        
        logger.info(f"Returning product: {product.get('name', 'Unknown')} for ID: {product_id}")
        return jsonify({"product": product})
    except Exception as e:
        logger.error(f"Error getting product {product_id}: {str(e)}")
        return jsonify({"error": "An error occurred while fetching product"}), 500

def api_analyze_sentiment():
    """
    Analyze sentiment of provided text
    """
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({"error": "No text provided"}), 400
            
        text = data['text']
        sentiment_score = analyze_sentiment(text)
        sentiment_class = classify_sentiment(sentiment_score)
        keywords = get_sentiment_keywords(text, sentiment_class)
        
        return jsonify({
            "text": text,
            "sentiment": {
                "score": sentiment_score,
                "class": sentiment_class,
                "keywords": keywords
            }
        })
    except Exception as e:
        logger.error(f"Error analyzing sentiment: {str(e)}")
        return jsonify({"error": "An error occurred while analyzing sentiment"}), 500

def api_get_recommendations(product_id):
    """
    Get product recommendations based on sentiment analysis
    """
    try:
        limit = request.args.get('limit', default=3, type=int)
        recommendations = get_recommendations_for_product(product_id, limit)
        
        return jsonify({"recommendations": recommendations})
    except Exception as e:
        logger.error(f"Error getting recommendations for product {product_id}: {str(e)}")
        return jsonify({"error": "An error occurred while fetching recommendations"}), 500

def api_get_top_rated():
    """
    Get top rated products based on sentiment score
    """
    try:
        category = request.args.get('category')
        limit = request.args.get('limit', default=5, type=int)
        
        top_products = get_top_rated_products(category, limit)
        
        return jsonify({"products": top_products})
    except Exception as e:
        logger.error(f"Error getting top rated products: {str(e)}")
        return jsonify({"error": "An error occurred while fetching top products"}), 500