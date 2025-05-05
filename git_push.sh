#!/bin/bash
# Script to push changes to Git

# Configure Git (adjust with your information)
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Add the modified files
git add mongo_config.py templates/admin/reports/time_based_analysis_api.py git_changes_summary.txt

# Commit the changes
git commit -m "Remove sample data fallbacks and improve MongoDB error handling"

# Push to the repository
# Note: You might need to set up authentication for this to work
git push

echo "Git operations completed"