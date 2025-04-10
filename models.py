from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from datetime import datetime


class User(UserMixin, db.Model):
    """User model for authentication"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # User's saved products
    saved_products = db.relationship('UserSavedProduct', backref='user', lazy='dynamic')

    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'


class Product(db.Model):
    """Product model to store product information"""
    id = db.Column(db.Integer, primary_key=True)
    asin = db.Column(db.String(16), unique=True, index=True)  # Amazon Standard Identification Number
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float)
    category = db.Column(db.String(128))
    image_url = db.Column(db.String(512))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    reviews = db.relationship('Review', backref='product', lazy='dynamic')
    saved_by = db.relationship('UserSavedProduct', backref='product', lazy='dynamic')
    
    # Sentiment score cache (updated periodically)
    positive_score = db.Column(db.Float, default=0.0)
    neutral_score = db.Column(db.Float, default=0.0)
    negative_score = db.Column(db.Float, default=0.0)
    
    def __repr__(self):
        return f'<Product {self.name}>'


class Review(db.Model):
    """Review model to store product reviews"""
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    author = db.Column(db.String(128))
    text = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Float)  # Star rating (1-5)
    date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Sentiment analysis results
    sentiment_score = db.Column(db.Float)  # 0-1 score where 1 is positive
    sentiment_class = db.Column(db.String(16))  # positive, neutral, negative
    sentiment_keywords = db.Column(db.Text)  # JSON list of keywords
    
    def __repr__(self):
        return f'<Review for Product {self.product_id}>'


class UserSavedProduct(db.Model):
    """Association table for users saving products"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'product_id'),)
    
    def __repr__(self):
        return f'<UserSavedProduct {self.user_id} - {self.product_id}>'