import logging
from models import Product

logger = logging.getLogger(__name__)

def search_products(query=None, category=None, min_sentiment=None, max_sentiment=None):
    """
    Search for products with filters
    """
    try:
        # Start with base query
        product_query = Product.query
        
        # Apply filters
        if query:
            product_query = product_query.filter(
                Product.name.ilike(f'%{query}%') | 
                Product.description.ilike(f'%{query}%')
            )
        
        if category:
            product_query = product_query.filter(Product.category == category)
        
        if min_sentiment is not None:
            # For min sentiment, we want products with positive + (neutral * 0.5) >= min_sentiment
            product_query = product_query.filter(
                (Product.positive_score + (Product.neutral_score * 0.5)) >= min_sentiment
            )
        
        if max_sentiment is not None:
            # For max sentiment, we want products with positive + (neutral * 0.5) <= max_sentiment
            product_query = product_query.filter(
                (Product.positive_score + (Product.neutral_score * 0.5)) <= max_sentiment
            )
        
        # Execute query
        products = product_query.all()
        
        # Convert to dictionaries
        result = []
        for product in products:
            product_dict = {
                "id": product.id,
                "asin": product.asin,
                "name": product.name,
                "price": product.price,
                "category": product.category,
                "description": product.description,
                "image_url": product.image_url,
                "sentiment_score": (product.positive_score * 1.0) + (product.neutral_score * 0.5),
            }
            result.append(product_dict)
        
        return result
    except Exception as e:
        logger.error(f"Error searching products: {str(e)}")
        return []