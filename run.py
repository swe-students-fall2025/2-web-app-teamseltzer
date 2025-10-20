#!/usr/bin/env python3
"""
Run script for SeltzerTracker Flask application
"""

import os
import sys
import subprocess

def check_mongodb():
    """Check if MongoDB is running"""
    try:
        import pymongo
        from pymongo import MongoClient
        client = MongoClient('mongodb://localhost:27017/')
        client.admin.command('ping')
        print("✅ MongoDB is running")
        return True
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        print("   Please start MongoDB: mongod")
        return False

def check_dependencies():
    """Check if all dependencies are installed"""
    try:
        import flask
        import pymongo
        import flask_login
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("   Run: pip3 install -r requirements.txt")
        return False

def check_env_file():
    """Check if .env file exists"""
    if os.path.exists('.env'):
        print("✅ .env file found")
        return True
    else:
        print("❌ .env file not found")
        print("   Run: cp env.example .env")
        print("   Then edit .env with your MongoDB credentials")
        return False

def main():
    print("🚀 Starting SeltzerTracker Flask Application")
    print("=" * 50)
    
    # Pre-flight checks
    checks = [
        ("Dependencies", check_dependencies),
        ("Environment file", check_env_file),
        ("MongoDB", check_mongodb)
    ]
    
    all_passed = True
    for name, check_func in checks:
        print(f"\n🔍 Checking {name}...")
        if not check_func():
            all_passed = False
    
    if not all_passed:
        print("\n❌ Pre-flight checks failed. Please fix the issues above.")
        sys.exit(1)
    
    print("\n🎉 All checks passed! Starting Flask application...")
    print("🌐 Open your browser to: http://localhost:5000")
    print("⏹️  Press Ctrl+C to stop the server")
    print("-" * 50)
    
    # Start the Flask application
    try:
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
