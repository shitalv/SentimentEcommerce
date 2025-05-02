"""
Simple Admin Access

This standalone module provides the simplest possible admin dashboard access.
It runs on a separate port and has no authentication requirements.
"""

import os
from flask import Flask, render_template, redirect, url_for, jsonify
from mongo_config import get_mongo_client

# Create a standalone app
app = Flask(__name__)

# Set a secret key for session management
app.secret_key = os.environ.get("SESSION_SECRET", "development_simple_admin")

@app.route('/')
def home():
    """Simple admin home page"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Simple Admin Dashboard</title>
        <link rel="stylesheet" href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css">
        <style>
            body { padding: 20px; }
            .admin-link { margin-bottom: 10px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Simple Admin Dashboard</h1>
            <p>This is a simplified admin dashboard with direct links to all admin sections.</p>
            
            <div class="list-group mt-4">
                <a href="/dashboard" class="list-group-item list-group-item-action">Main Dashboard</a>
                <a href="/products" class="list-group-item list-group-item-action">Products</a>
                <a href="/reviews" class="list-group-item list-group-item-action">Reviews</a>
                <a href="/users" class="list-group-item list-group-item-action">Users</a>
                <a href="/sentiment" class="list-group-item list-group-item-action">Sentiment Reports</a>
                <a href="/hype-reality" class="list-group-item list-group-item-action">Hype vs. Reality</a>
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/dashboard')
def dashboard():
    """Simple admin dashboard"""
    # Get database connection
    mongo_client, db = get_mongo_client()
    
    # Get counts
    product_count = db.products.count_documents({}) if db else 0
    review_count = db.reviews.count_documents({}) if db else 0
    user_count = db.users.count_documents({}) if db else 0
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Admin Dashboard</title>
        <link rel="stylesheet" href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css">
        <style>
            body {{ padding: 20px; }}
            .stat-card {{ padding: 20px; margin-bottom: 20px; border-radius: 5px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Admin Dashboard</h1>
            <a href="/" class="btn btn-secondary mb-4">Back to Menu</a>
            
            <div class="row">
                <div class="col-md-4">
                    <div class="stat-card bg-primary text-white">
                        <h3>Products</h3>
                        <h2>{product_count}</h2>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="stat-card bg-success text-white">
                        <h3>Reviews</h3>
                        <h2>{review_count}</h2>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="stat-card bg-info text-white">
                        <h3>Users</h3>
                        <h2>{user_count}</h2>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/products')
def products():
    """Show all products"""
    # Get database connection
    mongo_client, db = get_mongo_client()
    
    # Get products
    products_list = []
    if db:
        products_cursor = db.products.find().limit(20)
        for product in products_cursor:
            products_list.append({
                "id": str(product.get("_id")),
                "name": product.get("name"),
                "category": product.get("category"),
                "price": product.get("price")
            })
    
    # Create HTML table
    products_html = ""
    for product in products_list:
        products_html += f"""
        <tr>
            <td>{product['id']}</td>
            <td>{product['name']}</td>
            <td>{product['category']}</td>
            <td>${product['price']}</td>
        </tr>
        """
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Admin Products</title>
        <link rel="stylesheet" href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css">
        <style>
            body {{ padding: 20px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Products</h1>
            <a href="/" class="btn btn-secondary mb-4">Back to Menu</a>
            
            <table class="table table-striped">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Name</th>
                        <th>Category</th>
                        <th>Price</th>
                    </tr>
                </thead>
                <tbody>
                    {products_html}
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """

@app.route('/reviews')
def reviews():
    """Show all reviews"""
    # Get database connection
    mongo_client, db = get_mongo_client()
    
    # Get reviews
    reviews_list = []
    if db:
        reviews_cursor = db.reviews.find().limit(20)
        for review in reviews_cursor:
            reviews_list.append({
                "id": str(review.get("_id")),
                "product_id": review.get("product_id"),
                "author": review.get("author"),
                "text": review.get("text")[:100] + "..." if review.get("text") and len(review.get("text")) > 100 else review.get("text"),
                "rating": review.get("rating")
            })
    
    # Create HTML table
    reviews_html = ""
    for review in reviews_list:
        reviews_html += f"""
        <tr>
            <td>{review['id']}</td>
            <td>{review['product_id']}</td>
            <td>{review['author']}</td>
            <td>{review['text']}</td>
            <td>{review['rating']}</td>
        </tr>
        """
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Admin Reviews</title>
        <link rel="stylesheet" href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css">
        <style>
            body {{ padding: 20px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Reviews</h1>
            <a href="/" class="btn btn-secondary mb-4">Back to Menu</a>
            
            <table class="table table-striped">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Product ID</th>
                        <th>Author</th>
                        <th>Text</th>
                        <th>Rating</th>
                    </tr>
                </thead>
                <tbody>
                    {reviews_html}
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """

@app.route('/users')
def users():
    """Show all users"""
    # Get database connection
    mongo_client, db = get_mongo_client()
    
    # Get users
    users_list = []
    if db:
        users_cursor = db.users.find().limit(20)
        for user in users_cursor:
            users_list.append({
                "id": str(user.get("_id")),
                "username": user.get("username"),
                "email": user.get("email"),
                "is_admin": user.get("is_admin", False)
            })
    
    # Create HTML table
    users_html = ""
    for user in users_list:
        users_html += f"""
        <tr>
            <td>{user['id']}</td>
            <td>{user['username']}</td>
            <td>{user['email']}</td>
            <td>{"Yes" if user['is_admin'] else "No"}</td>
        </tr>
        """
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Admin Users</title>
        <link rel="stylesheet" href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css">
        <style>
            body {{ padding: 20px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Users</h1>
            <a href="/" class="btn btn-secondary mb-4">Back to Menu</a>
            
            <table class="table table-striped">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Username</th>
                        <th>Email</th>
                        <th>Admin</th>
                    </tr>
                </thead>
                <tbody>
                    {users_html}
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """

@app.route('/sentiment')
def sentiment():
    """Show sentiment reports"""
    # Get database connection
    mongo_client, db = get_mongo_client()
    
    # Get sentiment data
    sentiment_data = {"positive": 0, "neutral": 0, "negative": 0}
    if db:
        products = list(db.products.find({}, {"positive_score": 1, "neutral_score": 1, "negative_score": 1}))
        if products:
            total = len(products)
            for product in products:
                sentiment_data["positive"] += product.get("positive_score", 0)
                sentiment_data["neutral"] += product.get("neutral_score", 0)
                sentiment_data["negative"] += product.get("negative_score", 0)
            
            # Calculate averages
            sentiment_data["positive"] = round(sentiment_data["positive"] / total, 2)
            sentiment_data["neutral"] = round(sentiment_data["neutral"] / total, 2)
            sentiment_data["negative"] = round(sentiment_data["negative"] / total, 2)
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Sentiment Reports</title>
        <link rel="stylesheet" href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css">
        <style>
            body {{ padding: 20px; }}
            .sentiment-bar {{ height: 30px; margin-bottom: 10px; border-radius: 5px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Sentiment Reports</h1>
            <a href="/" class="btn btn-secondary mb-4">Back to Menu</a>
            
            <div class="card p-4">
                <h3>Average Sentiment Across All Products</h3>
                
                <div class="mt-4">
                    <p>Positive: {sentiment_data["positive"]}</p>
                    <div class="progress">
                        <div class="progress-bar bg-success" style="width: {sentiment_data["positive"]*100}%"></div>
                    </div>
                </div>
                
                <div class="mt-3">
                    <p>Neutral: {sentiment_data["neutral"]}</p>
                    <div class="progress">
                        <div class="progress-bar bg-warning" style="width: {sentiment_data["neutral"]*100}%"></div>
                    </div>
                </div>
                
                <div class="mt-3">
                    <p>Negative: {sentiment_data["negative"]}</p>
                    <div class="progress">
                        <div class="progress-bar bg-danger" style="width: {sentiment_data["negative"]*100}%"></div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/hype-reality')
def hype_reality():
    """Show hype vs reality reports"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Hype vs Reality</title>
        <link rel="stylesheet" href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css">
        <style>
            body { padding: 20px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Hype vs Reality</h1>
            <a href="/" class="btn btn-secondary mb-4">Back to Menu</a>
            
            <div class="alert alert-info">
                <h4>Welcome to Hype vs Reality Analysis</h4>
                <p>This page compares marketing claims with actual customer sentiment to identify discrepancies.</p>
            </div>
            
            <div class="card p-4 mb-4">
                <h3>Amazon Echo Dot</h3>
                <div class="row">
                    <div class="col-md-6">
                        <h5>Marketing Claims</h5>
                        <ul class="list-group">
                            <li class="list-group-item">"Crisp, rich sound quality"</li>
                            <li class="list-group-item">"Voice control your smart home"</li>
                            <li class="list-group-item">"Designed to protect your privacy"</li>
                        </ul>
                    </div>
                    <div class="col-md-6">
                        <h5>Customer Sentiment</h5>
                        <div class="progress mb-2">
                            <div class="progress-bar bg-success" style="width: 85%">Sound Quality (85%)</div>
                        </div>
                        <div class="progress mb-2">
                            <div class="progress-bar bg-success" style="width: 90%">Smart Home (90%)</div>
                        </div>
                        <div class="progress mb-2">
                            <div class="progress-bar bg-warning" style="width: 60%">Privacy (60%)</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="card p-4">
                <h3>Amazon Fire HD Tablet</h3>
                <div class="row">
                    <div class="col-md-6">
                        <h5>Marketing Claims</h5>
                        <ul class="list-group">
                            <li class="list-group-item">"Vibrant HD display"</li>
                            <li class="list-group-item">"All-day battery life"</li>
                            <li class="list-group-item">"Fast and responsive performance"</li>
                        </ul>
                    </div>
                    <div class="col-md-6">
                        <h5>Customer Sentiment</h5>
                        <div class="progress mb-2">
                            <div class="progress-bar bg-success" style="width: 80%">Display (80%)</div>
                        </div>
                        <div class="progress mb-2">
                            <div class="progress-bar bg-success" style="width: 75%">Battery (75%)</div>
                        </div>
                        <div class="progress mb-2">
                            <div class="progress-bar bg-danger" style="width: 45%">Performance (45%)</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

if __name__ == "__main__":
    # Get the port from environment or use a different default
    port = int(os.environ.get("SIMPLE_ADMIN_PORT", 5002))
    
    # Run the standalone Flask app
    app.run(host="0.0.0.0", port=port, debug=True)