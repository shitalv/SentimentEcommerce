"""
Check Dataset Products

This script analyzes the Amazon review dataset to count the number of unique products
and display product information to help with selective importing.
"""

import pandas as pd
import os
import sys
import logging
from collections import defaultdict

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('dataset_analyzer')

def analyze_dataset(file_path):
    """Analyze the dataset to count unique products and categories"""
    try:
        logger.info(f"Reading CSV file: {file_path}")
        
        # Read with pandas
        df = pd.read_csv(file_path, low_memory=False)
        logger.info(f"Loaded {len(df)} rows from CSV")
        
        # Count unique products by ASIN
        unique_asins = df['asins'].nunique()
        logger.info(f"Number of unique ASINs in dataset: {unique_asins}")
        
        # Count unique products by name
        unique_names = df['name'].nunique()
        logger.info(f"Number of unique product names in dataset: {unique_names}")
        
        # Get top categories
        categories = defaultdict(int)
        primary_categories = defaultdict(int)
        
        for category in df['categories'].dropna():
            for cat in str(category).split(','):
                cat = cat.strip()
                if cat:
                    categories[cat] += 1
        
        for category in df['primaryCategories'].dropna():
            category = str(category).strip()
            if category:
                primary_categories[category] += 1
        
        # Print top categories
        logger.info("Top 10 primary categories:")
        for cat, count in sorted(primary_categories.items(), key=lambda x: x[1], reverse=True)[:10]:
            logger.info(f"  {cat}: {count}")
        
        # Generate a sample of products with different ASINs
        sample_products = df.drop_duplicates('asins').head(20)
        
        logger.info("\nSample products available for import:")
        for idx, row in sample_products.iterrows():
            logger.info(f"ASIN: {row.get('asins')} | Name: {row.get('name')} | Category: {row.get('primaryCategories')}")
        
        # Return key statistics
        return {
            "total_rows": len(df),
            "unique_asins": unique_asins,
            "unique_names": unique_names,
            "top_categories": list(sorted(primary_categories.items(), key=lambda x: x[1], reverse=True)[:10]),
            "sample_products": sample_products.to_dict('records')
        }
        
    except Exception as e:
        logger.error(f"Error analyzing dataset: {str(e)}")
        return None

if __name__ == "__main__":
    dataset_path = "attached_assets/Datafiniti_Amazon_Consumer_Reviews_of_Amazon_Products.csv"
    
    if not os.path.isfile(dataset_path):
        logger.error(f"Dataset file not found: {dataset_path}")
        sys.exit(1)
    
    result = analyze_dataset(dataset_path)
    
    if result:
        logger.info("\nDataset Analysis Summary:")
        logger.info(f"Total rows: {result['total_rows']}")
        logger.info(f"Unique ASINs: {result['unique_asins']}")
        logger.info(f"Unique product names: {result['unique_names']}")
        
        logger.info("\nRecommendation: Modify import_amazon_reviews_mongo.py to increase import limit")
        logger.info("Current script is importing a very limited number of products")