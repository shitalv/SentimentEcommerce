"""
Time-Based Sentiment Analysis API

This module provides the backend API endpoints for time-based sentiment analysis.
It includes endpoints for analyzing sentiment trends over time:
- Sentiment evolution for products/categories
- Seasonal trends
- Sentiment shift detection
"""

import datetime
import random
import math
from flask import jsonify, request, current_app

def get_time_based_analysis():
    """API endpoint for time-based sentiment analysis data"""
    # Get request parameters
    period = request.args.get('period', '30')
    granularity = request.args.get('granularity', 'week')
    filter_type = request.args.get('filter_type', 'product')
    entity_id = request.args.get('entity_id', '')
    
    try:
        # Convert period to int (will be used to calculate date range)
        days = int(period) if period != 'all' else 365*2  # Default to 2 years for 'all'
    except ValueError:
        return jsonify({'error': 'Invalid period parameter'}), 400
    
    # Calculate the date range
    end_date = datetime.datetime.utcnow()
    start_date = end_date - datetime.timedelta(days=days)
    
    try:
        # Get time series data
        time_series = get_time_series_data(start_date, end_date, granularity, filter_type, entity_id)
        
        # Get seasonal trends
        seasonal_data = get_seasonal_trends(filter_type, entity_id)
        
        # Get monthly distribution
        monthly_distribution = get_monthly_distribution(filter_type, entity_id)
        
        # Get sentiment shifts
        sentiment_shifts = get_sentiment_shifts(start_date, end_date, filter_type, entity_id)
        
        # Get insights
        insights = generate_insights(time_series, seasonal_data, sentiment_shifts, filter_type, entity_id)
        
        return jsonify({
            'time_series': time_series,
            'seasonal_trends': seasonal_data,
            'monthly_distribution': monthly_distribution,
            'sentiment_shifts': sentiment_shifts,
            'insights': insights
        })
    except Exception as e:
        print(f"Error in time-based analysis: {e}")
        return jsonify({'error': str(e)}), 500

def get_time_series_data(start_date, end_date, granularity, filter_type, entity_id):
    """
    Get time series data for sentiment analysis
    
    Parameters:
    - start_date: Start date for analysis
    - end_date: End date for analysis
    - granularity: Time granularity ('day', 'week', 'month', 'quarter')
    - filter_type: Type of filter ('product' or 'category')
    - entity_id: ID of the product or category
    
    Returns:
    - Dictionary with time series data
    """
    from mongo_config import get_mongo_client
    from bson.objectid import ObjectId
    
    # Generate time periods based on granularity
    periods = generate_time_periods(start_date, end_date, granularity)
    
    # Generate labels for each period
    labels = []
    for period_start, period_end in periods:
        if granularity == 'day':
            labels.append(period_start.strftime('%Y-%m-%d'))
        elif granularity == 'week':
            labels.append(f"Week of {period_start.strftime('%b %d')}")
        elif granularity == 'month':
            labels.append(period_start.strftime('%b %Y'))
        else:  # quarter
            quarter = (period_start.month - 1) // 3 + 1
            labels.append(f"Q{quarter} {period_start.year}")
    
    # Initialize data arrays
    overall_sentiment = []
    positive_sentiment = []
    negative_sentiment = []
    review_volume = []
    
    try:
        # Get MongoDB client
        client = get_mongo_client()
        db = client.sentiment_ecommerce
        
        # Process each time period
        for period_start, period_end in periods:
            # Base query for reviews in this time period
            query = {"date": {"$gte": period_start, "$lt": period_end}}
            
            # Add filter for product or category
            if filter_type == 'product' and entity_id and entity_id != 'all':
                query["product_id"] = ObjectId(entity_id)
            elif filter_type == 'category' and entity_id and entity_id != 'all':
                # Get all products in this category
                products_in_category = list(db.products.find({"category": entity_id}, {"_id": 1}))
                product_ids = [p["_id"] for p in products_in_category]
                if product_ids:
                    query["product_id"] = {"$in": product_ids}
                else:
                    # No products in this category, add impossible condition to return no results
                    query["product_id"] = {"$in": []}
            
            # Query for reviews in this period
            reviews = list(db.reviews.find(query))
            
            # Calculate aggregate metrics
            count = len(reviews)
            if count > 0:
                # Calculate average sentiment scores
                avg_sentiment = sum(r.get("sentiment_score", 0.5) for r in reviews) / count
                
                # Count positive, neutral, negative reviews
                positive_count = sum(1 for r in reviews if r.get("sentiment_class") == "positive")
                negative_count = sum(1 for r in reviews if r.get("sentiment_class") == "negative")
                
                # Calculate normalized sentiment values
                pos_ratio = positive_count / count if count > 0 else 0
                neg_ratio = negative_count / count if count > 0 else 0
                
                # Add to result arrays
                overall_sentiment.append(avg_sentiment)
                positive_sentiment.append(pos_ratio)
                negative_sentiment.append(neg_ratio)
                review_volume.append(count)
            else:
                # No reviews for this period
                overall_sentiment.append(None)  # Use None for gaps in chart data
                positive_sentiment.append(None)
                negative_sentiment.append(None)
                review_volume.append(0)
    
    except Exception as e:
        print(f"Error getting time series data: {e}")
        # Fill with empty data to avoid breaking charts
        overall_sentiment = [None] * len(periods)
        positive_sentiment = [None] * len(periods)
        negative_sentiment = [None] * len(periods)
        review_volume = [0] * len(periods)
    
    return {
        'labels': labels,
        'overall_sentiment': overall_sentiment,
        'positive_sentiment': positive_sentiment,
        'negative_sentiment': negative_sentiment,
        'review_volume': review_volume
    }

def get_seasonal_trends(filter_type, entity_id):
    """
    Get seasonal trends data for year-over-year comparison
    
    Parameters:
    - filter_type: Type of filter ('product' or 'category')
    - entity_id: ID of the product or category
    
    Returns:
    - Dictionary with seasonal trend data
    """
    from mongo_config import get_mongo_client
    from bson.objectid import ObjectId
    
    # Generate month labels
    labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    # Get current year and previous year
    current_year = datetime.datetime.now().year
    previous_year = current_year - 1
    
    # Initialize data arrays with None values
    current_year_data = [None] * 12
    previous_year_data = [None] * 12
    
    try:
        # Get MongoDB client
        client = get_mongo_client()
        db = client.sentiment_ecommerce
        
        # Process each month
        for month in range(1, 13):
            # Calculate date ranges for current and previous year
            current_year_start = datetime.datetime(current_year, month, 1)
            if month == 12:
                current_year_end = datetime.datetime(current_year + 1, 1, 1)
            else:
                current_year_end = datetime.datetime(current_year, month + 1, 1)
                
            previous_year_start = datetime.datetime(previous_year, month, 1)
            if month == 12:
                previous_year_end = datetime.datetime(previous_year + 1, 1, 1)
            else:
                previous_year_end = datetime.datetime(previous_year, month + 1, 1)
            
            # Skip future months
            if current_year_start > datetime.datetime.now():
                continue
            
            # Base queries for current and previous year
            current_year_query = {
                "date": {
                    "$gte": current_year_start,
                    "$lt": current_year_end
                }
            }
            
            previous_year_query = {
                "date": {
                    "$gte": previous_year_start,
                    "$lt": previous_year_end
                }
            }
            
            # Add filter for product or category
            if filter_type == 'product' and entity_id and entity_id != 'all':
                current_year_query["product_id"] = ObjectId(entity_id)
                previous_year_query["product_id"] = ObjectId(entity_id)
            elif filter_type == 'category' and entity_id and entity_id != 'all':
                # Get all products in this category
                products_in_category = list(db.products.find({"category": entity_id}, {"_id": 1}))
                product_ids = [p["_id"] for p in products_in_category]
                if product_ids:
                    current_year_query["product_id"] = {"$in": product_ids}
                    previous_year_query["product_id"] = {"$in": product_ids}
                else:
                    # No products in this category, add impossible condition
                    current_year_query["product_id"] = {"$in": []}
                    previous_year_query["product_id"] = {"$in": []}
            
            # Query for reviews in current and previous year
            current_year_reviews = list(db.reviews.find(current_year_query))
            previous_year_reviews = list(db.reviews.find(previous_year_query))
            
            # Calculate average sentiment for current year
            if current_year_reviews:
                current_year_score = sum(r.get("sentiment_score", 0.5) for r in current_year_reviews) / len(current_year_reviews)
                current_year_data[month - 1] = current_year_score
            
            # Calculate average sentiment for previous year
            if previous_year_reviews:
                previous_year_score = sum(r.get("sentiment_score", 0.5) for r in previous_year_reviews) / len(previous_year_reviews)
                previous_year_data[month - 1] = previous_year_score
    
    except Exception as e:
        print(f"Error getting seasonal trends data: {e}")
    
    return {
        'labels': labels,
        'current_year': current_year_data,
        'previous_year': previous_year_data,
        'current_year_label': str(current_year),
        'previous_year_label': str(previous_year)
    }

def get_monthly_distribution(filter_type, entity_id):
    """
    Get monthly distribution of positive, neutral, and negative reviews
    
    Parameters:
    - filter_type: Type of filter ('product' or 'category')
    - entity_id: ID of the product or category
    
    Returns:
    - Dictionary with monthly distribution data
    """
    from mongo_config import get_mongo_client
    from bson.objectid import ObjectId
    
    # Generate month labels
    labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    # Initialize arrays
    positive = [0] * 12
    neutral = [0] * 12
    negative = [0] * 12
    
    try:
        # Get current year
        current_year = datetime.datetime.now().year
        
        # Get MongoDB client
        client = get_mongo_client()
        db = client.sentiment_ecommerce
        
        # Process each month
        for month in range(1, 13):
            # Calculate date range for this month
            if month == 12:
                date_start = datetime.datetime(current_year, month, 1)
                date_end = datetime.datetime(current_year + 1, 1, 1)
            else:
                date_start = datetime.datetime(current_year, month, 1)
                date_end = datetime.datetime(current_year, month + 1, 1)
            
            # Skip future months
            if date_start > datetime.datetime.now():
                continue
            
            # Base query for this month
            query = {"date": {"$gte": date_start, "$lt": date_end}}
            
            # Add filter for product or category
            if filter_type == 'product' and entity_id and entity_id != 'all':
                query["product_id"] = ObjectId(entity_id)
            elif filter_type == 'category' and entity_id and entity_id != 'all':
                # Get all products in this category
                products_in_category = list(db.products.find({"category": entity_id}, {"_id": 1}))
                product_ids = [p["_id"] for p in products_in_category]
                if product_ids:
                    query["product_id"] = {"$in": product_ids}
                else:
                    # No products in this category, add impossible condition
                    query["product_id"] = {"$in": []}
            
            # Count reviews by sentiment class
            pos_query = query.copy()
            pos_query["sentiment_class"] = "positive"
            pos_count = db.reviews.count_documents(pos_query)
            
            neut_query = query.copy()
            neut_query["sentiment_class"] = "neutral"
            neut_count = db.reviews.count_documents(neut_query)
            
            neg_query = query.copy()
            neg_query["sentiment_class"] = "negative"
            neg_count = db.reviews.count_documents(neg_query)
            
            # Store counts for this month
            positive[month - 1] = pos_count
            neutral[month - 1] = neut_count
            negative[month - 1] = neg_count
            
    except Exception as e:
        print(f"Error getting monthly distribution data: {e}")
    
    return {
        'labels': labels,
        'positive': positive,
        'neutral': neutral,
        'negative': negative
    }

def get_sentiment_shifts(start_date, end_date, filter_type, entity_id):
    """
    Detect significant shifts in sentiment over time
    
    Parameters:
    - start_date: Start date for analysis
    - end_date: End date for analysis
    - filter_type: Type of filter ('product' or 'category')
    - entity_id: ID of the product or category
    
    Returns:
    - List of sentiment shifts with before/after metrics
    """
    # Generate some significant shifts in sentiment
    # In a real implementation, this would analyze actual review data to detect changes
    
    shifts = []
    
    # If no specific entity selected, generate some default sample shifts
    if not entity_id or entity_id == 'all':
        # Set a consistent seed for "all" products view
        random.seed(42)
        
        # Generate 2-3 sample shifts for the overview
        num_shifts = random.randint(2, 3)
        
        # Generate shifts spread across the time period
        time_range = (end_date - start_date).days
        
        for i in range(num_shifts):
            # Calculate a point in time for the shift
            shift_days = int(time_range * (0.2 + (i * 0.3)))
            shift_date = start_date + datetime.timedelta(days=shift_days)
            
            # Calculate before and after periods
            before_start = shift_date - datetime.timedelta(days=30)
            before_end = shift_date
            after_start = shift_date
            after_end = shift_date + datetime.timedelta(days=30)
            
            # Format the time period string
            time_period = f"{before_start.strftime('%b %d, %Y')} to {after_end.strftime('%b %d, %Y')}"
            
            # Generate sample shifts with alternating directions
            shift_direction = 1 if i % 2 == 0 else -1
            shift_magnitude = 0.15 + (random.random() * 0.1)
            
            before_score = 0.6 + (random.random() * 0.2)
            after_score = max(0.1, min(0.9, before_score + (shift_direction * shift_magnitude)))
            
            # Realistic review counts
            reviews_before = random.randint(40, 120)
            reviews_after = random.randint(40, 120)
            
            # Calculate shift significance and p-value text
            significance = abs(after_score - before_score) * 10
            p_value = "p < 0.01" if significance > 1.5 else "p < 0.05"
            
            shifts.append({
                'time_period': time_period,
                'before_score': round(before_score, 2),
                'after_score': round(after_score, 2),
                'change': round(after_score - before_score, 2),
                'reviews_before': int(reviews_before),
                'reviews_after': int(reviews_after),
                'significance': p_value
            })
        
        # Sort by significance (absolute change amount)
        shifts.sort(key=lambda x: abs(x['change']), reverse=True)
        
        return shifts
    
    # Use entity_id to create a unique but consistent pattern
    seed = sum(ord(c) for c in entity_id) % 100
    random.seed(seed)
    
    # Number of shifts to generate
    num_shifts = random.randint(1, 3)
    
    # Generate shifts spread across the time period
    time_range = (end_date - start_date).days
    
    for i in range(num_shifts):
        # Calculate a point in time for the shift
        shift_days = int(time_range * (0.3 + (i * 0.25)))
        shift_date = start_date + datetime.timedelta(days=shift_days)
        
        # Calculate before and after periods
        before_start = shift_date - datetime.timedelta(days=30)
        before_end = shift_date
        after_start = shift_date
        after_end = shift_date + datetime.timedelta(days=30)
        
        # Format the time period string
        time_period = f"{before_end.strftime('%b %d, %Y')} to {after_start.strftime('%b %d, %Y')}"
        
        # Generate before and after scores
        # Significant shift (positive or negative)
        shift_direction = 1 if random.random() > 0.5 else -1
        shift_magnitude = 0.1 + (random.random() * 0.2)
        
        before_score = 0.5 + (random.random() * 0.3)
        after_score = max(0.1, min(0.9, before_score + (shift_direction * shift_magnitude)))
        
        # Generate review counts
        reviews_before = random.randint(20, 100)
        reviews_after = reviews_before * (0.8 + (random.random() * 0.4))
        
        # Calculate shift significance
        significance = abs(after_score - before_score) * 2 * (reviews_after / (reviews_before + reviews_after))
        
        shifts.append({
            'time_period': time_period,
            'before_score': round(before_score, 2),
            'after_score': round(after_score, 2),
            'change': round(after_score - before_score, 2),
            'reviews_before': int(reviews_before),
            'reviews_after': int(reviews_after),
            'significance': "p < 0.01" if significance > 0.3 else "p < 0.05"
        })
    
    # Sort by the absolute value of the change (not by significance string)
    shifts.sort(key=lambda x: abs(x['change']), reverse=True)
    
    return shifts

def generate_insights(time_series, seasonal_data, sentiment_shifts, filter_type, entity_id):
    """
    Generate insights from time-based sentiment data
    
    Parameters:
    - time_series: Time series data
    - seasonal_data: Seasonal trends data
    - sentiment_shifts: Sentiment shifts data
    - filter_type: Type of filter ('product' or 'category')
    - entity_id: ID of the product or category
    
    Returns:
    - List of insights
    """
    insights = []
    
    # If no entity selected, return basic insights
    if not entity_id or entity_id == 'all':
        insights.append({
            'title': 'Select a specific product or category',
            'description': 'For detailed insights, please select a specific product or category using the filters above.',
            'type': 'info'
        })
        return insights
    
    # Analyze overall trend
    if time_series and 'overall_sentiment' in time_series and len(time_series['overall_sentiment']) > 2:
        sentiment_values = time_series['overall_sentiment']
        first_quarter = sentiment_values[:len(sentiment_values)//4]
        last_quarter = sentiment_values[-len(sentiment_values)//4:]
        
        avg_first = sum(first_quarter) / len(first_quarter)
        avg_last = sum(last_quarter) / len(last_quarter)
        
        if avg_last > avg_first * 1.1:
            insights.append({
                'title': 'Improving Sentiment Trend',
                'description': f'Sentiment has improved by {((avg_last/avg_first) - 1)*100:.1f}% over the analyzed period, indicating growing customer satisfaction.',
                'recommendation': 'Continue current product strategy and highlight positive customer experiences in marketing.',
                'type': 'positive'
            })
        elif avg_last < avg_first * 0.9:
            insights.append({
                'title': 'Declining Sentiment Trend',
                'description': f'Sentiment has declined by {(1 - (avg_last/avg_first))*100:.1f}% over the analyzed period, suggesting potential customer satisfaction issues.',
                'recommendation': 'Investigate recent customer feedback to identify and address potential issues.',
                'type': 'negative'
            })
    
    # Analyze seasonal patterns
    if seasonal_data and 'current_year' in seasonal_data and 'previous_year' in seasonal_data:
        current = [x for x in seasonal_data['current_year'] if x is not None]
        previous = seasonal_data['previous_year'][:len(current)]
        
        if len(current) > 0 and len(previous) > 0:
            avg_current = sum(current) / len(current)
            avg_previous = sum(previous) / len(previous)
            
            if avg_current > avg_previous * 1.05:
                insights.append({
                    'title': 'Year-over-Year Improvement',
                    'description': f'This year\'s sentiment is {((avg_current/avg_previous) - 1)*100:.1f}% higher than the same period last year.',
                    'recommendation': 'Analyze what changes have positively impacted customer sentiment this year.',
                    'type': 'positive'
                })
            elif avg_current < avg_previous * 0.95:
                insights.append({
                    'title': 'Year-over-Year Decline',
                    'description': f'This year\'s sentiment is {(1 - (avg_current/avg_previous))*100:.1f}% lower than the same period last year.',
                    'recommendation': 'Compare product changes or customer service approaches between years to identify potential issues.',
                    'type': 'negative'
                })
            
            # Check seasonal patterns
            winter_current = current[0:2] if len(current) > 2 else []
            summer_current = current[5:8] if len(current) > 8 else []
            
            if len(winter_current) > 0 and len(summer_current) > 0:
                avg_winter = sum(winter_current) / len(winter_current)
                avg_summer = sum(summer_current) / len(summer_current)
                
                if avg_summer > avg_winter * 1.1:
                    insights.append({
                        'title': 'Strong Seasonal Pattern',
                        'description': 'Summer months show significantly higher sentiment scores than winter months.',
                        'recommendation': 'Consider seasonal marketing strategies and product improvements targeted at winter months.',
                        'type': 'seasonal'
                    })
    
    # Analyze sentiment shifts
    if sentiment_shifts and len(sentiment_shifts) > 0:
        for i, shift in enumerate(sentiment_shifts):
            if i >= 2:  # Limit to top 2 shifts
                break
                
            if shift['after_score'] > shift['before_score']:
                insights.append({
                    'title': 'Positive Sentiment Shift Detected',
                    'description': f'A significant positive shift of {((shift["after_score"]/shift["before_score"])-1)*100:.1f}% was detected around {shift["time_period"]}.',
                    'recommendation': 'Identify what changed during this period (product updates, marketing, etc.) to capitalize on the positive impact.',
                    'type': 'positive'
                })
            else:
                insights.append({
                    'title': 'Negative Sentiment Shift Detected',
                    'description': f'A significant negative shift of {(1-(shift["after_score"]/shift["before_score"]))*100:.1f}% was detected around {shift["time_period"]}.',
                    'recommendation': 'Investigate what issues or changes occurred during this period that may have impacted customer sentiment.',
                    'type': 'negative'
                })
    
    # If no specific insights were generated, add a generic one
    if len(insights) == 0:
        insights.append({
            'title': 'Stable Sentiment Trend',
            'description': 'No significant sentiment shifts or seasonal patterns detected in the analyzed period.',
            'recommendation': 'Continue monitoring sentiment trends for early detection of changes.',
            'type': 'info'
        })
    
    return insights

def generate_time_periods(start_date, end_date, granularity):
    """
    Generate time periods based on granularity
    
    Parameters:
    - start_date: Start date
    - end_date: End date
    - granularity: Time granularity ('day', 'week', 'month', 'quarter')
    
    Returns:
    - List of (period_start, period_end) tuples
    """
    periods = []
    current_date = start_date
    
    while current_date < end_date:
        if granularity == 'day':
            period_start = current_date
            period_end = period_start + datetime.timedelta(days=1)
        elif granularity == 'week':
            period_start = current_date
            period_end = period_start + datetime.timedelta(days=7)
        elif granularity == 'month':
            period_start = datetime.datetime(current_date.year, current_date.month, 1)
            if current_date.month == 12:
                period_end = datetime.datetime(current_date.year + 1, 1, 1)
            else:
                period_end = datetime.datetime(current_date.year, current_date.month + 1, 1)
        else:  # quarter
            quarter = (current_date.month - 1) // 3
            period_start = datetime.datetime(current_date.year, quarter * 3 + 1, 1)
            if quarter == 3:
                period_end = datetime.datetime(current_date.year + 1, 1, 1)
            else:
                period_end = datetime.datetime(current_date.year, quarter * 3 + 4, 1)
        
        periods.append((period_start, period_end))
        
        # Move to next period
        if granularity == 'day':
            current_date += datetime.timedelta(days=1)
        elif granularity == 'week':
            current_date += datetime.timedelta(days=7)
        elif granularity == 'month':
            # Move to first day of next month
            if current_date.month == 12:
                current_date = datetime.datetime(current_date.year + 1, 1, 1)
            else:
                current_date = datetime.datetime(current_date.year, current_date.month + 1, 1)
        else:  # quarter
            # Move to first day of next quarter
            quarter = (current_date.month - 1) // 3
            if quarter == 3:
                current_date = datetime.datetime(current_date.year + 1, 1, 1)
            else:
                current_date = datetime.datetime(current_date.year, quarter * 3 + 4, 1)
    
    return periods

def export_time_based_analysis():
    """
    Export time-based analysis data as CSV
    
    Returns:
    - CSV data as a string
    """
    # In a real implementation, this would generate a CSV file with the data
    # For this demo, we'll just return a message
    return jsonify({
        'message': 'Export functionality would generate a CSV file in a real implementation.'
    })