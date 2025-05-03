"""
Sentiment Trends Module

This module provides functionality for tracking and analyzing sentiment trends over time.
It allows users to see how product sentiment has evolved, identifying patterns and changes
in customer satisfaction.
"""

import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from mongo_config import get_db, mongo

logger = logging.getLogger(__name__)

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
        # Get database connection
        db = get_db()
        if not db:
            logger.error("Failed to connect to database")
            return []
            
        # Build matching criteria
        match_criteria = {}
        if product_id:
            match_criteria["product_id"] = product_id
            
        # Ensure we only analyze reviews with dates
        match_criteria["date"] = {"$ne": None}
        
        # Get all reviews matching criteria
        reviews_collection = db.reviews
        reviews = list(reviews_collection.find(match_criteria))
        
        # If no reviews found, return empty results
        if not reviews:
            logger.info(f"No reviews found for criteria: {match_criteria}")
            return []
            
        # Create a pandas DataFrame for easier time-based analysis
        review_data = []
        for review in reviews:
            # Extract sentiment info
            sentiment_class = review.get("sentiment_class", "neutral")
            sentiment_score = review.get("sentiment_score", 0.5)
            review_date = review.get("date")
            
            # Skip reviews without date
            if not review_date:
                continue
                
            # Ensure date is datetime
            if isinstance(review_date, str):
                try:
                    review_date = datetime.fromisoformat(review_date.replace('Z', '+00:00'))
                except ValueError:
                    try:
                        review_date = datetime.strptime(review_date, "%Y-%m-%d")
                    except ValueError:
                        logger.warning(f"Could not parse date: {review_date}")
                        continue
            
            # Append data point
            review_data.append({
                "date": review_date,
                "sentiment_score": sentiment_score,
                "sentiment_class": sentiment_class,
                "is_positive": 1 if sentiment_class == "positive" else 0,
                "is_neutral": 1 if sentiment_class == "neutral" else 0,
                "is_negative": 1 if sentiment_class == "negative" else 0,
            })
            
        # Create DataFrame
        if not review_data:
            logger.info("No valid reviews with dates found")
            return []
            
        df = pd.DataFrame(review_data)
        
        # Set appropriate time frequency based on time_range
        if time_range == "day":
            freq = "D"
            date_format = "%Y-%m-%d"
            period_name = "day"
        elif time_range == "week":
            freq = "W-MON"  # Week starting on Monday
            date_format = "%Y-%m-%d"
            period_name = "week"
        else:  # Default to month
            freq = "MS"  # Month start
            date_format = "%Y-%m"
            period_name = "month"
            
        # Group by time period
        df["period"] = df["date"].dt.to_period(freq)
        
        # Get summary statistics for each period
        period_stats = df.groupby("period").agg({
            "sentiment_score": ["mean", "count"],
            "is_positive": "sum",
            "is_neutral": "sum", 
            "is_negative": "sum"
        }).reset_index()
        
        # Flatten multi-level columns
        period_stats.columns = [
            "period" if col[0] == "period" else f"{col[0]}_{col[1]}"
            for col in period_stats.columns
        ]
        
        # Calculate percentages
        period_stats["positive_percent"] = round(
            (period_stats["is_positive_sum"] / period_stats["sentiment_score_count"]) * 100, 1
        )
        period_stats["neutral_percent"] = round(
            (period_stats["is_neutral_sum"] / period_stats["sentiment_score_count"]) * 100, 1
        )
        period_stats["negative_percent"] = round(
            (period_stats["is_negative_sum"] / period_stats["sentiment_score_count"]) * 100, 1
        )
        
        # Sort by period and limit results
        period_stats = period_stats.sort_values("period", ascending=False).head(limit)
        
        # Convert to list of dictionaries
        result = []
        for _, row in period_stats.iterrows():
            period_start = row["period"].start_time
            period_label = period_start.strftime(date_format)
            
            result.append({
                "period": period_label,
                "period_name": period_name,
                "review_count": int(row["sentiment_score_count"]),
                "average_score": float(row["sentiment_score_mean"]),
                "positive_count": int(row["is_positive_sum"]),
                "neutral_count": int(row["is_neutral_sum"]),
                "negative_count": int(row["is_negative_sum"]),
                "positive_percent": float(row["positive_percent"]),
                "neutral_percent": float(row["neutral_percent"]),
                "negative_percent": float(row["negative_percent"]),
            })
            
        return result
        
    except Exception as e:
        logger.error(f"Error aggregating sentiment by time: {e}")
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
        # Get monthly data for the past year
        monthly_data = aggregate_sentiment_by_time(
            product_id=product_id, 
            time_range="month", 
            limit=12
        )
        
        if not monthly_data or len(monthly_data) < 2:
            return {
                "trend": "stable",
                "trend_direction": 0,
                "trend_percent": 0,
                "insufficient_data": True,
                "periods_analyzed": len(monthly_data) if monthly_data else 0
            }
            
        # Calculate trend between most recent two months
        current = monthly_data[0]
        previous = monthly_data[1]
        
        current_score = current["average_score"]
        previous_score = previous["average_score"]
        
        # Calculate change
        score_change = current_score - previous_score
        percent_change = round((score_change / max(0.1, previous_score)) * 100, 1)
        
        # Determine trend direction and description
        if abs(percent_change) < 5:
            trend = "stable"
            trend_direction = 0
        elif percent_change > 0:
            trend = "improving"
            trend_direction = 1
        else:
            trend = "declining"
            trend_direction = -1
            
        return {
            "trend": trend,
            "trend_direction": trend_direction,
            "trend_percent": percent_change,
            "current_period": current["period"],
            "previous_period": previous["period"],
            "current_score": current_score,
            "previous_score": previous_score,
            "insufficient_data": False,
            "periods_analyzed": len(monthly_data)
        }
        
    except Exception as e:
        logger.error(f"Error getting sentiment trend metrics: {e}")
        return {
            "trend": "unknown",
            "trend_direction": 0,
            "trend_percent": 0,
            "error": str(e),
            "insufficient_data": True
        }