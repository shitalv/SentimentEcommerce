"""
Main Flask application for Sentiment E-commerce Platform

This module sets up the Flask application, MongoDB, and handles routes.
"""

import os
import logging
from flask import Flask, jsonify, send_from_directory
from flask_login import LoginManager
from flask_cors import CORS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the Flask app
app = Flask(__name__)
CORS(app)

# Set app configuration
app.config["SECRET_KEY"] = os.environ.get("SESSION_SECRET", "default_secret_key")
app.config["MONGO_URI"] = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/sentiment_ecommerce")
app.config["MONGO_DBNAME"] = os.environ.get("MONGODB_NAME", "sentiment_ecommerce")

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Import and initialize MongoDB after app creation but before model imports
from mongo_config import init_mongo, setup_db
with app.app_context():
    init_mongo(app)
    setup_db()
    logger.info("MongoDB setup completed")

# Import models after MongoDB initialization
from models_mongo import User, Product, Review, UserSavedProduct

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)

# Import backend routes
try:
    from backend.app import bp as backend_bp
    app.register_blueprint(backend_bp)
    logger.info("Backend routes registered successfully")
except ImportError as e:
    logger.warning(f"Failed to import backend routes: {e}")

# Serve React frontend
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    """Serve React frontend static files"""
    if path != "" and os.path.exists(os.path.join('frontend/public', path)):
        return send_from_directory('frontend/public', path)
    else:
        return send_from_directory('frontend/public', 'index.html')

# Basic API endpoints (will be moved to backend blueprint later)
@app.route('/api/status')
def api_status():
    """API status check endpoint"""
    return jsonify({
        "status": "ok",
        "database": "mongodb",
        "message": "Sentiment E-commerce API is running"
    })

# Development server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)