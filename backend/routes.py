"""
Backend routes for the Sentiment E-commerce API.

This module contains API routes for handling backend operations.
"""

from flask import Blueprint, jsonify, request, session
from flask_cors import CORS
from flask_login import login_user, logout_user, login_required, current_user
import logging
import os

from backend.sentiment_analyzer import analyze_sentiment, classify_sentiment, get_sentiment_keywords, analyze_hype_vs_reality
from backend.product_data import get_products, get_product_by_id
from backend.recommendations import get_recommendations_for_product, get_top_rated_products
from mongo_config import get_db
from models_mongo import User

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create blueprint
bp = Blueprint('backend', __name__, url_prefix='/api')

@bp.route('/')
def home():
    return jsonify({"message": "Sentiment Analysis E-Commerce API"})

@bp.route('/auth/register', methods=['POST'])
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
        
        # Add to database
        user.save()
        
        # Log in the new user
        login_user(user)
        
        return jsonify({
            "message": "User registered successfully",
            "user": {
                "id": user.id(),
                "username": user.username,
                "email": user.email
            }
        }), 201
    except Exception as e:
        logger.error(f"Error registering user: {str(e)}")
        return jsonify({"error": "Failed to register user"}), 500

@bp.route('/auth/login', methods=['POST'])
def login():
    """Log in a user"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        # Check required fields
        if 'username' not in data or 'password' not in data:
            return jsonify({"error": "Missing username or password"}), 400
            
        # Find user by username
        user = User.get_by_username(data['username'])
        if not user or not user.check_password(data['password']):
            return jsonify({"error": "Invalid username or password"}), 401
            
        # Log in the user
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
        return jsonify({"error": "Failed to log in"}), 500

@bp.route('/auth/logout', methods=['POST'])
def logout():
    """Log out the current user"""
    try:
        if current_user.is_authenticated:
            logout_user()
            return jsonify({"message": "Logged out successfully"})
        else:
            return jsonify({"message": "No user to log out"}), 200
    except Exception as e:
        logger.error(f"Error logging out: {str(e)}")
        return jsonify({"error": "Failed to log out"}), 500

@bp.route('/auth/user', methods=['GET'])
def get_user():
    """Get the current user info"""
    if current_user.is_authenticated:
        return jsonify({
            "user": {
                "id": current_user.id(),
                "username": current_user.username,
                "email": current_user.email
            }
        })
    else:
        return jsonify({"error": "Not authenticated"}), 401

@bp.route('/products', methods=['GET'])
def api_get_products():
    """
    Get all products with sentiment analysis
    """
    try:
        products = get_products()
        return jsonify(products)
    except Exception as e:
        logger.error(f"Error fetching products: {str(e)}")
        return jsonify({"error": "Failed to fetch products"}), 500

@bp.route('/products/<product_id>', methods=['GET'])
def api_get_product(product_id):
    """
    Get product details with sentiment analysis
    """
    try:
        product = get_product_by_id(product_id)
        if not product:
            return jsonify({"error": "Product not found"}), 404
        return jsonify(product)
    except Exception as e:
        logger.error(f"Error fetching product {product_id}: {str(e)}")
        return jsonify({"error": f"Failed to fetch product {product_id}"}), 500

@bp.route('/analyze', methods=['POST'])
def api_analyze_sentiment():
    """
    Analyze sentiment of provided text
    """
    try:
        data = request.get_json()
        if not data or "text" not in data:
            return jsonify({"error": "No text provided"}), 400
        
        text = data["text"]
        sentiment = analyze_sentiment(text)
        sentiment_class = classify_sentiment(sentiment)
        
        return jsonify({
            "text": text,
            "sentiment_score": sentiment,
            "sentiment_class": sentiment_class
        })
    except Exception as e:
        logger.error(f"Error analyzing sentiment: {str(e)}")
        return jsonify({"error": "Failed to analyze sentiment"}), 500

@bp.route('/products/<product_id>/recommendations', methods=['GET'])
def api_get_recommendations(product_id):
    """
    Get product recommendations based on sentiment analysis
    """
    try:
        # Get the limit parameter from query string (default to 3)
        limit = request.args.get('limit', default=3, type=int)
        
        # Get recommended products
        recommended_products = get_recommendations_for_product(product_id, limit=limit)
        
        # Return as JSON
        result = []
        for product in recommended_products:
            # Convert product model to dict
            product_dict = {
                "id": product.id(),
                "name": product.name,
                "category": product.category,
                "price": product.price,
                "description": product.description,
                "image_url": product.image_url,
                "sentiment_scores": {
                    "positive": product.positive_score,
                    "neutral": product.neutral_score,
                    "negative": product.negative_score
                }
            }
            result.append(product_dict)
            
        return jsonify({
            "product_id": product_id,
            "recommendations": result
        })
    except Exception as e:
        logger.error(f"Error getting recommendations for product {product_id}: {str(e)}")
        return jsonify({"error": f"Failed to get recommendations for product {product_id}"}), 500

@bp.route('/recommendations/top-rated', methods=['GET'])
def api_get_top_rated():
    """
    Get top rated products based on sentiment score
    """
    try:
        # Get the category and limit parameters from query string
        category = request.args.get('category', default=None, type=str)
        limit = request.args.get('limit', default=5, type=int)
        
        # Get top rated products
        top_products = get_top_rated_products(category=category, limit=limit)
        
        # Return as JSON
        result = []
        for product in top_products:
            # Convert product model to dict
            product_dict = {
                "id": product.id(),
                "name": product.name,
                "category": product.category,
                "price": product.price,
                "description": product.description,
                "image_url": product.image_url,
                "sentiment_scores": {
                    "positive": product.positive_score,
                    "neutral": product.neutral_score,
                    "negative": product.negative_score
                }
            }
            result.append(product_dict)
            
        return jsonify({
            "category": category,
            "top_rated": result
        })
    except Exception as e:
        logger.error(f"Error getting top rated products: {str(e)}")
        return jsonify({"error": "Failed to get top rated products"}), 500

# Apply CORS to blueprint
CORS(bp, supports_credentials=True)