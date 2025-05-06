#!/bin/bash

# Create backup directory
BACKUP_DIR="time_analysis_fix_backup"
mkdir -p $BACKUP_DIR

# Copy the fixed file to backup
cp templates/admin/reports/time_based_analysis_api.py $BACKUP_DIR/

# Create a summary file
cat > $BACKUP_DIR/README.txt << EOF
Time-Based Analysis API Fix Summary
==================================

Date: $(date)

Fixed Issue:
- The time-based analysis API was failing because it was trying to convert product_id string to MongoDB ObjectId format
- Reviews in the database store product_ids as strings, causing a mismatch

Changes Made:
1. Modified get_time_series_data to use string format for product_id
2. Modified get_seasonal_trends to use string format for product_id
3. Modified get_monthly_distribution to use string format for product_id
4. Modified get_sentiment_shifts to use string format for product_id

These changes ensure the time-based analysis graphs now properly display data when a specific product is selected.
EOF

# Create a tar archive
tar -czf time_analysis_fix.tar.gz $BACKUP_DIR

echo "Backup created: time_analysis_fix.tar.gz"
echo "This file contains the fixed time-based analysis API code"