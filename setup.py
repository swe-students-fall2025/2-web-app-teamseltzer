#!/usr/bin/env python3
"""
Setup script for SeltzerTracker Flask application
"""

import os
import subprocess
import sys

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False

def main():
    print("🚀 Setting up SeltzerTracker Flask Application")
    print("=" * 50)
    
    # Check if Python is available
    if not run_command("python3 --version", "Checking Python installation"):
        print("❌ Python 3 is required but not found. Please install Python 3.")
        sys.exit(1)
    
    # Check if pip is available
    if not run_command("pip3 --version", "Checking pip installation"):
        print("❌ pip3 is required but not found. Please install pip3.")
        sys.exit(1)
    
    # Install Python dependencies
    if not run_command("pip3 install -r requirements.txt", "Installing Python dependencies"):
        print("❌ Failed to install dependencies. Please check requirements.txt")
        sys.exit(1)
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("📝 Creating .env file from template...")
        if os.path.exists('env.example'):
            with open('env.example', 'r') as src:
                with open('.env', 'w') as dst:
                    dst.write(src.read())
            print("✅ .env file created. Please update it with your MongoDB credentials.")
        else:
            print("⚠️  env.example not found. Please create .env file manually.")
    
    # Check if MongoDB is running (optional)
    print("🔍 Checking MongoDB connection...")
    try:
        import pymongo
        from pymongo import MongoClient
        client = MongoClient('mongodb://localhost:27017/')
        client.admin.command('ping')
        print("✅ MongoDB is running and accessible")
    except Exception as e:
        print(f"⚠️  MongoDB connection failed: {e}")
        print("   Please make sure MongoDB is installed and running:")
        print("   - Install MongoDB: https://docs.mongodb.com/manual/installation/")
        print("   - Start MongoDB: mongod")
    
    print("\n🎉 Setup completed!")
    print("\n📋 Next steps:")
    print("1. Update .env file with your MongoDB credentials")
    print("2. Make sure MongoDB is running")
    print("3. Run the application: python3 app.py")
    print("4. Open your browser to: http://localhost:5000")
    print("\n🔧 Default admin password: admin123 (change in .env)")

if __name__ == "__main__":
    main()
