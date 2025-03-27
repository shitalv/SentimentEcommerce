from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
import os
from sentiment_analyzer import analyze_sentiment, classify_sentiment
from product_data import get_products, get_product_by_id

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Initialize Flask app if not imported
if not 'app' in globals():
    app = Flask(__name__)
    app.secret_key = os.environ.get("SESSION_SECRET", "default_secret_key")
    # Enable CORS
    CORS(app)

@app.route('/')
def home():
    return jsonify({"message": "Sentiment Analysis E-Commerce API"})

@app.route('/api/products', methods=['GET'])
def api_get_products():
    """
    Get all products with sentiment analysis
    """
    try:
        products = get_products()
        # Add sentiment score to each product
        for product in products:
            # Calculate overall sentiment score based on all reviews
            all_reviews_text = " ".join([review["text"] for review in product["reviews"]])
            product["sentiment_score"] = analyze_sentiment(all_reviews_text)
        
        return jsonify(products)
    except Exception as e:
        logging.error(f"Error fetching products: {str(e)}")
        return jsonify({"error": "Failed to fetch products"}), 500

@app.route('/api/products/<int:product_id>', methods=['GET'])
def api_get_product(product_id):
    """
    Get product details with sentiment analysis
    """
    try:
        product = get_product_by_id(product_id)
        if not product:
            return jsonify({"error": "Product not found"}), 404
        
        # Calculate sentiment for each review
        sentiment_counts = {"positive": 0, "neutral": 0, "negative": 0}
        
        for review in product["reviews"]:
            # Analyze sentiment of each review
            sentiment_score = analyze_sentiment(review["text"])
            review["sentiment"] = sentiment_score
            
            # Classify sentiment for counting
            sentiment_class = classify_sentiment(sentiment_score)
            sentiment_counts[sentiment_class] += 1
        
        # Calculate overall sentiment score based on all reviews
        all_reviews_text = " ".join([review["text"] for review in product["reviews"]])
        product["sentiment_score"] = analyze_sentiment(all_reviews_text)
        
        # Add sentiment counts to the product
        product["sentiment_counts"] = sentiment_counts
        
        return jsonify(product)
    except Exception as e:
        logging.error(f"Error fetching product {product_id}: {str(e)}")
        return jsonify({"error": f"Failed to fetch product {product_id}"}), 500

@app.route('/api/analyze', methods=['POST'])
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

if __name__ == "__main__":
    # This is run when this file is executed directly (for development)
    app.run(host="0.0.0.0", port=8000, debug=True)
