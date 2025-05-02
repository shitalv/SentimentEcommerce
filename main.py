"""
Main entry point for the Sentiment E-commerce Application

This module sets up the application and serves as the entry point.
"""

import os
import sys
import logging
from flask import redirect, render_template

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import the Flask app factory
from app_factory import create_app

# Create the application
app = create_app()

# Add a direct reports route at the application level
@app.route('/reports-direct')
def reports_direct():
    """Direct access to reports without authentication"""
    return redirect('/reports')
    
# Add a root redirect to our direct admin dashboard
@app.route('/')
def root_page():
    """Root page redirects to our ultra-simple admin dashboard"""
    return redirect('/admin/direct')

# Admin direct access
@app.route('/admin-portal')
def admin_portal():
    """Direct access to admin portal without authentication"""
    return redirect('/admin/direct')
    
# Add a direct route to the admin dashboard that bypasses all authentication
@app.route('/admin_dashboard_direct')
def admin_dashboard_direct():
    """Direct access to admin dashboard without template inheritance"""
    return render_template('admin_dashboard_direct.html')

if __name__ == "__main__":
    # Get the port from environment or use a different default
    port = int(os.environ.get("FLASK_PORT", 5001))
    
    # Run the backend Flask app
    app.run(host="0.0.0.0", port=port, debug=True)