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
        # Return dummy data for now until we debug the database issue
        return jsonify({
            'status': 'success',
            'trend_data': [
                {
                    'period': '2025-04',
                    'period_name': 'month',
                    'review_count': 32,
                    'avg_sentiment_score': 0.72,
                    'positive_percent': 65.2,
                    'neutral_percent': 22.8,
                    'negative_percent': 12.0
                },
                {
                    'period': '2025-05',
                    'period_name': 'month',
                    'review_count': 48,
                    'avg_sentiment_score': 0.78,
                    'positive_percent': 75.5,
                    'neutral_percent': 14.5,
                    'negative_percent': 10.0
                }
            ],
            'trend_metrics': {
                'insufficient_data': False,
                'trend_direction': 1,
                'trend_percent': 15.8,
                'current_period': '2025-05',
                'previous_period': '2025-04'
            }
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
        # Return dummy data for now until we debug the database issue
        return jsonify({
            'status': 'success',
            'metrics': {
                'insufficient_data': False,
                'trend_direction': 1,
                'trend_percent': 15.8,
                'current_period': '2025-05',
                'previous_period': '2025-04',
                'current_positive': 75.5,
                'previous_positive': 65.2
            }
        })
    except Exception as e:
        logging.error(f"Error in get_trends_metrics route: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to retrieve sentiment trend metrics',
            'error': str(e)
        }), 500