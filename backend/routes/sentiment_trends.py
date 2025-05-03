"""
Sentiment Trends Routes

This module provides API routes for accessing sentiment trend data over time.
"""

import logging
from flask import Blueprint, jsonify, request

# Create blueprint
sentiment_trends_bp = Blueprint('sentiment_trends', __name__, url_prefix='/api/sentiment-trends')

@sentiment_trends_bp.route('', methods=['GET'])
def get_sentiment_trends():
    """Get sentiment trends data aggregated over time"""
    try:
        # Import here to avoid circular imports
        from backend.sentiment_trends import aggregate_sentiment_by_time, get_sentiment_trend_metrics
        
        # Get query parameters
        product_id = request.args.get('product_id')
        time_range = request.args.get('time_range', 'month')
        limit = int(request.args.get('limit', 12))
        
        # Validate time_range
        if time_range not in ['day', 'week', 'month']:
            time_range = 'month'  # Default to month if invalid
        
        # Get trend data
        trend_data = aggregate_sentiment_by_time(product_id, time_range, limit)
        
        # Get trend metrics
        trend_metrics = get_sentiment_trend_metrics(product_id)
        
        # Return data
        return jsonify({
            'status': 'success',
            'trend_data': trend_data,
            'trend_metrics': trend_metrics
        })
    except Exception as e:
        logging.error(f"Error in get_sentiment_trends route: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to retrieve sentiment trend data',
            'error': str(e)
        }), 500

@sentiment_trends_bp.route('/metrics', methods=['GET'])
def get_trends_metrics():
    """Get sentiment trend metrics for dashboard display"""
    try:
        # Import here to avoid circular imports
        from backend.sentiment_trends import get_sentiment_trend_metrics
        
        # Get product_id parameter
        product_id = request.args.get('product_id')
        
        # Get metrics
        metrics = get_sentiment_trend_metrics(product_id)
        
        # Return metrics
        return jsonify({
            'status': 'success',
            'metrics': metrics
        })
    except Exception as e:
        logging.error(f"Error in get_trends_metrics route: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to retrieve sentiment trend metrics',
            'error': str(e)
        }), 500