from flask import Blueprint, jsonify, request, session
from flask_cors import CORS
from flask_login import login_user, logout_user, login_required, current_user
import logging
import os
from backend.sentiment_analyzer import analyze_sentiment, classify_sentiment, get_sentiment_keywords, analyze_hype_vs_reality
from backend.product_data import get_products, get_product_by_id

# Get the db from parent module
from app import db
from models import User

# Set up logging
logging.basicConfig(level=logging.DEBUG)

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
        if User.query.filter_by(username=data['username']).first():
            return jsonify({"error": "Username already exists"}), 400
            
        if User.query.filter_by(email=data['email']).first():
            return jsonify({"error": "Email already exists"}), 400
            
        # Create new user
        user = User(username=data['username'], email=data['email'])
        user.set_password(data['password'])
        
        # Add to database
        db.session.add(user)
        db.session.commit()
        
        # Log in the new user
        login_user(user)
        
        return jsonify({
            "message": "User registered successfully",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email
            }
        }), 201
    except Exception as e:
        logging.error(f"Error registering user: {str(e)}")
        db.session.rollback()
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
        user = User.query.filter_by(username=data['username']).first()
        if not user or not user.check_password(data['password']):
            return jsonify({"error": "Invalid username or password"}), 401
            
        # Log in the user
        login_user(user)
        
        return jsonify({
            "message": "Login successful",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email
            }
        })
    except Exception as e:
        logging.error(f"Error logging in: {str(e)}")
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
        logging.error(f"Error logging out: {str(e)}")
        return jsonify({"error": "Failed to log out"}), 500

@bp.route('/auth/user', methods=['GET'])
def get_user():
    """Get the current user info"""
    if current_user.is_authenticated:
        return jsonify({
            "user": {
                "id": current_user.id,
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
        # Add sentiment score to each product
        for product in products:
            # Calculate sentiment for each review
            review_sentiments = []
            for review in product["reviews"]:
                sentiment_score = analyze_sentiment(review["text"])
                review_sentiments.append(sentiment_score)
                
            # Calculate overall sentiment score (weighted average based on Amazon review methodology)
            if review_sentiments:
                # Amazon style weighting - more weight to recent and longer reviews
                product["sentiment_score"] = sum(review_sentiments) / len(review_sentiments)
            else:
                product["sentiment_score"] = 0.5  # Neutral if no reviews
        
        return jsonify(products)
    except Exception as e:
        logging.error(f"Error fetching products: {str(e)}")
        return jsonify({"error": "Failed to fetch products"}), 500

@bp.route('/products/<int:product_id>', methods=['GET'])
def api_get_product(product_id):
    """
    Get product details with sentiment analysis
    """
    try:
        product = get_product_by_id(product_id)
        if not product:
            return jsonify({"error": "Product not found"}), 404
        
        # Check if we need to process reviews
        if "sentiment_counts" not in product and "reviews" in product and product["reviews"]:
            # Initialize sentiment counts
            sentiment_counts = {"positive": 0, "neutral": 0, "negative": 0}
            
            for review in product["reviews"]:
                # Skip processing if review already has sentiment
                if "sentiment" not in review:
                    # Analyze sentiment of the review
                    sentiment_score = analyze_sentiment(review["text"])
                    review["sentiment"] = sentiment_score
                    
                    # Classify sentiment for counting
                    sentiment_class = classify_sentiment(sentiment_score)
                    
                    # Extract keywords that contribute to the sentiment (if not already present)
                    if "keywords" not in review:
                        review["keywords"] = get_sentiment_keywords(review["text"], sentiment_class)
                else:
                    # Use existing sentiment class
                    sentiment_score = review["sentiment"]
                    sentiment_class = classify_sentiment(sentiment_score)
                
                # Count the sentiment classes
                sentiment_counts[sentiment_class] += 1
            
            # Add sentiment counts to the response if not already present
            if "sentiment_counts" not in product:
                product["sentiment_counts"] = sentiment_counts
        
        # Initialize sentiment_counts if not done already
        if "sentiment_counts" not in product:
            product["sentiment_counts"] = {"positive": 0, "neutral": 0, "negative": 0}
            
            # If we have reviews, count sentiments
            if "reviews" in product and product["reviews"]:
                for review in product["reviews"]:
                    if "sentiment" in review:
                        sentiment_class = classify_sentiment(review["sentiment"])
                        product["sentiment_counts"][sentiment_class] += 1
        
        # Calculate overall sentiment score (weighted average based on Amazon review methodology)
        # Only do this if we need to and if there are reviews to process
        if "sentiment_score" not in product and "reviews" in product and product["reviews"]:
            # Only consider reviews that have sentiment scores
            valid_reviews = [r for r in product["reviews"] if "sentiment" in r]
            
            if valid_reviews:
                # Process reviews in chronological order (newer reviews have more weight)
                sorted_reviews = sorted(valid_reviews, key=lambda x: x.get("date", ""), reverse=True)
                
                # Apply weighted averaging giving more weight to recent reviews
                review_weights = []
                review_scores = []
                
                for i, review in enumerate(sorted_reviews):
                    # Weight based on recency (higher index = older review)
                    recency_weight = max(0.5, 1.0 - (i * 0.1))
                    
                    # Weight based on review length (longer reviews get more weight)
                    length_weight = min(1.5, max(0.5, len(review["text"]) / 100))
                    
                    total_weight = recency_weight * length_weight
                    review_weights.append(total_weight)
                    review_scores.append(review["sentiment"])
                
                # Calculate weighted average
                if review_weights and review_scores:
                    weighted_score = sum(w * s for w, s in zip(review_weights, review_scores)) / sum(review_weights)
                    product["sentiment_score"] = weighted_score
                else:
                    product["sentiment_score"] = 0.5  # Neutral if no valid reviews
            else:
                product["sentiment_score"] = 0.5  # Neutral if no valid reviews
        elif "sentiment_score" not in product:
            product["sentiment_score"] = 0.5  # Neutral if no reviews or sentiment_score
            
        # Add keyword extraction for key aspects of sentiment
        product["key_aspects"] = {
            "positive": [],
            "negative": []
        }
        
        # Extract key aspects from positive and negative reviews
        if "reviews" in product:
            for review in product["reviews"]:
                if "sentiment" in review:
                    if review["sentiment"] >= 0.7:  # Strongly positive
                        product["key_aspects"]["positive"].extend(review.get("keywords", []))
                    elif review["sentiment"] <= 0.3:  # Strongly negative
                        product["key_aspects"]["negative"].extend(review.get("keywords", []))
        
        # Ensure sentiment counts is initialized
        if "sentiment_counts" not in product:
            product["sentiment_counts"] = {"positive": 0, "neutral": 0, "negative": 0}
        
        # Add "Hype vs Reality" analysis by comparing product description with reviews
        if "reviews" in product and product["reviews"]:
            review_texts = [r.get("text", "") for r in product["reviews"] if "text" in r]
            if review_texts and product.get("description"):
                try:
                    product["hype_vs_reality"] = analyze_hype_vs_reality(
                        product.get("description", ""), 
                        review_texts
                    )
                except Exception as hype_error:
                    logging.error(f"Error in hype vs reality analysis: {str(hype_error)}")
                    product["hype_vs_reality"] = {
                        "matching_claims": [],
                        "contradicting_claims": []
                    }
            else:
                product["hype_vs_reality"] = {
                    "matching_claims": [],
                    "contradicting_claims": []
                }
        else:
            product["hype_vs_reality"] = {
                "matching_claims": [],
                "contradicting_claims": []
            }
        
        return jsonify(product)
    except Exception as e:
        logging.error(f"Error fetching product {product_id}: {str(e)}")
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
        logging.error(f"Error analyzing sentiment: {str(e)}")
        return jsonify({"error": "Failed to analyze sentiment"}), 500

# Apply CORS to blueprint
CORS(bp, supports_credentials=True)

# This is only run when this file is executed directly (for development)
if __name__ == "__main__":
    from flask import Flask
    app = Flask(__name__)
    app.register_blueprint(bp)
    app.run(host="0.0.0.0", port=8000, debug=True)
