#!/usr/bin/env python3
"""
SuperMean System Test Runner

This script discovers and runs all tests across the SuperMean system components.
It provides a comprehensive test suite execution with detailed reporting.
"""

import os
import sys
import unittest
import time
import argparse
from typing import List, Dict, Any

# Add the parent directory to the Python path for proper imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)


def discover_tests(start_dir: str = '.', pattern: str = '*_test.py') -> unittest.TestSuite:
    """
    Discover all test files in the project directories.
    
    Args:
        start_dir: The starting directory for test discovery
        pattern: The pattern to match test files
        
    Returns:
        A test suite containing all discovered tests
    """
    if not os.path.exists(start_dir):
        print(f"Warning: Start directory '{start_dir}' does not exist")
        return unittest.TestSuite()
        
    loader = unittest.TestLoader()
    try:
        suite = loader.discover(start_dir, pattern=pattern)
        return suite
    except Exception as e:
        print(f"Error discovering tests in {start_dir}: {e}")
        return unittest.TestSuite()


def run_tests(suite: unittest.TestSuite) -> unittest.TestResult:
    """
    Run the test suite and return the results.
    
    Args:
        suite: The test suite to run
        
    Returns:
        The test results
    """
    runner = unittest.TextTestRunner(verbosity=2)
    return runner.run(suite)


def generate_report(result: unittest.TestResult) -> Dict[str, Any]:
    """
    Generate a report from the test results.
    
    Args:
        result: The test results
        
    Returns:
        A dictionary containing the test report
    """
    report = {
        "total": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "skipped": len(result.skipped),
        "success": result.wasSuccessful(),
        "details": {
            "failures": result.failures,
            "errors": result.errors,
            "skipped": result.skipped
        }
    }
    return report


def print_report(report: Dict[str, Any]) -> None:
    """
    Print a formatted test report.
    
    Args:
        report: The test report dictionary
    """
    print("\n" + "=" * 80)
    print(f"TEST SUMMARY")
    print("=" * 80)
    print(f"Total tests run: {report['total']}")
    print(f"Failures: {report['failures']}")
    print(f"Errors: {report['errors']}")
    print(f"Skipped: {report['skipped']}")
    print(f"Success: {'Yes' if report['success'] else 'No'}")
    
    if report['failures'] > 0:
        print("\n" + "-" * 80)
        print("FAILURES:")
        print("-" * 80)
        for i, (test, traceback) in enumerate(report['details']['failures'], 1):
            print(f"\n{i}. {test}")
            print(f"Traceback: {traceback}\n")
    
    if report['errors'] > 0:
        print("\n" + "-" * 80)
        print("ERRORS:")
        print("-" * 80)
        for i, (test, traceback) in enumerate(report['details']['errors'], 1):
            print(f"\n{i}. {test}")
            print(f"Traceback: {traceback}\n")


def run_specific_modules(modules: List[str]) -> unittest.TestResult:
    """
    Run tests for specific modules.
    
    Args:
        modules: List of module names to test
        
    Returns:
        The test results
    """
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    
    for module in modules:
        try:
            # Try to find tests in the specified module directory
            module_path = os.path.join(os.getcwd(), module)
            if os.path.exists(module_path):
                module_suite = loader.discover(module_path, pattern="*_test.py")
                suite.addTest(module_suite)
            else:
                print(f"Warning: Module directory '{module}' not found")
        except Exception as e:
            print(f"Error processing module {module}: {e}")
    
    return run_tests(suite)


def main():
    """
    Main function to parse arguments and run tests.
    """
    parser = argparse.ArgumentParser(description="SuperMean System Test Runner")
    parser.add_argument(
        "--modules", 
        nargs="+", 
        help="Specific modules to test (e.g., agents memory super_agent)"
    )
    parser.add_argument(
        "--verbose", 
        action="store_true", 
        help="Enable verbose output"
    )
    parser.add_argument(
        "--pattern",
        default="*_test.py",
        help="Pattern to match test files (default: *_test.py)"
    )
    
    args = parser.parse_args()
    
    start_time = time.time()
    
    if args.verbose:
        print("SuperMean Test Runner")
        print("=" * 80)
        print(f"Current directory: {os.getcwd()}")
        print(f"Test pattern: {args.pattern}")
    
    try:
        if args.modules:
            if args.verbose:
                print(f"Running tests for modules: {', '.join(args.modules)}")
            result = run_specific_modules(args.modules)
        else:
            if args.verbose:
                print("Running all tests")
            suite = discover_tests('.')
            result = run_tests(suite)
        
        report = generate_report(result)
        print_report(report)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\nTest run completed in {duration:.2f} seconds")
        
        # Return non-zero exit code if tests failed
        return 0 if report["success"] else 1
    except Exception as e:
        print(f"Error running tests: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())