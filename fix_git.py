"""
Script to diagnose and potentially fix Git issues
"""

import os
import subprocess
import shutil
from datetime import datetime

def check_git_status():
    """Check the status of the Git repository"""
    print("Checking Git repository status...")
    try:
        # Create backup of problematic .git folder
        git_dir = os.path.join(os.getcwd(), ".git")
        backup_dir = os.path.join(os.getcwd(), f".git_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        
        if os.path.exists(git_dir):
            print(f"Git directory exists at: {git_dir}")
            
            # List files in .git directory
            print("\nFiles in .git directory:")
            for root, dirs, files in os.walk(git_dir):
                level = root.replace(git_dir, '').count(os.sep)
                indent = ' ' * 4 * level
                print(f"{indent}{os.path.basename(root)}/")
                sub_indent = ' ' * 4 * (level + 1)
                for f in files:
                    print(f"{sub_indent}{f}")
            
            # Check for lock files
            lock_files = []
            for root, dirs, files in os.walk(git_dir):
                for file in files:
                    if file.endswith('.lock'):
                        lock_path = os.path.join(root, file)
                        lock_files.append(lock_path)
            
            if lock_files:
                print("\nLock files found:")
                for lock_file in lock_files:
                    print(f"  - {lock_file}")
                    # Try to remove lock files
                    try:
                        os.remove(lock_file)
                        print(f"Successfully removed lock file: {lock_file}")
                    except Exception as e:
                        print(f"Failed to remove lock file {lock_file}: {str(e)}")
            else:
                print("\nNo lock files found.")
            
            # Print config information
            config_path = os.path.join(git_dir, "config")
            if os.path.exists(config_path):
                print("\nGit config contents:")
                with open(config_path, 'r') as f:
                    print(f.read())
            
            # Check if repo is in a detached HEAD state
            head_path = os.path.join(git_dir, "HEAD")
            if os.path.exists(head_path):
                with open(head_path, 'r') as f:
                    head_content = f.read().strip()
                    print(f"\nHEAD contents: {head_content}")
                    if not head_content.startswith("ref:"):
                        print("Repository appears to be in a detached HEAD state.")
            
            # Create a log file with diagnostics
            log_path = os.path.join(os.getcwd(), "git_diagnostics.log")
            with open(log_path, 'w') as log_file:
                log_file.write(f"Git diagnostics run at: {datetime.now()}\n\n")
                log_file.write(f"Git directory: {git_dir}\n")
                
                if lock_files:
                    log_file.write("\nLock files found:\n")
                    for lock_file in lock_files:
                        log_file.write(f"  - {lock_file}\n")
                else:
                    log_file.write("\nNo lock files found.\n")
                
                if os.path.exists(config_path):
                    log_file.write("\nGit config contents:\n")
                    with open(config_path, 'r') as f:
                        log_file.write(f.read())
                
                if os.path.exists(head_path):
                    with open(head_path, 'r') as f:
                        head_content = f.read().strip()
                        log_file.write(f"\nHEAD contents: {head_content}\n")
            
            print(f"\nDiagnostics log written to: {log_path}")
            
        else:
            print(f"Git directory not found at: {git_dir}")
        
    except Exception as e:
        print(f"Error checking Git status: {str(e)}")

if __name__ == "__main__":
    check_git_status()