"""
MongoDB Models for Sentiment E-commerce Application

This module defines document models for MongoDB collections.
"""

import json
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId  # Use ObjectId from bson.objectid
from mongo_config import mongo, USE_MOCK_DB, mock_db


class User(UserMixin):
    """User model for authentication"""
    
    @property
    def collection(self):
        if USE_MOCK_DB:
            return mock_db["users"]
        return mongo.db.users
    
    def __init__(self, username, email, password_hash=None, _id=None, created_at=None, is_admin=False):
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self._id = _id if _id else str(ObjectId())
        self.created_at = created_at if created_at else datetime.utcnow()
        self.is_admin = is_admin
        
    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def id(self):
        """Getter for id property, required by Flask-Login"""
        return str(self._id)
    
    def save(self):
        """Save user to database"""
        data = {
            "username": self.username,
            "email": self.email,
            "password_hash": self.password_hash,
            "created_at": self.created_at,
            "is_admin": getattr(self, 'is_admin', False)
        }
        
        if USE_MOCK_DB:
            # For mock DB, use simpler storage
            data["_id"] = self._id
            mock_db["users"][self._id] = data
        else:
            # Real MongoDB
            if not mongo.db.users.find_one({"_id": ObjectId(self._id)}):
                data["_id"] = ObjectId(self._id)
                mongo.db.users.insert_one(data)
            else:
                mongo.db.users.update_one({"_id": ObjectId(self._id)}, {"$set": data})
        
        return self
    
    @staticmethod
    def get_by_id(user_id):
        """Get user by ID (for Flask-Login)"""
        if USE_MOCK_DB:
            # Use mock data
            if user_id not in mock_db["users"]:
                return None
                
            user_data = mock_db["users"][user_id]
            return User(
                username=user_data["username"],
                email=user_data["email"],
                password_hash=user_data["password_hash"],
                _id=user_data["_id"],
                created_at=user_data.get("created_at")
            )
        else:
            # Use real MongoDB
            try:
                user_data = mongo.db.users.find_one({"_id": ObjectId(user_id)})
                if not user_data:
                    return None
                
                return User(
                    username=user_data["username"],
                    email=user_data["email"],
                    password_hash=user_data["password_hash"],
                    _id=str(user_data["_id"]),
                    created_at=user_data.get("created_at", datetime.utcnow()),
                    is_admin=user_data.get("is_admin", False)
                )
            except Exception as e:
                print(f"Error getting user by ID: {str(e)}")
                return None
            
    @staticmethod
    def get_by_username(username):
        """Get user by username"""
        if USE_MOCK_DB:
            # Search through mock data
            for user_id, user_data in mock_db["users"].items():
                if user_data["username"] == username:
                    return User(
                        username=user_data["username"],
                        email=user_data["email"],
                        password_hash=user_data["password_hash"],
                        _id=user_data["_id"],
                        created_at=user_data.get("created_at")
                    )
            return None
        else:
            user_data = mongo.db.users.find_one({"username": username})
            if not user_data:
                return None
                
            return User(
                username=user_data["username"],
                email=user_data["email"],
                password_hash=user_data["password_hash"],
                _id=str(user_data["_id"]),
                created_at=user_data.get("created_at", datetime.utcnow())
            )
    
    @staticmethod
    def get_by_email(email):
        """Get user by email"""
        if USE_MOCK_DB:
            # Search through mock data
            for user_id, user_data in mock_db["users"].items():
                if user_data["email"] == email:
                    return User(
                        username=user_data["username"],
                        email=user_data["email"],
                        password_hash=user_data["password_hash"],
                        _id=user_data["_id"],
                        created_at=user_data.get("created_at")
                    )
            return None
        else:
            user_data = mongo.db.users.find_one({"email": email})
            if not user_data:
                return None
                
            return User(
                username=user_data["username"],
                email=user_data["email"],
                password_hash=user_data["password_hash"],
                _id=str(user_data["_id"]),
                created_at=user_data.get("created_at", datetime.utcnow())
            )
    
    def get_saved_products(self):
        """Get products saved by this user"""
        if USE_MOCK_DB:
            # Mock implementation
            saved_products = []
            for saved_id, saved_data in mock_db["user_saved_products"].items():
                if saved_data["user_id"] == str(self._id):
                    saved_products.append(saved_data)
                    
            product_ids = [saved["product_id"] for saved in saved_products]
            
            products = []
            for product_id in product_ids:
                product = Product.get_by_id(product_id)
                if product:
                    products.append(product)
            return products
        else:
            # Real MongoDB implementation
            saved_products = mongo.db.user_saved_products.find({"user_id": str(self._id)})
            product_ids = [saved["product_id"] for saved in saved_products]
            
            # Get products by IDs
            products = []
            for product_id in product_ids:
                product = Product.get_by_id(product_id)
                if product:
                    products.append(product)
                    
            return products


class Product:
    """Product model to store product information"""
    
    @property
    def collection(self):
        if USE_MOCK_DB:
            return mock_db["products"]
        return mongo.db.products
    
    def __init__(self, name, description=None, price=None, category=None, 
                 image_url=None, asin=None, _id=None, created_at=None, 
                 updated_at=None, positive_score=0.0, neutral_score=0.0, 
                 negative_score=0.0):
        self.name = name
        self.description = description
        self.price = price
        self.category = category
        self.image_url = image_url
        self.asin = asin
        self._id = _id if _id else str(ObjectId())
        self.created_at = created_at if created_at else datetime.utcnow()
        self.updated_at = updated_at if updated_at else datetime.utcnow()
        self.positive_score = positive_score
        self.neutral_score = neutral_score
        self.negative_score = negative_score
    
    @property
    def id(self):
        """Getter for id property"""
        return str(self._id)
    
    def save(self):
        """Save product to database"""
        data = {
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "category": self.category,
            "image_url": self.image_url,
            "asin": self.asin,
            "updated_at": datetime.utcnow(),
            "positive_score": self.positive_score,
            "neutral_score": self.neutral_score,
            "negative_score": self.negative_score
        }
        
        if USE_MOCK_DB:
            # For mock DB, use simpler storage
            data["_id"] = self._id
            data["created_at"] = self.created_at
            mock_db["products"][self._id] = data
        else:
            # Real MongoDB
            if not mongo.db.products.find_one({"_id": ObjectId(self._id)}):
                data["_id"] = ObjectId(self._id)
                data["created_at"] = self.created_at
                mongo.db.products.insert_one(data)
            else:
                mongo.db.products.update_one({"_id": ObjectId(self._id)}, {"$set": data})
        
        return self
    
    @staticmethod
    def get_by_id(product_id):
        """Get product by ID"""
        if USE_MOCK_DB:
            # Use mock data
            if product_id not in mock_db["products"]:
                return None
                
            product_data = mock_db["products"][product_id]
            return Product(
                name=product_data["name"],
                description=product_data.get("description"),
                price=product_data.get("price"),
                category=product_data.get("category"),
                image_url=product_data.get("image_url"),
                asin=product_data.get("asin"),
                _id=product_data["_id"],
                created_at=product_data.get("created_at"),
                updated_at=product_data.get("updated_at"),
                positive_score=product_data.get("positive_score", 0.0),
                neutral_score=product_data.get("neutral_score", 0.0),
                negative_score=product_data.get("negative_score", 0.0)
            )
        else:
            # Use real MongoDB
            try:
                # Handle partial ObjectId by first trying to find by exact ID
                # then by partial ID match if necessary
                try:
                    # First try with the exact ObjectId
                    product_data = mongo.db.products.find_one({"_id": ObjectId(product_id)})
                except (TypeError, ValueError) as e:
                    print(f"Invalid ObjectId format: {product_id}, trying to find a matching ID")
                    # If the ID is not a valid ObjectId, try to find by partial ID match
                    products = list(mongo.db.products.find())
                    for product in products:
                        # Check if the provided ID is contained in the product's ID
                        if product_id in str(product["_id"]):
                            product_data = product
                            break
                    else:
                        # If no match found, return None
                        print(f"No product found with ID containing: {product_id}")
                        return None
                
                if not product_data:
                    return None
                
                return Product(
                    name=product_data["name"],
                    description=product_data.get("description"),
                    price=product_data.get("price"),
                    category=product_data.get("category"),
                    image_url=product_data.get("image_url"),
                    asin=product_data.get("asin"),
                    _id=str(product_data["_id"]),
                    created_at=product_data.get("created_at"),
                    updated_at=product_data.get("updated_at"),
                    positive_score=product_data.get("positive_score", 0.0),
                    neutral_score=product_data.get("neutral_score", 0.0),
                    negative_score=product_data.get("negative_score", 0.0)
                )
            except Exception as e:
                print(f"Error getting product by ID: {str(e)}")
                return None
    
    @staticmethod
    def get_by_asin(asin):
        """Get product by ASIN"""
        if USE_MOCK_DB:
            # Search through mock data
            for product_id, product_data in mock_db["products"].items():
                if product_data.get("asin") == asin:
                    return Product(
                        name=product_data["name"],
                        description=product_data.get("description"),
                        price=product_data.get("price"),
                        category=product_data.get("category"),
                        image_url=product_data.get("image_url"),
                        asin=product_data.get("asin"),
                        _id=product_data["_id"],
                        created_at=product_data.get("created_at"),
                        updated_at=product_data.get("updated_at"),
                        positive_score=product_data.get("positive_score", 0.0),
                        neutral_score=product_data.get("neutral_score", 0.0),
                        negative_score=product_data.get("negative_score", 0.0)
                    )
            return None
        else:
            product_data = mongo.db.products.find_one({"asin": asin})
            if not product_data:
                return None
                
            return Product(
                name=product_data["name"],
                description=product_data.get("description"),
                price=product_data.get("price"),
                category=product_data.get("category"),
                image_url=product_data.get("image_url"),
                asin=product_data.get("asin"),
                _id=str(product_data["_id"]),
                created_at=product_data.get("created_at"),
                updated_at=product_data.get("updated_at"),
                positive_score=product_data.get("positive_score", 0.0),
                neutral_score=product_data.get("neutral_score", 0.0),
                negative_score=product_data.get("negative_score", 0.0)
            )
    
    @staticmethod
    def get_all(limit=None, category=None, query=None):
        """Get all products, optionally filtered"""
        if USE_MOCK_DB:
            # Filter products in mock data
            filtered_products = []
            
            for product_id, product_data in mock_db["products"].items():
                # Apply category filter if specified
                if category and product_data.get("category") != category:
                    continue
                    
                # Apply search query if specified
                if query:
                    name = product_data.get("name", "").lower()
                    description = product_data.get("description", "").lower()
                    query_lower = query.lower()
                    if query_lower not in name and query_lower not in description:
                        continue
                
                # Add product to results
                filtered_products.append(Product(
                    name=product_data["name"],
                    description=product_data.get("description"),
                    price=product_data.get("price"),
                    category=product_data.get("category"),
                    image_url=product_data.get("image_url"),
                    asin=product_data.get("asin"),
                    _id=product_data["_id"],
                    created_at=product_data.get("created_at"),
                    updated_at=product_data.get("updated_at"),
                    positive_score=product_data.get("positive_score", 0.0),
                    neutral_score=product_data.get("neutral_score", 0.0),
                    negative_score=product_data.get("negative_score", 0.0)
                ))
                
            # Apply limit if specified
            if limit and limit < len(filtered_products):
                filtered_products = filtered_products[:limit]
                
            return filtered_products
        else:
            # Real MongoDB implementation
            query_filter = {}
            
            if category:
                query_filter["category"] = category
                
            if query:
                query_filter["$or"] = [
                    {"name": {"$regex": query, "$options": "i"}},
                    {"description": {"$regex": query, "$options": "i"}}
                ]
                
            cursor = mongo.db.products.find(query_filter)
            
            if limit:
                cursor = cursor.limit(limit)
                
            products = []
            for product_data in cursor:
                products.append(Product(
                    name=product_data["name"],
                    description=product_data.get("description"),
                    price=product_data.get("price"),
                    category=product_data.get("category"),
                    image_url=product_data.get("image_url"),
                    asin=product_data.get("asin"),
                    _id=str(product_data["_id"]),
                    created_at=product_data.get("created_at"),
                    updated_at=product_data.get("updated_at"),
                    positive_score=product_data.get("positive_score", 0.0),
                    neutral_score=product_data.get("neutral_score", 0.0),
                    negative_score=product_data.get("negative_score", 0.0)
                ))
                
            return products
    
    def get_reviews(self):
        """Get reviews for this product"""
        if USE_MOCK_DB:
            # Get reviews from mock data
            reviews = []
            for review_id, review_data in mock_db["reviews"].items():
                if review_data["product_id"] == str(self._id):
                    reviews.append(Review(
                        product_id=review_data["product_id"],
                        text=review_data["text"],
                        author=review_data.get("author"),
                        rating=review_data.get("rating"),
                        date=review_data.get("date"),
                        _id=review_data["_id"],
                        created_at=review_data.get("created_at"),
                        sentiment_score=review_data.get("sentiment_score"),
                        sentiment_class=review_data.get("sentiment_class"),
                        sentiment_keywords=review_data.get("sentiment_keywords")
                    ))
            return reviews
        else:
            # Real MongoDB implementation
            reviews_cursor = mongo.db.reviews.find({"product_id": str(self._id)})
            
            reviews = []
            for review_data in reviews_cursor:
                reviews.append(Review(
                    product_id=review_data["product_id"],
                    text=review_data["text"],
                    author=review_data.get("author"),
                    rating=review_data.get("rating"),
                    date=review_data.get("date"),
                    _id=str(review_data["_id"]),
                    created_at=review_data.get("created_at"),
                    sentiment_score=review_data.get("sentiment_score"),
                    sentiment_class=review_data.get("sentiment_class"),
                    sentiment_keywords=review_data.get("sentiment_keywords")
                ))
                
            return reviews


class Review:
    """Review model to store product reviews"""
    
    @property
    def collection(self):
        if USE_MOCK_DB:
            return mock_db["reviews"]
        return mongo.db.reviews
    
    def __init__(self, product_id, text, author=None, rating=None, date=None,
                 _id=None, created_at=None, sentiment_score=None, 
                 sentiment_class=None, sentiment_keywords=None):
        self.product_id = product_id
        self.text = text
        self.author = author
        self.rating = rating
        self.date = date
        self._id = _id if _id else str(ObjectId())
        self.created_at = created_at if created_at else datetime.utcnow()
        self.sentiment_score = sentiment_score
        self.sentiment_class = sentiment_class
        self.sentiment_keywords = sentiment_keywords
    
    @property
    def id(self):
        """Getter for id property"""
        return str(self._id)
    
    def save(self):
        """Save review to database"""
        data = {
            "product_id": self.product_id,
            "text": self.text,
            "author": self.author,
            "rating": self.rating,
            "date": self.date,
            "sentiment_score": self.sentiment_score,
            "sentiment_class": self.sentiment_class
        }
        
        # Convert keywords to JSON string if it's not already a string
        if isinstance(self.sentiment_keywords, list):
            data["sentiment_keywords"] = json.dumps(self.sentiment_keywords)
        else:
            data["sentiment_keywords"] = self.sentiment_keywords
        
        if USE_MOCK_DB:
            # For mock DB, use simpler storage
            data["_id"] = self._id
            data["created_at"] = self.created_at
            mock_db["reviews"][self._id] = data
        else:
            # Real MongoDB
            if not mongo.db.reviews.find_one({"_id": ObjectId(self._id)}):
                data["_id"] = ObjectId(self._id)
                data["created_at"] = self.created_at
                mongo.db.reviews.insert_one(data)
            else:
                mongo.db.reviews.update_one({"_id": ObjectId(self._id)}, {"$set": data})
        
        return self
        
    @staticmethod
    def get_by_id(review_id):
        """Get review by ID"""
        if USE_MOCK_DB:
            # Use mock data
            if review_id not in mock_db["reviews"]:
                return None
                
            review_data = mock_db["reviews"][review_id]
            return Review(
                product_id=review_data["product_id"],
                text=review_data["text"],
                author=review_data.get("author"),
                rating=review_data.get("rating"),
                date=review_data.get("date"),
                _id=review_data["_id"],
                created_at=review_data.get("created_at"),
                sentiment_score=review_data.get("sentiment_score"),
                sentiment_class=review_data.get("sentiment_class"),
                sentiment_keywords=review_data.get("sentiment_keywords")
            )
        else:
            # Use real MongoDB
            try:
                review_data = mongo.db.reviews.find_one({"_id": ObjectId(review_id)})
                if not review_data:
                    return None
                    
                return Review(
                    product_id=review_data["product_id"],
                    text=review_data["text"],
                    author=review_data.get("author"),
                    rating=review_data.get("rating"),
                    date=review_data.get("date"),
                    _id=str(review_data["_id"]),
                    created_at=review_data.get("created_at"),
                    sentiment_score=review_data.get("sentiment_score"),
                    sentiment_class=review_data.get("sentiment_class"),
                    sentiment_keywords=review_data.get("sentiment_keywords")
                )
            except Exception as e:
                print(f"Error getting review by ID: {str(e)}")
                return None


class UserSavedProduct:
    """Association model for users saving products"""
    
    @property
    def collection(self):
        if USE_MOCK_DB:
            return mock_db["user_saved_products"]
        return mongo.db.user_saved_products
    
    def __init__(self, user_id, product_id, _id=None, created_at=None):
        self.user_id = user_id
        self.product_id = product_id
        self._id = _id if _id else str(ObjectId())
        self.created_at = created_at if created_at else datetime.utcnow()
    
    @property
    def id(self):
        """Getter for id property"""
        return str(self._id)
    
    def save(self):
        """Save user-product association to database"""
        data = {
            "user_id": self.user_id,
            "product_id": self.product_id,
            "created_at": self.created_at
        }
        
        if USE_MOCK_DB:
            # For mock DB, check if association exists by user_id and product_id
            exists = False
            for saved_id, saved_data in mock_db["user_saved_products"].items():
                if (saved_data["user_id"] == self.user_id and 
                    saved_data["product_id"] == self.product_id):
                    exists = True
                    break
                    
            if not exists:
                data["_id"] = self._id
                mock_db["user_saved_products"][self._id] = data
        else:
            # Real MongoDB
            # Check if this association already exists
            existing = mongo.db.user_saved_products.find_one({
                "user_id": self.user_id,
                "product_id": self.product_id
            })
            
            if not existing:
                data["_id"] = ObjectId(self._id)
                mongo.db.user_saved_products.insert_one(data)
        
        return self
    
    @staticmethod
    def remove(user_id, product_id):
        """Remove user-product association from database"""
        if USE_MOCK_DB:
            # Remove from mock DB
            to_remove = []
            for saved_id, saved_data in mock_db["user_saved_products"].items():
                if (saved_data["user_id"] == user_id and 
                    saved_data["product_id"] == product_id):
                    to_remove.append(saved_id)
                    
            for saved_id in to_remove:
                if saved_id in mock_db["user_saved_products"]:
                    del mock_db["user_saved_products"][saved_id]
        else:
            # Remove from real MongoDB
            mongo.db.user_saved_products.delete_one({
                "user_id": user_id,
                "product_id": product_id
            })