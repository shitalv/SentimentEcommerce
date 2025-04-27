# MongoDB Integration & Data Cleaning Files

This folder contains files for MongoDB integration, Amazon review import, and data cleaning:

1. `mongo_config.py` - MongoDB connection configuration
2. `test_mongo_connection.py` - Test script for MongoDB connection
3. `fix_mongo_connection.py` - Script to fix MongoDB connection
4. `import_amazon_reviews_mongo.py` - Full Amazon review import script
5. `quick_import.py` - Quick import script for testing
6. `check_mongo_data.py` - Data verification script
7. `enhanced_import.py` - Enhanced data import with cleaning and normalization
8. `fix_product_data.py` - Fix null/undefined values in products
9. `create_diverse_products.py` - Create diverse product examples

## How to Use

1. Copy these files to your project root directory
2. Fix any MongoDB connection issues:
   ```
   python fix_mongo_connection.py
   ```
3. Import and clean product data:
   ```
   python enhanced_import.py [limit]
   ```
4. Create diverse product examples:
   ```
   python create_diverse_products.py
   ```
5. Verify data quality:
   ```
   python check_mongo_data.py
   ```

## Data Cleaning Features

- Fixes null categories and undefined values
- Normalizes product names
- Generates appropriate prices based on categories 
- Adds sentiment analysis to all reviews
- Ensures product-review relationships are maintained
- Follows ML workflow best practices: import → analyze/clean → use
