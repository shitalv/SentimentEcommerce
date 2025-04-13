import logging

# Sample product data with reviews for demonstration
# In a real application, this would come from a database
products = [
    {
        "id": 1,
        "name": "Wireless Bluetooth Headphones",
        "price": 79.99,
        "category": "Electronics",
        "description": "High-quality wireless headphones with noise cancellation technology, 20-hour battery life, and comfortable over-ear design.",
        "reviews": [
            {
                "author": "AudioFan",
                "date": "2023-05-15",
                "text": "These headphones are amazing! The sound quality is exceptional and the noise cancellation works perfectly. Battery life is as advertised. Worth every penny!"
            },
            {
                "author": "MusicLover",
                "date": "2023-04-22",
                "text": "Good headphones, but the ear cushions could be more comfortable for long listening sessions. Sound quality is excellent though."
            },
            {
                "author": "TechReviewer",
                "date": "2023-03-10",
                "text": "Battery doesn't last as long as advertised. Sound quality is decent but not as good as some competitors in the same price range."
            }
        ]
    },
    {
        "id": 2,
        "name": "Smart Fitness Tracker",
        "price": 49.99,
        "category": "Wearables",
        "description": "Track your health and fitness with this waterproof smart band featuring heart rate monitoring, sleep tracking, and 7-day battery life.",
        "reviews": [
            {
                "author": "FitnessEnthusiast",
                "date": "2023-06-02",
                "text": "Great fitness tracker for the price! Accurate heart rate monitoring and the app is easy to use. Battery lasts longer than expected."
            },
            {
                "author": "Runner123",
                "date": "2023-05-18",
                "text": "The sleep tracking feature is inaccurate. It often says I'm sleeping when I'm just watching TV. Heart rate seems accurate though."
            },
            {
                "author": "GymRat",
                "date": "2023-04-30",
                "text": "Does the job, but the band broke after just 2 months of use. The customer service was unhelpful when I tried to get a replacement."
            },
            {
                "author": "WellnessCoach",
                "date": "2023-04-15",
                "text": "I recommend this to all my clients. It's affordable and has all the basic features most people need for fitness tracking."
            }
        ]
    },
    {
        "id": 3,
        "name": "Ergonomic Office Chair",
        "price": 199.99,
        "category": "Furniture",
        "description": "Comfortable ergonomic chair with lumbar support, adjustable armrests, and breathable mesh back. Perfect for your home office.",
        "reviews": [
            {
                "author": "RemoteWorker",
                "date": "2023-06-10",
                "text": "After switching to this chair, my back pain has significantly decreased. Assembly was straightforward and the quality is excellent."
            },
            {
                "author": "OfficeManager",
                "date": "2023-05-25",
                "text": "Bought these chairs for our whole office. Everyone loves them and they look professional. Great value for money."
            },
            {
                "author": "BackPainSufferer",
                "date": "2023-05-02",
                "text": "Disappointed with this chair. The lumbar support is minimal and the seat cushion flattened within weeks. Not worth the price."
            }
        ]
    },
    {
        "id": 4,
        "name": "Ultra HD Smart TV - 55\"",
        "price": 499.99,
        "category": "Electronics",
        "description": "4K Ultra HD Smart TV with HDR, built-in streaming apps, voice control, and slim bezel design for an immersive viewing experience.",
        "reviews": [
            {
                "author": "MovieBuff",
                "date": "2023-06-15",
                "text": "Picture quality is outstanding! The smart features work smoothly and the setup was incredibly easy. Highly recommend for movie lovers."
            },
            {
                "author": "GamerDude",
                "date": "2023-05-30",
                "text": "Great for gaming! The refresh rate is good and there's minimal input lag. The only downside is the built-in speakers aren't very powerful."
            },
            {
                "author": "TechCritic",
                "date": "2023-05-12",
                "text": "The UI is sluggish and the OS needs frequent updates. Picture quality is good but the smart features are disappointing compared to competitors."
            },
            {
                "author": "FamilyGuy",
                "date": "2023-04-28",
                "text": "Perfect family TV. Easy to use for everyone from kids to grandparents. The value for money is excellent at this price point."
            }
        ]
    },
    {
        "id": 5,
        "name": "Professional Blender",
        "price": 89.99,
        "category": "Kitchen",
        "description": "High-performance blender with multiple speed settings, pulse function, and durable stainless steel blades. Perfect for smoothies, soups, and more.",
        "reviews": [
            {
                "author": "HomeChef",
                "date": "2023-06-20",
                "text": "This blender is a workhorse! It handles everything from frozen fruits to nuts with ease. Easy to clean and very durable."
            },
            {
                "author": "SmoothieKing",
                "date": "2023-06-05",
                "text": "Makes the smoothest smoothies I've ever had. No chunks or unblended bits. A bit loud but that's expected with such power."
            },
            {
                "author": "KitchenGadgetCollector",
                "date": "2023-05-19",
                "text": "The blender started leaking after just 3 weeks. When it worked, it was great, but the quality control seems poor."
            }
        ]
    },
    {
        "id": 6,
        "name": "Organic Cotton Bedding Set",
        "price": 129.99,
        "category": "Home",
        "description": "Luxury 100% organic cotton bedding set including duvet cover and pillowcases. Soft, breathable, and eco-friendly.",
        "reviews": [
            {
                "author": "EcoConsumer",
                "date": "2023-06-25",
                "text": "Love that these are organic and sustainable. They're so soft and comfortable, and they wash well without losing quality."
            },
            {
                "author": "LuxuryLover",
                "date": "2023-06-10",
                "text": "Not as soft as I expected for the price. The material is a bit stiff even after several washes. The color is beautiful though."
            },
            {
                "author": "AllergySufferer",
                "date": "2023-05-15",
                "text": "These sheets have helped reduce my allergic reactions at night. They're breathable and comfortable in all seasons."
            },
            {
                "author": "InteriorDesigner",
                "date": "2023-04-20",
                "text": "Beautiful quality and the colors are exactly as shown online. My clients have been very happy with these recommendations."
            }
        ]
    }
]

def get_products():
    """
    Return all products with basic sentiment analysis from database
    """
    try:
        # Try to query products from database
        from models import Product

        try:
            # Query products from database
            products_db = Product.query.all()

            if products_db:
                # Database has products, return them
                result = []
                for product in products_db:
                    # Convert product to dictionary
                    product_dict = {
                        "id": product.id,
                        "asin": product.asin,
                        "name": product.name,
                        "price": product.price,
                        "category": product.category,
                        "description": product.description,
                        "image_url": product.image_url,
                        "sentiment_score": (product.positive_score * 1.0) + (product.neutral_score * 0.5),
                        "reviews": []
                    }

                    # Add sample of reviews (limit to 3 for performance)
                    reviews = product.reviews.limit(3).all()
                    for review in reviews:
                        review_dict = {
                            "author": review.author,
                            "date": review.date.strftime("%Y-%m-%d") if review.date else None,
                            "text": review.text,
                            "rating": review.rating
                        }
                        product_dict["reviews"].append(review_dict)

                    result.append(product_dict)

                return result

        except Exception as db_error:
            # Database error, log and fall back
            logging.error(f"Database error: {str(db_error)}, falling back to sample data")

        # Return sample products if database is empty or unavailable
        return products

    except Exception as e:
        logging.error(f"Error fetching products: {str(e)}")
        return []

def get_product_by_id(product_id):
    """
    Return product by ID with detailed sentiment analysis from database
    """
    try:
        # Try to query from database first
        from models import Product, Review

        try:
            # Query product from database
            product = Product.query.get(product_id)

            if product:
                # Convert product to dictionary
                product_data = {
                    "id": product.id,
                    "asin": product.asin,
                    "name": product.name,
                    "price": product.price if product.price is not None else 0.0,
                    "category": product.category,
                    "description": product.description,
                    "image_url": product.image_url,
                    "reviews": [],
                    "sentiment_counts": {
                        "positive": product.positive_score,
                        "neutral": product.neutral_score,
                        "negative": product.negative_score
                    },
                    "sentiment_score": (product.positive_score * 1.0) + (product.neutral_score * 0.5)
                }

                # Add all reviews with sentiment analysis
                reviews = product.reviews.all()
                for review in reviews:
                    review_dict = {
                        "author": review.author,
                        "date": review.date.strftime("%Y-%m-%d") if review.date else None,
                        "text": review.text,
                        "rating": review.rating,
                        "sentiment": review.sentiment_score,
                        "sentiment_class": review.sentiment_class,
                    }

                    # Parse keywords from JSON if available
                    if review.sentiment_keywords:
                        try:
                            import json as json_module
                            review_dict["keywords"] = json_module.loads(review.sentiment_keywords)
                        except json_module.JSONDecodeError:
                            review_dict["keywords"] = []

                    product_data["reviews"].append(review_dict)

                # Add "Hype vs Reality" analysis if available
                if product.description and product_data["reviews"]:
                    from backend.sentiment_analyzer import analyze_hype_vs_reality
                    product_data["hype_vs_reality"] = analyze_hype_vs_reality(
                        product.description,
                        [r["text"] for r in product_data["reviews"]]
                    )

                return product_data

        except Exception as db_error:
            # Database error, log and fall back
            logging.error(f"Database error fetching product {product_id}: {str(db_error)}, falling back to sample data")

        # Fall back to sample data if database is unavailable
        for product in products:
            if product["id"] == product_id:
                return product

        # Product not found
        logging.warning(f"Product with ID {product_id} not found")
        return None
    except Exception as e:
        logging.error(f"Error fetching product {product_id}: {str(e)}")
        # Return a basic product info with error message instead of failing completely
        return {
            "id": product_id,
            "name": "Product Information Unavailable",
            "error": str(e),
            "reviews": [],
            "sentiment_score": 0.5
        }