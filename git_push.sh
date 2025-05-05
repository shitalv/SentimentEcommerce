#!/bin/bash
# Script to push changes to Git

# Configure Git with project information
git config --global user.name "Sentiment Analysis Platform"
git config --global user.email "dev@sentiment-platform.example.com"

# Add the modified files
git add mongo_config.py direct_mongo_app.py templates/admin/reports/time_based_analysis_api.py git_changes_summary.txt

# Commit the changes
git commit -m "Fix MongoDB connection by replacing environment variables with direct credentials"

# Push to the repository
# Note: You might need to set up authentication for this to work
git push

echo "Git operations completed"