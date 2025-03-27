from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
import os
from sentiment_analyzer import analyze_sentiment, classify_sentiment, get_sentiment_keywords, analyze_hype_vs_reality
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
            
            # Extract keywords that contribute to the sentiment (Amazon review analysis)
            review["keywords"] = get_sentiment_keywords(review["text"], sentiment_class)
        
        # Calculate overall sentiment score (weighted average based on Amazon review methodology)
        # Process reviews in chronological order (newer reviews have more weight)
        sorted_reviews = sorted(product["reviews"], key=lambda x: x.get("date", ""), reverse=True)
        
        # Amazon style weighting - more weight to recent and longer reviews
        if sorted_reviews:
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
            weighted_score = sum(w * s for w, s in zip(review_weights, review_scores)) / sum(review_weights)
            product["sentiment_score"] = weighted_score
        else:
            product["sentiment_score"] = 0.5  # Neutral if no reviews
            
        # Add keyword extraction for key aspects of sentiment
        product["key_aspects"] = {
            "positive": [],
            "negative": []
        }
        
        # Extract key aspects from positive and negative reviews
        for review in product["reviews"]:
            if review["sentiment"] >= 0.7:  # Strongly positive
                product["key_aspects"]["positive"].extend(review.get("keywords", []))
            elif review["sentiment"] <= 0.3:  # Strongly negative
                product["key_aspects"]["negative"].extend(review.get("keywords", []))
        
        # Add sentiment counts to the product
        product["sentiment_counts"] = sentiment_counts
        
        # Add "Hype vs Reality" analysis by comparing product description with reviews
        product["hype_vs_reality"] = analyze_hype_vs_reality(product.get("description", ""), product["reviews"])
        
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
