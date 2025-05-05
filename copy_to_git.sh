#!/bin/bash
# Script to copy the modified files to a directory for later git operations

# Create a directory to store files for git
COPY_DIR="code_export"
mkdir -p "$COPY_DIR"

# Copy the modified files
echo "Copying modified files to $COPY_DIR..."
cp mongo_config.py "$COPY_DIR/"
cp direct_mongo_app.py "$COPY_DIR/"
cp git_changes_summary.txt "$COPY_DIR/"

# Check if templates directory exists in the code_export
if [ ! -d "$COPY_DIR/templates/admin/reports" ]; then
    mkdir -p "$COPY_DIR/templates/admin/reports"
fi

# Copy template files if they exist
if [ -f "templates/admin/reports/time_based_analysis_api.py" ]; then
    cp "templates/admin/reports/time_based_analysis_api.py" "$COPY_DIR/templates/admin/reports/"
    echo "Copied time_based_analysis_api.py"
else
    echo "Warning: templates/admin/reports/time_based_analysis_api.py not found"
fi

echo ""
echo "Files have been copied to the $COPY_DIR directory."
echo "You can manually copy these files to your local repository and commit them."
echo ""
echo "Files copied:"
find "$COPY_DIR" -type f | sort

echo ""
echo "Done!"