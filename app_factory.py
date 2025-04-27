"""
App Factory Module

This module contains functions to create and configure the Flask app
and all its dependencies to avoid circular imports.
"""

import os
import logging
import nltk
from flask import Flask, jsonify, send_from_directory
from flask_login import LoginManager
from flask_cors import CORS
from mongo_config import init_mongo, setup_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    """Create and configure the Flask app and all its dependencies"""
    # Download NLTK data
    logger.info("Downloading VADER lexicon for sentiment analysis")
    nltk.download('vader_lexicon')
    logger.info("NLTK Vader lexicon downloaded successfully")
    
    # Create the Flask app
    app = Flask(__name__)
    CORS(app)
    
    # Set app configuration
    app.config["SECRET_KEY"] = os.environ.get("SESSION_SECRET", "default_secret_key")
    app.config["MONGO_URI"] = os.environ.get("MONGODB_URI")
    app.config["MONGO_DBNAME"] = os.environ.get("MONGODB_NAME", "sentiment_ecommerce")
    
    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    
    # Initialize MongoDB
    with app.app_context():
        init_mongo(app)
        setup_db()
        logger.info("MongoDB setup completed")
    
    # Import models after MongoDB initialization
    from models_mongo import User
    
    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return User.get_by_id(user_id)
    
    # Register routes
    register_routes(app)
    
    # Setup error handlers
    register_error_handlers(app)
    
    return app

def register_routes(app):
    """Register all routes with the app"""
    # Import backend routes
    try:
        from backend.routes import bp as backend_bp
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
    
    # Basic API endpoints
    @app.route('/api/status')
    def api_status():
        """API status check endpoint"""
        return jsonify({
            "status": "ok",
            "database": "mongodb",
            "message": "Sentiment E-commerce API is running"
        })

def register_error_handlers(app):
    """Register error handlers with the app"""
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Not found"}), 404
    
    @app.errorhandler(500)
    def server_error(error):
        return jsonify({"error": "Server error"}), 500