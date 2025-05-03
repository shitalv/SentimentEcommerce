"""
Sentiment Trends Routes

This module provides API routes for accessing sentiment trend data over time.
"""

import logging
from flask import Blueprint, jsonify, request
from backend.sentiment_trends import aggregate_sentiment_by_time, get_sentiment_trend_metrics

sentiment_trends_bp = Blueprint('sentiment_trends', __name__)
logger = logging.getLogger(__name__)

@sentiment_trends_bp.route('/api/sentiment-trends', methods=['GET'])
def get_sentiment_trends():
    """Get sentiment trends data aggregated over time"""
    try:
        # Get query parameters
        product_id = request.args.get('product_id')
        time_range = request.args.get('time_range', 'month')
        limit = int(request.args.get('limit', 12))
        
        # Validate time_range parameter
        if time_range not in ['day', 'week', 'month']:
            return jsonify({"error": "Invalid time_range parameter. Use 'day', 'week', or 'month'."}), 400
        
        # Get sentiment trend data
        trend_data = aggregate_sentiment_by_time(
            product_id=product_id,
            time_range=time_range,
            limit=limit
        )
        
        # Get overall trend metrics
        trend_metrics = get_sentiment_trend_metrics(product_id=product_id)
        
        return jsonify({
            "trend_data": trend_data,
            "trend_metrics": trend_metrics,
            "time_range": time_range,
            "product_id": product_id
        })
        
    except Exception as e:
        logger.error(f"Error retrieving sentiment trends: {e}")
        return jsonify({"error": str(e)}), 500

@sentiment_trends_bp.route('/api/sentiment-trends/metrics', methods=['GET'])
def get_trends_metrics():
    """Get sentiment trend metrics for dashboard display"""
    try:
        # Get query parameters
        product_id = request.args.get('product_id')
        
        # Get trend metrics
        metrics = get_sentiment_trend_metrics(product_id=product_id)
        
        return jsonify(metrics)
        
    except Exception as e:
        logger.error(f"Error retrieving sentiment trend metrics: {e}")
        return jsonify({"error": str(e)}), 500