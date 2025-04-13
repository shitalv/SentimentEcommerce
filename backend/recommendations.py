"""
Product Recommendation Engine based on Sentiment Analysis

This module provides functions to recommend products based on:
1. Sentiment scores - recommending products with high positive sentiment
2. Category similarity - products in the same category
3. Keyword similarity - products that share similar positive keywords
4. User preferences - based on previously viewed or favorited products
"""

import logging
import re
from collections import Counter
from models import Product, Review
from backend.sentiment_analyzer import analyze_sentiment, classify_sentiment

logger = logging.getLogger(__name__)

def get_recommendations_for_product(product_id, limit=3):
    """
    Get product recommendations based on the specified product
    
    Args:
        product_id: The ID of the product to find recommendations for
        limit: Maximum number of recommendations to return
        
    Returns:
        List of recommended product objects
    """
    try:
        # Get the base product
        base_product = Product.query.get(product_id)
        
        if not base_product:
            logger.warning(f"Cannot recommend products: Product {product_id} not found")
            return []
            
        # Get all other products (excluding the current one)
        all_other_products = Product.query.filter(Product.id != product_id).all()
        
        if not all_other_products:
            logger.warning("No other products available for recommendations")
            return []
            
        # Initialize scoring for each product
        product_scores = {}
        for product in all_other_products:
            # Base score is 0
            product_scores[product.id] = 0
            
        # 1. Score based on sentiment (products with high positive sentiment scores)
        for product in all_other_products:
            # Sentiment score 0-1, where 1 is most positive
            sentiment_score = (product.positive_score * 1.0) + (product.neutral_score * 0.5)
            
            # Scale the sentiment score to have more impact (0-5 range)
            product_scores[product.id] += sentiment_score * 5
            
        # 2. Score based on category match
        for product in all_other_products:
            # Same category gets a bonus
            if product.category == base_product.category:
                product_scores[product.id] += 3
            # Similar category (e.g., "Electronics" matches "Electronic Devices")
            elif base_product.category and product.category and \
                 (base_product.category.lower() in product.category.lower() or 
                  product.category.lower() in base_product.category.lower()):
                product_scores[product.id] += 1.5
                
        # 3. Score based on price similarity
        if base_product.price:
            for product in all_other_products:
                if product.price:
                    # Similar price range (within 20% difference)
                    price_diff_pct = abs(product.price - base_product.price) / max(base_product.price, 1)
                    if price_diff_pct < 0.2:
                        product_scores[product.id] += 2
                    elif price_diff_pct < 0.5:
                        product_scores[product.id] += 1
        
        # 4. Get features from reviews
        base_product_features = extract_product_features(base_product)
        
        # Score based on feature similarity
        for product in all_other_products:
            product_features = extract_product_features(product)
            
            # Get common features
            common_features = set(base_product_features).intersection(set(product_features))
            
            # Score based on feature overlap (each common feature adds 1 point)
            feature_score = len(common_features) * 0.5
            product_scores[product.id] += feature_score
        
        # Sort products by score (highest to lowest)
        sorted_product_ids = sorted(
            product_scores.keys(), 
            key=lambda pid: product_scores[pid], 
            reverse=True
        )
        
        # Get the top N recommended products
        recommended_products = []
        for pid in sorted_product_ids[:limit]:
            product = Product.query.get(pid)
            if product:
                recommended_products.append(product)
                
        logger.info(f"Generated {len(recommended_products)} recommendations for product {product_id}")
        return recommended_products
        
    except Exception as e:
        logger.error(f"Error generating recommendations: {str(e)}")
        return []

def extract_product_features(product):
    """
    Extract product features from reviews and description
    
    Args:
        product: Product object with reviews
        
    Returns:
        List of extracted features
    """
    features = []
    
    # Extract features from product description
    if product.description:
        # Extract adjectives and nouns using simple pattern matching
        # In a real implementation, you might use NLP tools like spaCy
        desc_words = re.findall(r'\b\w+\b', product.description.lower())
        features.extend(desc_words)
    
    # Extract features from positive reviews
    reviews = Review.query.filter_by(product_id=product.id).all()
    
    for review in reviews:
        if review.sentiment_class == 'positive':
            # Extract words from positive reviews
            if review.text:
                review_words = re.findall(r'\b\w+\b', review.text.lower())
                features.extend(review_words)
            
            # Extract keywords from sentiment analysis
            if review.sentiment_keywords:
                try:
                    import json
                    keywords = json.loads(review.sentiment_keywords)
                    for kw in keywords:
                        if isinstance(kw, dict) and 'keyword' in kw:
                            features.append(kw['keyword'].lower())
                except Exception:
                    pass
    
    # Count frequency and keep top features
    counter = Counter(features)
    # Filter out common stop words and very short words
    filtered_features = [
        word for word, count in counter.most_common(20) 
        if len(word) > 3 and word not in STOP_WORDS
    ]
    
    return filtered_features

def get_top_rated_products(category=None, limit=5):
    """
    Get top-rated products by sentiment score
    
    Args:
        category: Optional category to filter by
        limit: Maximum number of products to return
        
    Returns:
        List of top-rated product objects
    """
    try:
        # Query base
        query = Product.query
        
        # Apply category filter if specified
        if category:
            query = query.filter_by(category=category)
        
        # Order by positive sentiment
        query = query.order_by(Product.positive_score.desc())
        
        # Get top N products
        products = query.limit(limit).all()
        
        return products
    except Exception as e:
        logger.error(f"Error getting top-rated products: {str(e)}")
        return []

# Common English stop words to filter out
STOP_WORDS = {
    'a', 'an', 'the', 'and', 'or', 'but', 'if', 'then', 'else', 'when', 'at', 'from', 
    'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 
    'before', 'after', 'above', 'below', 'to', 'of', 'in', 'on', 'so', 'than', 'that', 
    'this', 'these', 'those', 'there', 'here', 'which', 'what', 'who', 'whom', 'whose', 
    'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'some', 'such', 
    'no', 'nor', 'not', 'only', 'own', 'same', 'too', 'very', 'can', 'will', 'just', 
    'should', 'now', 'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 
    'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 
    'her', 'hers', 'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 
    'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am', 
    'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 
    'do', 'does', 'did', 'doing', 'would', 'should', 'could', 'ought', 'i\'m', 'you\'re', 
    'he\'s', 'she\'s', 'it\'s', 'we\'re', 'they\'re', 'i\'ve', 'you\'ve', 'we\'ve', 
    'they\'ve', 'i\'d', 'you\'d', 'he\'d', 'she\'d', 'we\'d', 'they\'d', 'i\'ll', 'you\'ll', 
    'he\'ll', 'she\'ll', 'we\'ll', 'they\'ll', 'isn\'t', 'aren\'t', 'wasn\'t', 'weren\'t', 
    'hasn\'t', 'haven\'t', 'hadn\'t', 'doesn\'t', 'don\'t', 'didn\'t', 'won\'t', 'wouldn\'t', 
    'shan\'t', 'shouldn\'t', 'can\'t', 'cannot', 'couldn\'t', 'mustn\'t', 'let\'s', 'that\'s', 
    'who\'s', 'what\'s', 'here\'s', 'there\'s', 'when\'s', 'where\'s', 'why\'s', 'how\'s'
}