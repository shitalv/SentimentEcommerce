"""
Create Diverse Products

This script creates a diverse set of product examples with reviews for demonstration.
"""

import logging
import json
import random
from datetime import datetime, timedelta
from mongo_config import get_mongo_client
from backend.sentiment_analyzer import analyze_sentiment, classify_sentiment, get_sentiment_keywords

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('create_diverse_products')

# Sample product data with reviews
SAMPLE_PRODUCTS = [
    {
        "name": "Echo Dot (4th Gen) Smart Speaker",
        "asin": "B07XJ8C8F5",
        "category": "Electronics",
        "price": 49.99,
        "image_url": "https://m.media-amazon.com/images/I/61MbLLagiVL._AC_SL1000_.jpg",
        "description": "Smart speaker with Alexa built-in. Perfect for any room.",
        "reviews": [
            {
                "title": "Great smart speaker!",
                "text": "I love this Echo Dot! The sound quality is excellent for such a compact device. Alexa responds quickly to commands and the smart home integration works perfectly. Highly recommended.",
                "rating": 5.0,
                "author": "TechFan2023"
            },
            {
                "title": "Good but could be better",
                "text": "The sound is decent for a small speaker. I like the Alexa features, but sometimes it doesn't respond to my commands correctly. Overall a good purchase though.",
                "rating": 4.0,
                "author": "SmartHomeBuilder"
            },
            {
                "title": "Decent device, poor privacy",
                "text": "Works as advertised but I'm concerned about privacy issues. I feel like Amazon is always listening. The speaker quality is just okay.",
                "rating": 3.0,
                "author": "PrivacyFirst"
            }
        ]
    },
    {
        "name": "Amazon Fire HD 10 Tablet",
        "asin": "B08BX7FV5L",
        "category": "Electronics",
        "price": 149.99,
        "image_url": "https://m.media-amazon.com/images/I/61uE03cRsyL._AC_SL1000_.jpg",
        "description": "10.1-inch HD display, 32 GB, latest model (2021 release), designed for entertainment",
        "reviews": [
            {
                "title": "Perfect for media consumption",
                "text": "Great tablet for the price! The screen is bright and clear, and it's perfect for watching Netflix and reading books. Battery life is excellent too. Not as fast as an iPad but for the price it's a great value.",
                "rating": 4.5,
                "author": "TabletEnthusiast"
            },
            {
                "title": "Good but sluggish sometimes",
                "text": "It's a decent tablet for basic tasks. Good screen and battery life. However, it can be a bit sluggish when switching between apps or with more intensive tasks. For the price though, it's quite good.",
                "rating": 3.5,
                "author": "MediaConsumer"
            },
            {
                "title": "Disappointed with performance",
                "text": "The tablet is very slow and lags a lot. Even simple tasks like web browsing can be frustrating. The screen is good but the performance issues make this hard to recommend.",
                "rating": 2.0,
                "author": "SpeedSeeker"
            }
        ]
    },
    {
        "name": "Amazon Basics Microfiber Cleaning Cloth",
        "asin": "B07PNLX7L1",
        "category": "Home & Kitchen",
        "price": 14.99,
        "image_url": "https://m.media-amazon.com/images/I/91Iq7AcxDSL._AC_SL1500_.jpg",
        "description": "Pack of 24 cloths for cleaning and dusting. Super absorbent and lint-free.",
        "reviews": [
            {
                "title": "Great quality cleaning cloths",
                "text": "These microfiber cloths are excellent quality. They clean well without leaving streaks or lint behind. Very absorbent and durable - I've washed them several times and they hold up well. Highly recommended for cleaning around the house.",
                "rating": 5.0,
                "author": "CleanFreak"
            },
            {
                "title": "Good but not super durable",
                "text": "These cloths work well for general cleaning. They pick up dust effectively and don't leave lint behind. However, after washing a few times, they start to fray around the edges. Still a decent value for the price.",
                "rating": 3.5,
                "author": "PracticalCleaner"
            }
        ]
    },
    {
        "name": "Amazon Essentials Men's Slim-Fit T-Shirt",
        "asin": "B09BTNPFG6",
        "category": "Clothing",
        "price": 18.50,
        "image_url": "https://m.media-amazon.com/images/I/71VB0lCIhBL._AC_UX679_.jpg",
        "description": "Comfortable cotton t-shirt with a modern slim fit. Pack of 2.",
        "reviews": [
            {
                "title": "Great fit and quality",
                "text": "These t-shirts are excellent quality for the price! The fit is perfect - slim but not too tight. The fabric is soft and comfortable, and they've held up well after several washes without shrinking or fading. Will definitely buy more.",
                "rating": 5.0,
                "author": "FashionGuy"
            },
            {
                "title": "Decent shirts for the price",
                "text": "The shirts are okay, about what you'd expect for the price. The fit is good but the fabric could be a bit thicker. They've held up fine in the wash so far. Worth it for basic everyday shirts.",
                "rating": 3.5,
                "author": "CasualDresser"
            },
            {
                "title": "Disappointing quality",
                "text": "I expected better from Amazon Essentials. The shirts shrunk significantly after the first wash, even though I followed the care instructions. The seams are also coming apart already. Would not recommend or purchase again.",
                "rating": 1.5,
                "author": "QualitySeeker"
            }
        ]
    },
    {
        "name": "The Psychology of Money by Morgan Housel",
        "asin": "B08FHZ5L47",
        "category": "Books",
        "price": 15.99,
        "image_url": "https://m.media-amazon.com/images/I/71vKyimfuJL._AC_UY436_QL65_.jpg",
        "description": "Timeless lessons on wealth, greed, and happiness. A popular finance book with practical wisdom.",
        "reviews": [
            {
                "title": "Life-changing financial wisdom",
                "text": "This is the best financial book I've ever read. It's not about technical investing strategies but about the psychology behind our money decisions. The short chapters make it easy to digest, and the stories are memorable. It completely changed how I think about money and success. Highly recommend to everyone.",
                "rating": 5.0,
                "author": "FinancialFreedom"
            },
            {
                "title": "Good insights but somewhat repetitive",
                "text": "This book has some excellent insights about how we think about money. The anecdotes and historical examples are interesting and enlightening. However, it does get repetitive at times and could have been more concise. Still, a good read for anyone interested in personal finance.",
                "rating": 4.0,
                "author": "BookwormInvestor"
            },
            {
                "title": "Overrated financial philosophy",
                "text": "I found this book to be quite overrated. Most of the concepts are common sense dressed up with anecdotes. There's not much actionable advice, and many of the stories feel cherry-picked to support the author's points. There are better financial books out there.",
                "rating": 2.5,
                "author": "CriticalThinker"
            }
        ]
    }
]

def create_diverse_products():
    """Create a diverse set of products with reviews for demonstration purposes"""
    # Get MongoDB client
    mongo_client, db = get_mongo_client()
    if db is None:
        logger.error("Failed to connect to MongoDB")
        return False
    
    try:
        products_created = 0
        
        for product_data in SAMPLE_PRODUCTS:
            # Check if product already exists by ASIN
            existing_product = db.products.find_one({"asin": product_data["asin"]})
            
            if existing_product:
                logger.info(f"Product already exists: {product_data['name']}")
                product_id = existing_product["_id"]
            else:
                # Create product data with sentiment score placeholders
                product_doc = {
                    "asin": product_data["asin"],
                    "name": product_data["name"],
                    "description": product_data.get("description", ""),
                    "price": product_data["price"],
                    "category": product_data["category"],
                    "image_url": product_data["image_url"],
                    "positive_score": 0.0,
                    "neutral_score": 0.0,
                    "negative_score": 0.0,
                    "sentiment_score": 0.5,  # Default neutral
                    "created_at": datetime.now(),
                    "updated_at": datetime.now()
                }
                
                # Insert product
                product_id = db.products.insert_one(product_doc).inserted_id
                logger.info(f"Created product: {product_data['name']}")
                products_created += 1
            
            # Process reviews for this product
            positive_count = 0
            neutral_count = 0
            negative_count = 0
            total_sentiment = 0
            
            for review_data in product_data["reviews"]:
                # Check if review already exists to avoid duplicates
                existing_review = db.reviews.find_one({
                    "product_id": str(product_id),
                    "text": review_data["text"]
                })
                
                if not existing_review:
                    # Add sentiment analysis
                    sentiment_score = analyze_sentiment(review_data["text"])
                    sentiment_class = classify_sentiment(sentiment_score)
                    keywords = get_sentiment_keywords(review_data["text"], sentiment_score)
                    
                    # Track sentiment counts
                    if sentiment_class == "positive":
                        positive_count += 1
                    elif sentiment_class == "neutral":
                        neutral_count += 1
                    else:
                        negative_count += 1
                    
                    total_sentiment += sentiment_score
                    
                    # Create date within the last 30 days
                    days_ago = random.randint(1, 30)
                    review_date = datetime.now() - timedelta(days=days_ago)
                    
                    # Create review
                    review_doc = {
                        "product_id": str(product_id),
                        "author": review_data["author"],
                        "title": review_data["title"],
                        "text": review_data["text"],
                        "rating": review_data["rating"],
                        "date": review_date,
                        "sentiment_score": sentiment_score,
                        "sentiment_class": sentiment_class,
                        "sentiment_keywords": json.dumps(keywords),
                        "created_at": datetime.now()
                    }
                    
                    # Insert review
                    db.reviews.insert_one(review_doc)
                    logger.info(f"Added review for product: {product_data['name']}")
            
            # Update product with sentiment scores
            review_count = len(product_data["reviews"])
            if review_count > 0:
                db.products.update_one(
                    {"_id": product_id},
                    {"$set": {
                        "positive_score": positive_count / review_count,
                        "neutral_score": neutral_count / review_count,
                        "negative_score": negative_count / review_count,
                        "sentiment_score": total_sentiment / review_count,
                        "updated_at": datetime.now()
                    }}
                )
                logger.info(f"Updated sentiment scores for product: {product_data['name']}")
        
        logger.info(f"Created {products_created} new diverse products")
        return True
    
    except Exception as e:
        logger.error(f"Error creating diverse products: {str(e)}")
        return False

if __name__ == "__main__":
    if create_diverse_products():
        logger.info("Diverse products created successfully")
    else:
        logger.error("Failed to create diverse products")