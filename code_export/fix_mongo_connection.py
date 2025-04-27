"""
Fix the MongoDB connection using a direct approach
This is a helper script to migrate to the working direct connection method.
"""

import pymongo
import json
import os

# Direct MongoDB connection
def direct_mongo_connect():
    # Connection string (use environment variable if available)
    mongo_uri = os.environ.get('MONGODB_URI', 
                              "mongodb+srv://testdev01:testdev01@cluster0.kx3tti3.mongodb.net/sentiment_ecommerce?retryWrites=true&w=majority&appName=Cluster0")
    db_name = "sentiment_ecommerce"
    
    print(f"Attempting to connect to MongoDB database: {db_name}")
    
    try:
        # Connect directly
        client = pymongo.MongoClient(mongo_uri)
        
        # Verify connection
        client.admin.command('ping')
        print("Successfully connected to MongoDB!")
        
        # Get database
        db = client[db_name]
        print(f"Connected to database: {db_name}")
        
        # Import sample products
        import_sample_products(db)
        
        return True
    except Exception as e:
        print(f"Error connecting to MongoDB: {str(e)}")
        return False

def import_sample_products(db):
    """Import sample products to test database write operations"""
    # Sample products
    products = [
        {
            "name": "Wireless Bluetooth Headphones",
            "description": "High-quality wireless headphones with noise cancellation technology.",
            "price": 79.99,
            "category": "Electronics",
            "image_url": "https://example.com/headphones.jpg",
            "asin": "B01ABCDEF",
            "positive_score": 0.75,
            "neutral_score": 0.15,
            "negative_score": 0.10
        },
        {
            "name": "Smart Fitness Tracker",
            "description": "Track your health and fitness with this waterproof smart band.",
            "price": 49.99,
            "category": "Wearables",
            "image_url": "https://example.com/fitness-tracker.jpg",
            "asin": "B02GHIJKL",
            "positive_score": 0.80,
            "neutral_score": 0.15,
            "negative_score": 0.05
        }
    ]
    
    # Check if products collection exists
    if "products" not in db.list_collection_names():
        print("Creating products collection...")
        db.create_collection("products")
    
    # Insert products
    for product in products:
        # Only insert if not already exists
        existing = db.products.find_one({"asin": product["asin"]})
        if not existing:
            result = db.products.insert_one(product)
            print(f"Inserted product: {product['name']} with ID: {result.inserted_id}")
        else:
            print(f"Product already exists: {product['name']}")
    
    # Count products
    count = db.products.count_documents({})
    print(f"Total products in database: {count}")
    
    # List all products
    all_products = list(db.products.find({}, {"_id": 1, "name": 1}))
    print(f"All products: {json.dumps(str(all_products))}")

if __name__ == "__main__":
    direct_mongo_connect()