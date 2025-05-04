"""
Sentiment Trend Monitoring API

This module provides the backend API endpoints for the sentiment trend monitoring dashboard.
It includes endpoints for:
- Overall sentiment trends
- Sentiment anomaly detection
- Product comparison data
- Sentiment forecasting
"""

import json
import datetime
import random
from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user

# Use deferred imports to avoid circular dependencies
# We'll import these inside the functions to avoid circular references
# from models import Product, Review, db
# from sqlalchemy import func

# Create a blueprint for sentiment trends API
sentiment_trends_api = Blueprint('sentiment_trends_api', __name__)

@sentiment_trends_api.route('/admin/api/reports/sentiment-trends', methods=['GET'])
@login_required
def get_sentiment_trends():
    """API endpoint to get sentiment trend data for the dashboard"""
    # Get request parameters
    period = request.args.get('period', '30')
    
    try:
        # Convert period to int (will be used to calculate date range)
        days = int(period) if period != 'all' else 365  # Default to 1 year for 'all'
    except ValueError:
        return jsonify({'error': 'Invalid period parameter'}), 400
    
    # Calculate the date range
    end_date = datetime.datetime.utcnow()
    start_date = end_date - datetime.timedelta(days=days)
    
    try:
        # Get sentiment trend data
        trend_data = get_sentiment_trend_data(start_date, end_date)
        
        # Get positive and negative spikes
        positive_spikes = get_sentiment_spikes(start_date, end_date, spike_type='positive')
        negative_spikes = get_sentiment_spikes(start_date, end_date, spike_type='negative')
        
        # Get product list for dropdowns
        products = get_product_list()
        
        return jsonify({
            'trends': trend_data,
            'positive_spikes': positive_spikes,
            'negative_spikes': negative_spikes,
            'products': products
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@sentiment_trends_api.route('/admin/api/reports/product-comparison', methods=['GET'])
@login_required
def get_product_comparison():
    """API endpoint to get comparison data for multiple products"""
    # Get request parameters
    product_ids = request.args.get('products', '')
    
    if not product_ids:
        return jsonify({'error': 'No products specified'}), 400
    
    try:
        # Split comma-separated product IDs
        product_id_list = product_ids.split(',')
        
        # Get comparison data
        comparison_data = get_product_comparison_data(product_id_list)
        
        return jsonify({
            'comparison_data': comparison_data
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@sentiment_trends_api.route('/admin/api/reports/sentiment-forecast', methods=['GET'])
@login_required
def get_sentiment_forecast():
    """API endpoint to get sentiment forecast for a product"""
    # Get request parameters
    product_id = request.args.get('product_id', '')
    days = request.args.get('days', '7')
    
    if not product_id:
        return jsonify({'error': 'No product specified'}), 400
    
    try:
        # Convert days to int
        forecast_days = int(days)
    except ValueError:
        return jsonify({'error': 'Invalid days parameter'}), 400
    
    try:
        # Get forecast data
        forecast_data = get_forecast_data(product_id, forecast_days)
        
        return jsonify({
            'forecast_data': forecast_data
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Helper functions for data retrieval

def get_sentiment_trend_data(start_date, end_date):
    """
    Get sentiment trend data for the overall trend chart
    
    Returns a dict with:
    - dates: list of date strings
    - positive_scores: list of daily positive sentiment scores
    - negative_scores: list of daily negative sentiment scores
    - overall_scores: list of daily overall sentiment scores
    """
    # Query database for sentiment over time
    # For each day in the range, aggregate sentiment scores
    try:
        # Generate all dates in the range
        date_range = []
        current_date = start_date
        while current_date <= end_date:
            date_range.append(current_date.strftime('%Y-%m-%d'))
            current_date += datetime.timedelta(days=1)
        
        # Query daily sentiment scores
        daily_sentiments = db.session.query(
            func.date(Review.date).label('review_date'),
            func.avg(Review.sentiment_score).label('avg_score'),
            func.count(Review.id).label('review_count')
        ).filter(
            Review.date.between(start_date, end_date)
        ).group_by(
            func.date(Review.date)
        ).all()
        
        # Create a dict of date -> sentiment data for faster lookup
        daily_data = {item.review_date.strftime('%Y-%m-%d'): {
            'avg_score': float(item.avg_score) if item.avg_score else 0.5,
            'review_count': item.review_count
        } for item in daily_sentiments}
        
        # Generate the complete series with all dates
        positive_scores = []
        negative_scores = []
        overall_scores = []
        
        for date_str in date_range:
            if date_str in daily_data:
                score = daily_data[date_str]['avg_score']
                # Calculate positive and negative components
                positive_scores.append(score)
                negative_scores.append(1 - score)  # Inverse of positive is negative
                overall_scores.append(score)
            else:
                # No data for this date - use default or interpolate
                positive_scores.append(None)
                negative_scores.append(None)
                overall_scores.append(None)
        
        # Handle missing values (None) - replace with interpolated values
        # Simple linear interpolation
        for i in range(1, len(overall_scores) - 1):
            if overall_scores[i] is None:
                # Find nearest non-None values before and after
                prev_idx = i - 1
                while prev_idx >= 0 and overall_scores[prev_idx] is None:
                    prev_idx -= 1
                
                next_idx = i + 1
                while next_idx < len(overall_scores) and overall_scores[next_idx] is None:
                    next_idx += 1
                
                if prev_idx >= 0 and next_idx < len(overall_scores):
                    # Interpolate
                    prev_val = overall_scores[prev_idx]
                    next_val = overall_scores[next_idx]
                    weight = (i - prev_idx) / (next_idx - prev_idx)
                    
                    interpolated = prev_val + (next_val - prev_val) * weight
                    overall_scores[i] = interpolated
                    positive_scores[i] = interpolated
                    negative_scores[i] = 1 - interpolated
                elif prev_idx >= 0:
                    # Use previous value
                    overall_scores[i] = overall_scores[prev_idx]
                    positive_scores[i] = positive_scores[prev_idx]
                    negative_scores[i] = negative_scores[prev_idx]
                elif next_idx < len(overall_scores):
                    # Use next value
                    overall_scores[i] = overall_scores[next_idx]
                    positive_scores[i] = positive_scores[next_idx]
                    negative_scores[i] = negative_scores[next_idx]
                else:
                    # Default value as fallback
                    overall_scores[i] = 0.5
                    positive_scores[i] = 0.5
                    negative_scores[i] = 0.5
        
        # Handle edge cases (first and last elements)
        if overall_scores[0] is None:
            # Find first non-None value
            next_idx = 1
            while next_idx < len(overall_scores) and overall_scores[next_idx] is None:
                next_idx += 1
            
            if next_idx < len(overall_scores):
                overall_scores[0] = overall_scores[next_idx]
                positive_scores[0] = positive_scores[next_idx]
                negative_scores[0] = negative_scores[next_idx]
            else:
                overall_scores[0] = 0.5
                positive_scores[0] = 0.5
                negative_scores[0] = 0.5
        
        if overall_scores[-1] is None:
            # Find last non-None value
            prev_idx = len(overall_scores) - 2
            while prev_idx >= 0 and overall_scores[prev_idx] is None:
                prev_idx -= 1
            
            if prev_idx >= 0:
                overall_scores[-1] = overall_scores[prev_idx]
                positive_scores[-1] = positive_scores[prev_idx]
                negative_scores[-1] = negative_scores[prev_idx]
            else:
                overall_scores[-1] = 0.5
                positive_scores[-1] = 0.5
                negative_scores[-1] = 0.5
        
        return {
            'dates': date_range,
            'positive_scores': positive_scores,
            'negative_scores': negative_scores,
            'overall_scores': overall_scores
        }
    
    except Exception as e:
        print(f"Error getting trend data: {e}")
        raise

def get_sentiment_spikes(start_date, end_date, spike_type='positive'):
    """
    Get sentiment spikes for anomaly detection
    
    Parameters:
    - start_date: start of the period
    - end_date: end of the period
    - spike_type: 'positive' or 'negative'
    
    Returns a list of dictionaries with:
    - date: date of the spike
    - product_id: ID of the product
    - product_name: name of the product
    - score: sentiment score
    - change: percentage change
    """
    try:
        # Query database for daily sentiment scores by product
        daily_product_sentiments = db.session.query(
            func.date(Review.date).label('review_date'),
            Review.product_id,
            Product.name.label('product_name'),
            func.avg(Review.sentiment_score).label('avg_score'),
            func.count(Review.id).label('review_count')
        ).join(
            Product, Review.product_id == Product.id
        ).filter(
            Review.date.between(start_date, end_date)
        ).group_by(
            func.date(Review.date),
            Review.product_id,
            Product.name
        ).having(
            func.count(Review.id) >= 3  # Minimum number of reviews
        ).all()
        
        # Organize by product
        product_data = {}
        for item in daily_product_sentiments:
            product_id = item.product_id
            if product_id not in product_data:
                product_data[product_id] = {
                    'name': item.product_name,
                    'daily_scores': []
                }
            
            product_data[product_id]['daily_scores'].append({
                'date': item.review_date.strftime('%Y-%m-%d'),
                'score': float(item.avg_score) if item.avg_score else 0.5,
                'count': item.review_count
            })
        
        # Calculate day-to-day changes and find spikes
        spikes = []
        
        for product_id, data in product_data.items():
            daily_scores = sorted(data['daily_scores'], key=lambda x: x['date'])
            
            if len(daily_scores) < 2:
                continue  # Need at least 2 days to calculate change
            
            for i in range(1, len(daily_scores)):
                today = daily_scores[i]
                yesterday = daily_scores[i-1]
                
                # Calculate percentage change
                previous_score = yesterday['score']
                current_score = today['score']
                
                if previous_score > 0:
                    change_pct = ((current_score - previous_score) / previous_score) * 100
                else:
                    change_pct = 100  # Arbitrarily large when previous was 0
                
                # Determine if this is a spike of the requested type
                # For positive spikes: score increase
                # For negative spikes: score decrease
                is_spike = False
                
                if spike_type == 'positive' and change_pct > 15:  # >15% increase
                    is_spike = True
                elif spike_type == 'negative' and change_pct < -15:  # >15% decrease
                    is_spike = True
                
                if is_spike:
                    spikes.append({
                        'date': today['date'],
                        'product_id': product_id,
                        'product_name': data['name'],
                        'score': current_score,
                        'change': round(change_pct, 1)
                    })
        
        # Sort by absolute change magnitude
        spikes.sort(key=lambda x: abs(x['change']), reverse=True)
        
        # Return top 5 spikes
        return spikes[:5]
    
    except Exception as e:
        print(f"Error getting spikes: {e}")
        raise

def get_product_list():
    """Get list of products for dropdowns"""
    try:
        products = db.session.query(
            Product.id,
            Product.name,
            Product.category
        ).all()
        
        return [{
            'id': str(p.id),
            'name': p.name,
            'category': p.category or 'Uncategorized'
        } for p in products]
    
    except Exception as e:
        print(f"Error getting product list: {e}")
        raise

def get_product_comparison_data(product_id_list):
    """
    Get sentiment comparison data for multiple products
    
    Parameters:
    - product_id_list: list of product IDs
    
    Returns a dict with:
    - dates: list of date strings
    - products: list of product data dicts
    """
    try:
        # Get the date range (use last 30 days)
        end_date = datetime.datetime.utcnow()
        start_date = end_date - datetime.timedelta(days=30)
        
        # Generate all dates in the range
        date_range = []
        current_date = start_date
        while current_date <= end_date:
            date_range.append(current_date.strftime('%Y-%m-%d'))
            current_date += datetime.timedelta(days=1)
        
        # Query daily sentiment scores for each product
        product_sentiments = []
        
        for product_id in product_id_list:
            # Query product info
            product = db.session.query(
                Product.id,
                Product.name
            ).filter(
                Product.id == product_id
            ).first()
            
            if not product:
                continue
            
            # Query daily sentiment scores
            daily_scores = db.session.query(
                func.date(Review.date).label('review_date'),
                func.avg(Review.sentiment_score).label('avg_score')
            ).filter(
                Review.product_id == product_id,
                Review.date.between(start_date, end_date)
            ).group_by(
                func.date(Review.date)
            ).all()
            
            # Create a dict of date -> score for faster lookup
            score_dict = {item.review_date.strftime('%Y-%m-%d'): 
                         float(item.avg_score) if item.avg_score else 0.5 
                         for item in daily_scores}
            
            # Generate complete series
            sentiment_scores = []
            for date_str in date_range:
                if date_str in score_dict:
                    sentiment_scores.append(score_dict[date_str])
                else:
                    sentiment_scores.append(None)
            
            # Handle missing values with interpolation
            # Similar to the one in get_sentiment_trend_data
            for i in range(1, len(sentiment_scores) - 1):
                if sentiment_scores[i] is None:
                    # Find nearest non-None values before and after
                    prev_idx = i - 1
                    while prev_idx >= 0 and sentiment_scores[prev_idx] is None:
                        prev_idx -= 1
                    
                    next_idx = i + 1
                    while next_idx < len(sentiment_scores) and sentiment_scores[next_idx] is None:
                        next_idx += 1
                    
                    if prev_idx >= 0 and next_idx < len(sentiment_scores):
                        # Interpolate
                        prev_val = sentiment_scores[prev_idx]
                        next_val = sentiment_scores[next_idx]
                        weight = (i - prev_idx) / (next_idx - prev_idx)
                        
                        sentiment_scores[i] = prev_val + (next_val - prev_val) * weight
                    elif prev_idx >= 0:
                        sentiment_scores[i] = sentiment_scores[prev_idx]
                    elif next_idx < len(sentiment_scores):
                        sentiment_scores[i] = sentiment_scores[next_idx]
                    else:
                        sentiment_scores[i] = 0.5
            
            # Handle edge cases
            if sentiment_scores[0] is None:
                next_valid = next((s for s in sentiment_scores if s is not None), 0.5)
                sentiment_scores[0] = next_valid
                
            if sentiment_scores[-1] is None:
                prev_valid = next((s for s in reversed(sentiment_scores) if s is not None), 0.5)
                sentiment_scores[-1] = prev_valid
            
            product_sentiments.append({
                'id': str(product.id),
                'name': product.name,
                'sentiment_scores': sentiment_scores
            })
        
        return {
            'dates': date_range,
            'products': product_sentiments
        }
    
    except Exception as e:
        print(f"Error getting product comparison data: {e}")
        raise

def get_forecast_data(product_id, forecast_days=7):
    """
    Get sentiment forecast data
    
    Parameters:
    - product_id: ID of the product
    - forecast_days: number of days to forecast
    
    Returns a dict with:
    - historical_dates: list of date strings for historical data
    - historical_scores: list of historical sentiment scores
    - forecast_dates: list of date strings for forecast
    - forecast_scores: list of forecasted sentiment scores
    - upper_bound: list of upper confidence bounds
    - lower_bound: list of lower confidence bounds
    """
    try:
        # Get historical data (last 30 days)
        end_date = datetime.datetime.utcnow()
        start_date = end_date - datetime.timedelta(days=30)
        
        # Query historical sentiment scores
        historical_data = db.session.query(
            func.date(Review.date).label('review_date'),
            func.avg(Review.sentiment_score).label('avg_score')
        ).filter(
            Review.product_id == product_id,
            Review.date.between(start_date, end_date)
        ).group_by(
            func.date(Review.date)
        ).all()
        
        # Generate date ranges
        historical_dates = []
        historical_scores = []
        
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            historical_dates.append(date_str)
            current_date += datetime.timedelta(days=1)
        
        # Create score dictionary for faster lookup
        score_dict = {item.review_date.strftime('%Y-%m-%d'): 
                     float(item.avg_score) if item.avg_score else 0.5 
                     for item in historical_data}
        
        # Fill historical scores
        for date_str in historical_dates:
            if date_str in score_dict:
                historical_scores.append(score_dict[date_str])
            else:
                historical_scores.append(None)
        
        # Handle missing values with interpolation
        # Similar to previous interpolation functions
        for i in range(1, len(historical_scores) - 1):
            if historical_scores[i] is None:
                # Find nearest non-None values before and after
                prev_idx = i - 1
                while prev_idx >= 0 and historical_scores[prev_idx] is None:
                    prev_idx -= 1
                
                next_idx = i + 1
                while next_idx < len(historical_scores) and historical_scores[next_idx] is None:
                    next_idx += 1
                
                if prev_idx >= 0 and next_idx < len(historical_scores):
                    # Interpolate
                    prev_val = historical_scores[prev_idx]
                    next_val = historical_scores[next_idx]
                    weight = (i - prev_idx) / (next_idx - prev_idx)
                    
                    historical_scores[i] = prev_val + (next_val - prev_val) * weight
                elif prev_idx >= 0:
                    historical_scores[i] = historical_scores[prev_idx]
                elif next_idx < len(historical_scores):
                    historical_scores[i] = historical_scores[next_idx]
                else:
                    historical_scores[i] = 0.5
        
        # Handle edge cases
        if historical_scores[0] is None:
            next_valid = next((s for s in historical_scores if s is not None), 0.5)
            historical_scores[0] = next_valid
            
        if historical_scores[-1] is None:
            prev_valid = next((s for s in reversed(historical_scores) if s is not None), 0.5)
            historical_scores[-1] = prev_valid
        
        # Generate forecast dates
        forecast_dates = []
        forecast_date = end_date + datetime.timedelta(days=1)
        for _ in range(forecast_days):
            forecast_dates.append(forecast_date.strftime('%Y-%m-%d'))
            forecast_date += datetime.timedelta(days=1)
        
        # In a real implementation, use a time series forecasting algorithm here
        # For this demo, we'll use a simple moving average with some randomness
        
        # Calculate moving average of last 7 days
        last_week_avg = sum(historical_scores[-7:]) / 7 if len(historical_scores) >= 7 else 0.5
        
        # Generate forecast with some randomness, but maintain trend direction
        forecast_scores = []
        upper_bound = []
        lower_bound = []
        
        last_score = historical_scores[-1]
        for i in range(forecast_days):
            # Slight regression toward the moving average
            regression = 0.2 * (last_week_avg - last_score)
            
            # Random component - increases with days into future
            random_component = (random.random() - 0.5) * 0.05 * (i + 1) / forecast_days
            
            # New forecast value
            new_score = last_score + regression + random_component
            
            # Ensure the score stays between 0 and 1
            new_score = max(0, min(1, new_score))
            
            forecast_scores.append(new_score)
            
            # Confidence bounds - widen as we get further into the future
            confidence = 0.05 + (0.15 * i / forecast_days)
            upper_bound.append(min(1, new_score + confidence))
            lower_bound.append(max(0, new_score - confidence))
            
            # Update last score for next iteration
            last_score = new_score
        
        return {
            'historical_dates': historical_dates,
            'historical_scores': historical_scores,
            'forecast_dates': forecast_dates,
            'forecast_scores': forecast_scores,
            'upper_bound': upper_bound,
            'lower_bound': lower_bound
        }
    
    except Exception as e:
        print(f"Error getting forecast data: {e}")
        raise