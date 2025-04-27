# MongoDB Integration Files

This folder contains files for MongoDB integration and Amazon review import:

1. `mongo_config.py` - MongoDB connection configuration
2. `test_mongo_connection.py` - Test script for MongoDB connection
3. `fix_mongo_connection.py` - Script to fix MongoDB connection
4. `import_amazon_reviews_mongo.py` - Full Amazon review import script
5. `quick_import.py` - Quick import script for testing
6. `check_mongo_data.py` - Data verification script

## How to Use

1. Copy these files to your project root directory
2. Run the import script:
   ```
   python import_amazon_reviews_mongo.py path/to/amazon_reviews.csv [limit]
   ```
3. Or use quick import for testing:
   ```
   python quick_import.py
   ```
4. Verify data import:
   ```
   python check_mongo_data.py
   ```
