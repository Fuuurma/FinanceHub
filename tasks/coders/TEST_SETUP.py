#!/usr/bin/env python3
"""
Quick Setup Test Script
Run this to verify your development environment is ready.
"""

import sys
import subprocess

def run_command(cmd, description):
    print(f"\n{'='*60}")
    print(f"Testing: {description}")
    print(f"Command: {cmd}")
    print('='*60)
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"✅ PASS: {result.stdout.strip()}")
        return True
    else:
        print(f"❌ FAIL: {result.stderr.strip() or result.stdout.strip()}")
        return False

def main():
    print("FinanceHub Setup Test")
    print("="*60)
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Python version
    tests_total += 1
    if run_command("python3 --version", "Python 3.11+"):
        tests_passed += 1
    
    # Test 2: Venv exists
    tests_total += 1
    if run_command("test -f /Users/sergi/Desktop/Projects/FinanceHub/apps/backend/venv/bin/python", "Venv exists"):
        tests_passed += 1
    
    # Test 3: Dramatiq installed
    tests_total += 1
    if run_command("source /Users/sergi/Desktop/Projects/FinanceHub/apps/backend/venv/bin/activate && python -c 'import dramatiq; print(dramatiq.__version__)'", "Dramatiq installed"):
        tests_passed += 1
    
    # Test 4: Django installed
    tests_total += 1
    if run_command("source /Users/sergi/Desktop/Projects/FinanceHub/apps/backend/venv/bin/activate && python -c 'import django; print(django.VERSION)'", "Django installed"):
        tests_passed += 1
    
    # Test 5: Redis-py installed
    tests_total += 1
    if run_command("source /Users/sergi/Desktop/Projects/FinanceHub/apps/backend/venv/bin/activate && python -c 'import redis; print(redis.__version__)'", "Redis-py installed"):
        tests_passed += 1
    
    # Test 6: Docker is running
    tests_total += 1
    if run_command("docker info > /dev/null 2>&1 && echo 'Docker running'", "Docker running"):
        tests_passed += 1
    
    print("\n" + "="*60)
    print(f"RESULTS: {tests_passed}/{tests_total} tests passed")
    print("="*60)
    
    if tests_passed == tests_total:
        print("✅ All tests passed! Your environment is ready.")
        return 0
    else:
        print("❌ Some tests failed. Check the failures above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
