"""
Main entry point for the Sentiment E-commerce Application

This module sets up the application and serves as the entry point.
"""

import os
import sys
import logging
from flask import redirect, render_template, Flask, jsonify

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import the Flask app factory
from app_factory import create_app

# Create the application
app = create_app()

# Import MongoDB connection here to avoid circular imports
from mongo_config import get_mongo_client

# Ensure app is also available as a global variable for gunicorn
# This is what Replit expects for deployment - BOTH names are needed
application = app
# Make sure both 'app' and 'application' are defined for compatibility

# Add a direct reports route at the application level
@app.route('/reports-direct')
def reports_direct():
    """Direct access to reports without authentication"""
    return redirect('/reports')

# Root URL handler - ensure there's something at the root path
@app.route('/')
def root_page():
    """Root page - single source of truth for root URL handling
    
    Shows a simple dashboard interface with basic stats and navigation.
    No authentication required for this page since it's the landing page.
    """
    # Get database connection for stats
    mongo_client, db = None, None
    try:
        mongo_client, db = get_mongo_client()
    except Exception as e:
        logger.error(f"Database connection error: {e}")
    
    # Get counts with fallbacks if database unavailable
    product_count = db.products.count_documents({}) if db else 0
    review_count = db.reviews.count_documents({}) if db else 0
    user_count = db.users.count_documents({}) if db else 0
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Sentiment E-commerce Platform</title>
        <link rel="stylesheet" href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css">
        <style>
            body {{ padding: 20px; }}
            .stat-card {{ padding: 20px; margin-bottom: 20px; border-radius: 5px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Sentiment E-commerce Platform</h1>
            <p>AI-powered product insights based on customer sentiment analysis</p>
            
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
                            <h3>Navigation</h3>
                        </div>
                        <div class="card-body">
                            <div class="list-group">
                                <a href="/admin/dashboard" class="list-group-item list-group-item-action">Admin Dashboard</a>
                                <a href="/admin/products" class="list-group-item list-group-item-action">Products</a>
                                <a href="/admin/reviews" class="list-group-item list-group-item-action">Reviews</a>
                                <a href="/admin/users" class="list-group-item list-group-item-action">Users</a>
                                <a href="/admin/reports/sentiment" class="list-group-item list-group-item-action">Sentiment Reports</a>
                                <a href="/admin/reports/hype-reality" class="list-group-item list-group-item-action">Hype vs Reality</a>
                                <a href="/emergency" class="list-group-item list-group-item-action">Emergency Navigation</a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

# Admin direct access route
@app.route('/admin-portal')
def admin_portal():
    """Direct access to admin portal without authentication"""
    return redirect('/admin/dashboard')
    
# Direct route to admin dashboard that doesn't require template inheritance
@app.route('/admin_dashboard_direct')
def admin_dashboard_direct():
    """Direct access to admin dashboard without template inheritance"""
    try:
        return render_template('admin_dashboard_direct.html')
    except Exception as e:
        logger.error(f"Template error: {e}")
        return redirect('/')

# API status is already defined in app_factory.py, no need to redefine it here

# Emergency navigation with direct HTML (no templates)
@app.route('/emergency')
def emergency_direct():
    """Super simple emergency navigation with no template dependencies"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Emergency Navigation</title>
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
                        <h1>Emergency Navigation</h1>
                        <p>Direct access links to all important sections of the application.</p>
                    </div>
                    
                    <div class="list-group mt-4">
                        <a href="/" class="list-group-item list-group-item-action list-group-item-primary">Home</a>
                        <a href="/admin/dashboard" class="list-group-item list-group-item-action">Admin Dashboard</a>
                        <a href="/admin/products" class="list-group-item list-group-item-action">Products Management</a>
                        <a href="/admin/reviews" class="list-group-item list-group-item-action">Reviews Management</a>
                        <a href="/admin/users" class="list-group-item list-group-item-action">Users Management</a>
                        <a href="/admin/reports/sentiment" class="list-group-item list-group-item-action">Sentiment Reports</a>
                        <a href="/admin/reports/hype-reality" class="list-group-item list-group-item-action">Hype vs Reality</a>
                        <a href="/api/status" class="list-group-item list-group-item-action">API Status Check</a>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

if __name__ == "__main__":
    # Get the port from environment or use a different default
    port = int(os.environ.get("FLASK_PORT", 5001))
    
    # Run the backend Flask app
    app.run(host="0.0.0.0", port=port, debug=True)