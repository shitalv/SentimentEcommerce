"""
Check Sentiment Scores

This script checks the sentiment scores for products and reviews in the MongoDB database.
"""

import pymongo
import json
from bson import ObjectId

# MongoDB connection string - hardcode the verified working connection string
MONGO_URI = "mongodb+srv://testdev01:testdev01@cluster0.kx3tti3.mongodb.net/sentiment_ecommerce?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME = "sentiment_ecommerce"

# Helper function to convert ObjectId to string
def json_friendly(obj):
    if isinstance(obj, ObjectId):
        return str(obj)
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

def check_sentiment_scores():
    """Check sentiment scores for products and reviews in the database"""
    try:
        # Connect to MongoDB
        client = pymongo.MongoClient(MONGO_URI)
        db = client[DB_NAME]
        
        # Check product sentiment scores
        print("\n--- PRODUCT SENTIMENT SCORES ---")
        products = list(db.products.find().limit(5))
        for product in products:
            product_id = product.get('_id')
            name = product.get('name', 'Unknown')
            positive = product.get('positive_score', 0)
            neutral = product.get('neutral_score', 0)
            negative = product.get('negative_score', 0)
            
            print(f"Product: {name}")
            print(f"ID: {product_id}")
            print(f"Positive Score: {positive}")
            print(f"Neutral Score: {neutral}")
            print(f"Negative Score: {negative}")
            print("------------------------------")
        
        # Check review sentiment scores
        print("\n--- REVIEW SENTIMENT SCORES ---")
        reviews = list(db.reviews.find().limit(5))
        for review in reviews:
            product_id = review.get('product_id', 'Unknown')
            text = review.get('text', 'No text')[:100] + "..." if review.get('text') else 'No text'
            sentiment_score = review.get('sentiment_score', 'None')
            sentiment_class = review.get('sentiment_class', 'None')
            
            print(f"Product ID: {product_id}")
            print(f"Review: {text}")
            print(f"Sentiment Score: {sentiment_score}")
            print(f"Sentiment Class: {sentiment_class}")
            print("------------------------------")
        
        # Count products with no sentiment scores
        zero_sentiment_count = db.products.count_documents({
            "$or": [
                {"positive_score": {"$exists": False}},
                {"neutral_score": {"$exists": False}},
                {"negative_score": {"$exists": False}},
                {"positive_score": 0, "neutral_score": 0, "negative_score": 0}
            ]
        })
        
        print(f"\nProducts with missing or zero sentiment scores: {zero_sentiment_count}")
        
        # Get examples of products with zero sentiment
        print("\n--- PRODUCTS WITH ZERO SENTIMENT ---")
        zero_sentiment_products = list(db.products.find({
            "$or": [
                {"positive_score": {"$exists": False}},
                {"neutral_score": {"$exists": False}},
                {"negative_score": {"$exists": False}},
                {"positive_score": 0, "neutral_score": 0, "negative_score": 0}
            ]
        }).limit(3))
        
        for product in zero_sentiment_products:
            product_id = product.get('_id')
            name = product.get('name', 'Unknown')
            
            print(f"Product: {name}")
            print(f"ID: {product_id}")
            
            # Check if this product has any reviews
            review_count = db.reviews.count_documents({"product_id": str(product_id)})
            print(f"Review Count: {review_count}")
            
            if review_count > 0:
                # Get some sample reviews for this product
                product_reviews = list(db.reviews.find({"product_id": str(product_id)}).limit(2))
                for i, review in enumerate(product_reviews):
                    print(f"  Review {i+1}: {review.get('text', 'No text')[:100]}...")
                    print(f"  Sentiment: {review.get('sentiment_score', 'None')}")
            print("------------------------------")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    check_sentiment_scores()