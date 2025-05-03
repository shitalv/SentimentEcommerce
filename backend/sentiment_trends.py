"""
Sentiment Trends Module

This module provides functionality for tracking and analyzing sentiment trends over time.
It allows users to see how product sentiment has evolved, identifying patterns and changes
in customer satisfaction.
"""

import datetime
import logging
import json
import pandas as pd
import numpy as np
from models import Review, Product

def aggregate_sentiment_by_time(product_id=None, time_range="month", limit=12):
    """
    Aggregate sentiment data over time periods (day, week, month)
    
    Args:
        product_id: Optional product ID to filter data for a specific product
        time_range: Time granularity ('day', 'week', 'month')
        limit: Maximum number of time periods to return
        
    Returns:
        A list of time periods with aggregated sentiment data
    """
    try:
        # Query to get reviews with dates
        query = Review.query
        
        # Filter by product if specified
        if product_id:
            query = query.filter(Review.product_id == product_id)
        
        # Only consider reviews with dates
        query = query.filter(Review.date != None)
        
        # Get all relevant reviews
        reviews = query.order_by(Review.date).all()
        
        # If no reviews with dates, return empty result
        if not reviews:
            return []
        
        # Convert SQLAlchemy objects to dictionaries for easier processing
        reviews_data = [{
            'date': review.date,
            'sentiment_class': review.sentiment_class or 'neutral',
            'sentiment_score': review.sentiment_score or 0.5
        } for review in reviews if review.date]
        
        # Convert to pandas DataFrame for time-based analysis
        df = pd.DataFrame(reviews_data)
        
        # Determine period format based on time_range
        period_format = '%Y-%m'  # Default format (month)
        period_name = 'month'  # Default name
        
        if time_range == 'day':
            period_format = '%Y-%m-%d'
            period_name = 'day'
        elif time_range == 'week':
            # Use ISO week format (year-week)
            df['period'] = df['date'].apply(lambda x: f"{x.isocalendar()[0]}-W{x.isocalendar()[1]:02d}")
            period_name = 'week'
        else:  # Default to month
            period_format = '%Y-%m'
            period_name = 'month'
        
        # Format period string for day/month (week already handled above)
        if time_range != 'week':
            df['period'] = df['date'].dt.strftime(period_format)
        
        # Calculate sentiment percentages per period
        sentiment_counts = df.groupby('period')['sentiment_class'].value_counts().unstack().fillna(0)
        
        # If any sentiment class is missing, add it with zeros
        for sentiment in ['positive', 'neutral', 'negative']:
            if sentiment not in sentiment_counts.columns:
                sentiment_counts[sentiment] = 0
        
        # Calculate total reviews per period
        total_reviews = sentiment_counts.sum(axis=1)
        
        # Calculate percentages
        sentiment_percentages = sentiment_counts.div(total_reviews, axis=0) * 100
        
        # Calculate average sentiment score per period
        avg_scores = df.groupby('period')['sentiment_score'].mean()
        
        # Combine into result with limited periods
        result = []
        
        # Get the most recent periods up to the limit
        recent_periods = sentiment_percentages.index.sort_values(ascending=False)[:limit]
        
        # Sort periods chronologically for the result
        for period in sorted(recent_periods):
            period_data = {
                'period': period,
                'period_name': period_name,
                'review_count': int(total_reviews[period]),
                'avg_sentiment_score': float(avg_scores.get(period, 0.5)),
                'positive_percent': float(round(sentiment_percentages.loc[period, 'positive'], 1)),
                'neutral_percent': float(round(sentiment_percentages.loc[period, 'neutral'], 1)),
                'negative_percent': float(round(sentiment_percentages.loc[period, 'negative'], 1))
            }
            result.append(period_data)
        
        return result
        
    except Exception as e:
        logging.error(f"Error in aggregate_sentiment_by_time: {str(e)}")
        return []

def get_sentiment_trend_metrics(product_id=None):
    """
    Get sentiment trend metrics for dashboard display
    
    Args:
        product_id: Optional product ID to filter data for a specific product
        
    Returns:
        A dictionary containing trend metrics
    """
    try:
        # Get monthly data for the past few months
        monthly_data = aggregate_sentiment_by_time(product_id, 'month', 6)
        
        # Check if we have enough data for trend analysis
        if len(monthly_data) < 2:
            return {
                'insufficient_data': True,
                'trend_direction': 0,
                'trend_percent': 0
            }
        
        # Compare most recent month to previous
        current = monthly_data[-1]
        previous = monthly_data[-2]
        
        # Calculate trend direction and percentage change
        current_positive = current['positive_percent']
        previous_positive = previous['positive_percent']
        
        if previous_positive == 0:
            # Avoid division by zero
            trend_percent = 100 if current_positive > 0 else 0
        else:
            trend_percent = ((current_positive - previous_positive) / previous_positive) * 100
        
        # Determine trend direction (positive, negative, or neutral)
        if abs(trend_percent) < 5:
            trend_direction = 0  # Neutral/stable
        else:
            trend_direction = 1 if trend_percent > 0 else -1
        
        return {
            'insufficient_data': False,
            'trend_direction': trend_direction,
            'trend_percent': round(abs(trend_percent), 1),
            'current_period': current['period'],
            'previous_period': previous['period'],
            'current_positive': current_positive,
            'previous_positive': previous_positive
        }
        
    except Exception as e:
        logging.error(f"Error in get_sentiment_trend_metrics: {str(e)}")
        return {
            'insufficient_data': True,
            'error': str(e)
        }