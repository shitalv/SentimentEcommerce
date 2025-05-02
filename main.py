"""
Main entry point for the Sentiment E-commerce Application

This module sets up the application and serves as the entry point.
"""

import os
import sys
import logging
from flask import redirect, render_template, Flask

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import the Flask app factory
from app_factory import create_app

# Create the application
app = create_app()

# Ensure app is also available as a global variable for gunicorn
application = app

# Add a direct reports route at the application level
@app.route('/reports-direct')
def reports_direct():
    """Direct access to reports without authentication"""
    return redirect('/reports')
    
# Add a root redirect to our ultra-simple admin dashboard
@app.route('/')
def root_page():
    """Root page shows a simple admin interface directly"""
    # Get database connection
    mongo_client, db = None, None
    try:
        from mongo_config import get_mongo_client
        mongo_client, db = get_mongo_client()
    except Exception as e:
        print(f"Database connection error: {e}")
    
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
            <p>This is a direct admin interface embedded in the main application.</p>
            
            <div class="row mt-4">
                <div class="col-md-4">
                    <div class="card bg-primary text-white mb-4">
                        <div class="card-body text-center">
                            <h3>Products</h3>
                            <h2>{product_count}</h2>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card bg-success text-white mb-4">
                        <div class="card-body text-center">
                            <h3>Reviews</h3>
                            <h2>{review_count}</h2>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card bg-info text-white mb-4">
                        <div class="card-body text-center">
                            <h3>Users</h3>
                            <h2>{user_count}</h2>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="row mt-4">
                <div class="col-12">
                    <div class="card mb-4">
                        <div class="card-header">
                            <h3>Admin Navigation</h3>
                        </div>
                        <div class="card-body">
                            <div class="list-group">
                                <a href="/emergency_navigation" class="list-group-item list-group-item-action">Emergency Navigation</a>
                                <a href="/admin/products" class="list-group-item list-group-item-action">Products</a>
                                <a href="/admin/reviews" class="list-group-item list-group-item-action">Reviews</a>
                                <a href="/admin/users" class="list-group-item list-group-item-action">Users</a>
                                <a href="/admin/reports/sentiment" class="list-group-item list-group-item-action">Sentiment Reports</a>
                                <a href="/admin/reports/hype-reality" class="list-group-item list-group-item-action">Hype vs Reality</a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

# Admin direct access
@app.route('/admin-portal')
def admin_portal():
    """Direct access to admin portal without authentication"""
    return redirect('/')
    
# Add a direct route to the admin dashboard that bypasses all authentication
@app.route('/admin_dashboard_direct')
def admin_dashboard_direct():
    """Direct access to admin dashboard without template inheritance"""
    return render_template('admin_dashboard_direct.html')

# Emergency navigation with direct HTML (no templates)
@app.route('/emergency')
def emergency_direct():
    """Super simple emergency navigation with no template dependencies"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Emergency Admin Navigation</title>
        <link rel="stylesheet" href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css">
        <style>
            body { padding: 20px; }
            .nav-link { display: block; padding: 10px; margin-bottom: 5px; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="row">
                <div class="col-12">
                    <div class="alert alert-warning">
                        <h1>Emergency Admin Navigation</h1>
                        <p>This is a direct emergency access page with no dependencies on templates or authentication.</p>
                    </div>
                    
                    <div class="list-group mt-4">
                        <a href="/" class="list-group-item list-group-item-action list-group-item-primary">Home/Dashboard</a>
                        <a href="/admin/products" class="list-group-item list-group-item-action">Products Management</a>
                        <a href="/admin/reviews" class="list-group-item list-group-item-action">Reviews Management</a>
                        <a href="/admin/users" class="list-group-item list-group-item-action">Users Management</a>
                        <a href="/admin/reports/sentiment" class="list-group-item list-group-item-action">Sentiment Reports</a>
                        <a href="/admin/reports/hype-reality" class="list-group-item list-group-item-action">Hype vs Reality</a>
                        <a href="/admin/dashboard" class="list-group-item list-group-item-action">Admin Dashboard</a>
                        <a href="/admin/direct" class="list-group-item list-group-item-action">Admin Direct Access</a>
                        <a href="/admin-portal" class="list-group-item list-group-item-action">Admin Portal</a>
                        <a href="/admin_dashboard_direct" class="list-group-item list-group-item-action">Admin Dashboard Direct</a>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

# Make this clear for gunicorn in deployment
# This is the WSGI entry point that Replit uses for deployment
application = app

if __name__ == "__main__":
    # Get the port from environment or use a different default
    port = int(os.environ.get("FLASK_PORT", 5001))
    
    # Run the backend Flask app
    app.run(host="0.0.0.0", port=port, debug=True)