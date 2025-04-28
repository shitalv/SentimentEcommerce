"""
Test Runner

This script runs all tests in the tests directory.
"""

import unittest
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.abspath('.'))

if __name__ == '__main__':
    # Discover and run all tests
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('tests', pattern='test_*.py')
    
    # Run the tests
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    
    # Exit with appropriate code
    sys.exit(not result.wasSuccessful())