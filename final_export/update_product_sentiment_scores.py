"""
Update Product Sentiment Scores

This script updates the sentiment scores for products in the MongoDB database
by aggregating the sentiment scores from their associated reviews.
"""

import pymongo
from bson import ObjectId

# MongoDB connection string - hardcode the verified working connection string
MONGO_URI = "mongodb+srv://testdev01:testdev01@cluster0.kx3tti3.mongodb.net/sentiment_ecommerce?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME = "sentiment_ecommerce"

def update_product_sentiment_scores():
    """Update sentiment scores for products based on their reviews"""
    try:
        # Connect to MongoDB
        client = pymongo.MongoClient(MONGO_URI)
        db = client[DB_NAME]
        
        # Get all products
        products = list(db.products.find())
        update_count = 0
        
        print(f"Found {len(products)} products to check")
        
        for product in products:
            product_id = product.get('_id')
            name = product.get('name', 'Unknown')
            
            # Get all reviews for this product
            product_reviews = list(db.reviews.find({"product_id": str(product_id)}))
            
            if product_reviews:
                print(f"Processing {name} ({product_id}) with {len(product_reviews)} reviews")
                
                # Calculate sentiment scores
                positive_count = 0
                neutral_count = 0
                negative_count = 0
                
                for review in product_reviews:
                    sentiment_score = review.get('sentiment_score', 0)
                    sentiment_class = review.get('sentiment_class', '')
                    
                    # Prioritize the explicit classification over the score
                    if sentiment_class == 'positive':
                        positive_count += 1
                    elif sentiment_class == 'negative':
                        negative_count += 1
                    elif sentiment_class == 'neutral':
                        neutral_count += 1
                    # Fall back to score-based classification if no explicit class
                    elif sentiment_score >= 0.05:
                        positive_count += 1
                    elif sentiment_score <= -0.05:
                        negative_count += 1
                    else:
                        neutral_count += 1
                
                total_reviews = len(product_reviews)
                positive_score = positive_count / total_reviews if total_reviews > 0 else 0
                neutral_score = neutral_count / total_reviews if total_reviews > 0 else 0
                negative_score = negative_count / total_reviews if total_reviews > 0 else 0
                
                # Alternative calculation using actual sentiment scores
                alt_positive_score = sum(max(0, review.get('sentiment_score', 0)) for review in product_reviews) / total_reviews if total_reviews > 0 else 0
                
                # Update product sentiment scores
                db.products.update_one(
                    {"_id": product_id},
                    {"$set": {
                        "positive_score": positive_score,
                        "neutral_score": neutral_score,
                        "negative_score": negative_score,
                        "review_count": total_reviews
                    }}
                )
                
                print(f"  Updated scores: pos={positive_score:.2f}, neu={neutral_score:.2f}, neg={negative_score:.2f}")
                update_count += 1
            else:
                print(f"Skipping {name} ({product_id}) - no reviews found")
        
        print(f"\nSuccessfully updated sentiment scores for {update_count} products")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    update_product_sentiment_scores()