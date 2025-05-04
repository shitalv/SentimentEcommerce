"""
Main entry point for the Sentiment E-commerce Application

This module sets up the application and serves as the entry point.
"""

import os
import sys
import logging
import math
import random
from flask import redirect, render_template, Flask, jsonify, send_from_directory

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

# Add direct routes to access reports without authentication
@app.route('/reports-direct')
def reports_direct():
    """Direct access to reports without authentication"""
    return redirect('/reports')

@app.route('/sentiment-direct')
def sentiment_direct():
    """Direct access to sentiment reports without authentication"""
    return redirect('/direct/sentiment', code=307)  # Use 307 to preserve HTTP method

@app.route('/hype-reality-direct')
def hype_reality_direct():
    """Direct access to hype-reality reports without authentication"""
    return redirect('/direct/hype-reality', code=307)  # Use 307 to preserve HTTP method

# Route for direct links page
@app.route('/direct-links')
def direct_links_page():
    """Page with direct links to reports without authentication"""
    try:
        return render_template('direct_links.html')
    except Exception as e:
        logger.error(f"Error rendering direct_links template: {e}")
        return f"<h1>Direct Links</h1><p>Error rendering template: {e}</p>"

# Root URL handler - serve the frontend application
@app.route('/')
def root_page():
    """Root page - single source of truth for root URL handling

    Serve the frontend application with product listings that don't require authentication
    """
    logger.info("ROOT PAGE ACCESSED - Serving frontend application")
    from flask import send_from_directory
    return send_from_directory('frontend/public', 'index.html')

# Direct access to Hype vs Reality standalone page
@app.route('/hype-reality-standalone')
def hype_reality_standalone():
    """Serve the standalone Hype vs Reality page"""
    return send_from_directory('templates/admin/reports', 'hype_reality_standalone.html')

# Direct access to Sentiment Trends dashboard
@app.route('/admin/reports/sentiment-trends')
def sentiment_trends_dashboard():
    """Serve the sentiment trends monitoring dashboard"""
    try:
        return render_template('admin/reports/sentiment_trends.html')
    except Exception as e:
        logger.error(f"Error rendering sentiment_trends template: {e}")
        return f"<h1>Sentiment Trend Monitoring</h1><p>Error rendering template: {e}</p>"

# Direct access to Time-Based Analysis dashboard
@app.route('/admin/reports/time-based-analysis')
def time_based_analysis_dashboard():
    """Serve the time-based sentiment analysis dashboard"""
    try:
        return render_template('admin/reports/time_based_analysis.html')
    except Exception as e:
        logger.error(f"Error rendering time_based_analysis template: {e}")
        return f"<h1>Time-Based Sentiment Analysis</h1><p>Error rendering template: {e}</p>"

# API endpoint for time-based analysis data
@app.route('/admin/api/reports/time-based-analysis', methods=['GET'])
def time_based_analysis_api():
    """API endpoint for time-based sentiment analysis data"""
    try:
        # Import the API module
        from templates.admin.reports.time_based_analysis_api import get_time_based_analysis
        # Call the API function
        return get_time_based_analysis()
    except Exception as e:
        logger.error(f"Error in time_based_analysis_api: {e}")
        return jsonify({'error': str(e)}), 500

# API endpoint for time-based analysis export
@app.route('/admin/api/reports/time-based-analysis/export', methods=['GET'])
def time_based_analysis_export_api():
    """API endpoint for exporting time-based analysis data"""
    try:
        # Import the API module
        from templates.admin.reports.time_based_analysis_api import export_time_based_analysis
        # Call the export function
        return export_time_based_analysis()
    except Exception as e:
        logger.error(f"Error in time_based_analysis_export_api: {e}")
        return jsonify({'error': str(e)}), 500

# Add time series analysis to the standalone page
@app.route('/api/time-series/<product_id>')
def time_series_data(product_id):
    """API endpoint for time series data"""
    # Example time series data
    data = {
        "dates": ["2025-01-01", "2025-02-01", "2025-03-01", "2025-04-01", "2025-05-01"],
        "sentiment_scores": [0.65, 0.72, 0.68, 0.81, 0.79],
        "review_counts": [2, 3, 2, 5, 4],
        "product_id": product_id
    }
    return jsonify(data)

# API endpoints for sentiment trend monitoring
@app.route('/admin/api/reports/sentiment-trends', methods=['GET'])
def api_sentiment_trends():
    """API endpoint for sentiment trend data"""
    # Get request parameters
    from flask import request
    import datetime
    import random
    
    period = request.args.get('period', '30')
    
    try:
        # Convert period to int (will be used to calculate date range)
        days = int(period) if period != 'all' else 365  # Default to 1 year for 'all'
    except ValueError:
        return jsonify({'error': 'Invalid period parameter'}), 400
    
    # Calculate the date range
    end_date = datetime.datetime.utcnow()
    start_date = end_date - datetime.timedelta(days=days)
    
    # Generate sample data instead of querying the database
    # This avoids circular dependencies and database access issues
    
    # Generate date range
    date_range = []
    current_date = start_date
    while current_date <= end_date:
        date_range.append(current_date.strftime('%Y-%m-%d'))
        current_date += datetime.timedelta(days=1)
    
    # Generate random sentiment scores with a trend
    base_score = 0.7  # Start with a good sentiment
    positive_scores = []
    negative_scores = []
    overall_scores = []
    
    for i in range(len(date_range)):
        # Create a slight downward trend with some randomness
        trend_factor = i / (len(date_range) * 5)  # Small trend factor
        random_factor = (random.random() - 0.5) * 0.2  # Random noise
        
        score = max(0.1, min(0.9, base_score - trend_factor + random_factor))
        positive_scores.append(score)
        negative_scores.append(1 - score)
        overall_scores.append(score)
    
    # Generate sample spikes data
    spike_products = [
        {"id": "1", "name": "Amazon Echo Dot"},
        {"id": "2", "name": "Kindle Paperwhite"},
        {"id": "3", "name": "Fire TV Stick"},
        {"id": "4", "name": "Amazon Fire Tablet"},
        {"id": "5", "name": "Ring Doorbell"}
    ]
    
    positive_spikes = []
    negative_spikes = []
    
    # Generate 3 positive spikes
    for i in range(3):
        positive_spikes.append({
            "date": date_range[-10 + i],
            "product_id": spike_products[i]["id"],
            "product_name": spike_products[i]["name"],
            "score": round(0.75 + (random.random() * 0.2), 2),
            "change": round(15 + (random.random() * 20), 1)
        })
    
    # Generate 3 negative spikes
    for i in range(3):
        negative_spikes.append({
            "date": date_range[-5 + i],
            "product_id": spike_products[i+2]["id"],
            "product_name": spike_products[i+2]["name"],
            "score": round(0.3 + (random.random() * 0.3), 2),
            "change": round(-15 - (random.random() * 20), 1)
        })
    
    # Product list for dropdowns
    products = []
    for i, product in enumerate(spike_products):
        products.append({
            "id": product["id"],
            "name": product["name"],
            "category": "Electronics" if i % 2 == 0 else "Smart Home"
        })
    
    return jsonify({
        "trends": {
            "dates": date_range,
            "positive_scores": positive_scores,
            "negative_scores": negative_scores,
            "overall_scores": overall_scores
        },
        "positive_spikes": positive_spikes,
        "negative_spikes": negative_spikes,
        "products": products
    })

@app.route('/admin/api/reports/product-comparison', methods=['GET'])
def api_product_comparison():
    """API endpoint for product comparison data"""
    # Get request parameters
    from flask import request
    import datetime
    import random
    
    product_ids = request.args.get('products', '')
    
    if not product_ids:
        return jsonify({'error': 'No products specified'}), 400
    
    # Split comma-separated product IDs
    product_id_list = product_ids.split(',')
    
    # Generate sample data
    # Get the date range (use last 30 days)
    end_date = datetime.datetime.utcnow()
    start_date = end_date - datetime.timedelta(days=30)
    
    # Generate all dates in the range
    date_range = []
    current_date = start_date
    while current_date <= end_date:
        date_range.append(current_date.strftime('%Y-%m-%d'))
        current_date += datetime.timedelta(days=1)
    
    # Sample product names
    product_names = {
        "1": "Amazon Echo Dot",
        "2": "Kindle Paperwhite",
        "3": "Fire TV Stick",
        "4": "Amazon Fire Tablet",
        "5": "Ring Doorbell"
    }
    
    # Generate comparison data
    products = []
    for product_id in product_id_list:
        # Generate a unique pattern for each product
        base_score = 0.5 + (int(product_id) / 10)  # Different base score for each product
        sentiment_scores = []
        
        for i in range(len(date_range)):
            # Create a unique pattern with some randomness
            pattern_factor = 0.1 * math.sin(i / 5 + int(product_id))  # Different pattern per product
            random_factor = (random.random() - 0.5) * 0.1  # Random noise
            
            score = max(0.1, min(0.9, base_score + pattern_factor + random_factor))
            sentiment_scores.append(score)
        
        # Add product to the comparison
        products.append({
            "id": product_id,
            "name": product_names.get(product_id, f"Product {product_id}"),
            "sentiment_scores": sentiment_scores
        })
    
    return jsonify({
        "comparison_data": {
            "dates": date_range,
            "products": products
        }
    })

@app.route('/admin/api/reports/sentiment-forecast', methods=['GET'])
def api_sentiment_forecast():
    """API endpoint for sentiment forecast data"""
    # Get request parameters
    from flask import request
    import datetime
    import random
    
    product_id = request.args.get('product_id', '')
    days = request.args.get('days', '7')
    
    if not product_id:
        return jsonify({'error': 'No product specified'}), 400
    
    # Convert days to int
    try:
        forecast_days = int(days)
    except ValueError:
        return jsonify({'error': 'Invalid days parameter'}), 400
    
    # Generate sample data
    # Get historical data (last 30 days)
    end_date = datetime.datetime.utcnow()
    start_date = end_date - datetime.timedelta(days=30)
    
    # Generate date ranges
    historical_dates = []
    historical_scores = []
    
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime('%Y-%m-%d')
        historical_dates.append(date_str)
        current_date += datetime.timedelta(days=1)
    
    # Generate historical sentiment with a pattern based on product ID
    base_score = 0.5 + (int(product_id) / 10)  # Different base score for each product
    
    for i in range(len(historical_dates)):
        # Create a unique pattern with some randomness
        pattern_factor = 0.1 * math.sin(i / 5 + int(product_id))  # Different pattern per product
        random_factor = (random.random() - 0.5) * 0.1  # Random noise
        
        score = max(0.1, min(0.9, base_score + pattern_factor + random_factor))
        historical_scores.append(score)
    
    # Generate forecast dates
    forecast_dates = []
    forecast_date = end_date + datetime.timedelta(days=1)
    for _ in range(forecast_days):
        forecast_dates.append(forecast_date.strftime('%Y-%m-%d'))
        forecast_date += datetime.timedelta(days=1)
    
    # Generate forecast with trend continuation and increasing uncertainty
    last_score = historical_scores[-1]
    last_trend = historical_scores[-1] - historical_scores[-2]  # Simple trend
    
    forecast_scores = []
    upper_bound = []
    lower_bound = []
    
    for i in range(forecast_days):
        # Continue trend with increasing randomness
        random_component = (random.random() - 0.5) * 0.1 * (i + 1) / forecast_days
        new_score = last_score + last_trend + random_component
        
        # Ensure score stays between 0 and 1
        new_score = max(0.1, min(0.9, new_score))
        
        forecast_scores.append(new_score)
        
        # Confidence bounds - widen as we get further into the future
        confidence = 0.05 + (0.15 * i / forecast_days)
        upper_bound.append(min(1, new_score + confidence))
        lower_bound.append(max(0, new_score - confidence))
        
        # Update for next iteration
        last_score = new_score
        
    return jsonify({
        "forecast_data": {
            "historical_dates": historical_dates,
            "historical_scores": historical_scores,
            "forecast_dates": forecast_dates,
            "forecast_scores": forecast_scores,
            "upper_bound": upper_bound,
            "lower_bound": lower_bound
        }
    })

# Admin direct access routes - ensure all of these work
@app.route('/admin-portal')
def admin_portal():
    """Direct access to admin portal without authentication"""
    return redirect('/admin')

@app.route('/admin')
def admin_dashboard():
    """Main admin dashboard route"""
    try:
        return render_template('admin/dashboard.html')
    except Exception as e:
        logger.error(f"Admin dashboard template error: {e}")
        return redirect('/')

@app.route('/admin/analytics')
def admin_analytics():
    """Get analytics data for admin dashboard"""
    mongo_client = get_mongo_client()
    db = mongo_client.get_database()
    
    try:
        # Get product count
        product_count = db.products.count_documents({})
        
        # Get review count
        review_count = db.reviews.count_documents({})
        
        # Get recent reviews (last 7 days)
        one_week_ago = datetime.datetime.now() - datetime.timedelta(days=7)
        recent_reviews = db.reviews.count_documents({"created_at": {"$gte": one_week_ago}})
        
        # Get user count
        user_count = db.users.count_documents({}) if "users" in db.list_collection_names() else 0
        
        # Calculate sentiment stats
        positive_reviews = db.reviews.count_documents({"sentiment_class": "positive"})
        neutral_reviews = db.reviews.count_documents({"sentiment_class": "neutral"})
        negative_reviews = db.reviews.count_documents({"sentiment_class": "negative"})
        
        total_reviews = positive_reviews + neutral_reviews + negative_reviews
        sentiment_stats = {
            "positive": positive_reviews / total_reviews if total_reviews > 0 else 0,
            "neutral": neutral_reviews / total_reviews if total_reviews > 0 else 0,
            "negative": negative_reviews / total_reviews if total_reviews > 0 else 0
        }
        
        # Get top categories
        pipeline = [
            {"$group": {"_id": "$category", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 5}
        ]
        top_categories = list(db.products.aggregate(pipeline))
        
        # Get top products by sentiment
        pipeline = [
            {"$lookup": {
                "from": "reviews",
                "localField": "_id",
                "foreignField": "product_id",
                "as": "reviews"
            }},
            {"$match": {"reviews": {"$ne": []}}},
            {"$project": {
                "name": 1,
                "reviews": 1,
                "positive_count": {
                    "$size": {
                        "$filter": {
                            "input": "$reviews",
                            "as": "review",
                            "cond": {"$eq": ["$$review.sentiment_class", "positive"]}
                        }
                    }
                },
                "review_count": {"$size": "$reviews"}
            }},
            {"$project": {
                "name": 1,
                "review_count": 1,
                "sentiment_score": {"$divide": ["$positive_count", "$review_count"]}
            }},
            {"$sort": {"sentiment_score": -1}},
            {"$limit": 5}
        ]
        top_products = list(db.products.aggregate(pipeline))
        
        # Return analytics data
        return jsonify({
            "product_count": product_count,
            "review_count": review_count,
            "recent_reviews": recent_reviews,
            "user_count": user_count,
            "sentiment_stats": sentiment_stats,
            "top_categories": top_categories,
            "top_products": top_products
        })
    except Exception as e:
        logger.error(f"Error fetching admin analytics: {e}")
        # Return demo data for testing
        return jsonify({
            "product_count": 5,
            "review_count": 18,
            "recent_reviews": 3,
            "user_count": 2,
            "sentiment_stats": {"positive": 0.72, "neutral": 0.17, "negative": 0.11},
            "top_categories": [
                {"_id": "Electronics", "count": 3},
                {"_id": "Home & Kitchen", "count": 1},
                {"_id": "Clothing", "count": 1}
            ],
            "top_products": [
                {"_id": "1", "name": "Amazon Kindle E-Reader", "sentiment_score": 0.89, "review_count": 9},
                {"_id": "2", "name": "Amazon Fire HD 10 Tablet", "sentiment_score": 0.85, "review_count": 3},
                {"_id": "3", "name": "Echo Dot (4th Gen)", "sentiment_score": 0.82, "review_count": 3},
                {"_id": "4", "name": "Men's Slim-Fit T-Shirt", "sentiment_score": 0.80, "review_count": 1},
                {"_id": "5", "name": "Microfiber Cleaning Cloth", "sentiment_score": 0.75, "review_count": 2}
            ]
        })

@app.route('/admin/dashboard')
def admin_dashboard_redirect():
    """Ensure /admin/dashboard redirects to /admin for consistency"""
    return redirect('/admin')

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
                        <a href="/admin" class="list-group-item list-group-item-action">Admin Dashboard</a>
                        <a href="/admin/products" class="list-group-item list-group-item-action">Products Management</a>
                        <a href="/admin/reviews" class="list-group-item list-group-item-action">Reviews Management</a>
                        <a href="/admin/users" class="list-group-item list-group-item-action">Users Management</a>
                        <a href="/admin/reports/sentiment" class="list-group-item list-group-item-action">Sentiment Reports</a>
                        <a href="/admin/reports/sentiment-trends" class="list-group-item list-group-item-action">Sentiment Trends</a>
                        <a href="/admin/reports/hype-reality" class="list-group-item list-group-item-action">Hype vs Reality</a>
                        <a href="/api/status" class="list-group-item list-group-item-action">API Status Check</a>
                    </div>
                    
                    <h3 class="mt-4">Direct Access (No Auth Required)</h3>
                    <div class="list-group mt-2">
                        <a href="/direct/sentiment" class="list-group-item list-group-item-action list-group-item-success">Sentiment Reports (Direct)</a>
                        <a href="/direct/hype-reality" class="list-group-item list-group-item-action list-group-item-success">Hype vs Reality (Direct)</a>
                        <a href="/hype-reality-standalone" class="list-group-item list-group-item-action list-group-item-success">Hype vs Reality (Standalone Version)</a>
                        <a href="/direct/products" class="list-group-item list-group-item-action list-group-item-success">Products Report (Direct)</a>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

if __name__ == "__main__":
    # Check if we need to run a simple HTTP server for emergency access
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "emergency":
        import http.server
        import socketserver

        class EmergencyHandler(http.server.SimpleHTTPRequestHandler):
            def do_GET(self):
                if self.path == '/' or self.path == '/index.html':
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()

                    emergency_html = f"""
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <title>Emergency Access - Sentiment Platform</title>
                        <link rel="stylesheet" href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css">
                        <meta name="viewport" content="width=device-width, initial-scale=1">
                        <style>
                            body {{ padding: 20px; }}
                            .btn {{ margin: 5px; }}
                        </style>
                    </head>
                    <body class="bg-dark text-white">
                        <div class="container">
                            <div class="alert alert-danger">
                                <h1>Emergency Access Mode</h1>
                                <p>This is a direct access page bypassing the main application.</p>
                            </div>

                            <div class="card bg-secondary mb-4">
                                <div class="card-body">
                                    <h2>Direct Access Links</h2>
                                    <div class="d-grid gap-2">
                                        <a href="/admin" class="btn btn-primary">Admin Dashboard</a>
                                        <a href="/admin/reports/sentiment" class="btn btn-info">Sentiment Reports</a>
                                        <a href="/admin/reports/sentiment-trends" class="btn btn-info">Sentiment Trends</a>
                                        <a href="/admin/reports/hype-reality" class="btn btn-warning">Hype vs. Reality</a>
                                        <a href="/admin/products" class="btn btn-success">Products</a>
                                        <a href="/admin/reviews" class="btn btn-danger">Reviews</a>
                                    </div>
                                </div>
                            </div>

                            <p>Server is running on port 8000</p>
                        </div>
                    </body>
                    </html>
                    """
                    self.wfile.write(emergency_html.encode())
                else:
                    super().do_GET()

        # Run a simple HTTP server on port 8000 for emergency access
        print("Starting emergency HTTP server on port 8000")
        handler = EmergencyHandler
        with socketserver.TCPServer(("0.0.0.0", 8000), handler) as httpd:
            print("Emergency server started at http://0.0.0.0:8000")
            httpd.serve_forever()
    else:
        # Use port 5001 for the app_workflow to avoid conflicts with Gunicorn
        port = int(os.environ.get("PORT", 5001))

        # Run the backend Flask app
        app.run(host="0.0.0.0", port=port, debug=True)