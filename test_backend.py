#!/usr/bin/env python3
"""
Simple test script to verify the SeltzerTracker backend is working
"""

import requests
import json
import sys

BASE_URL = "http://localhost:5000"

def test_connection():
    """Test if the server is running"""
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ Server is running")
            return True
        else:
            print(f"❌ Server returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure it's running on localhost:5000")
        return False

def test_registration():
    """Test user registration"""
    print("\n🔄 Testing user registration...")
    
    test_user = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/register", json=test_user)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ User registration successful")
                return True
            else:
                print(f"❌ Registration failed: {result.get('message')}")
                return False
        else:
            print(f"❌ Registration request failed with status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return False

def test_login():
    """Test user login"""
    print("\n🔄 Testing user login...")
    
    login_data = {
        "username": "testuser",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/login", json=login_data)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ User login successful")
                return True
            else:
                print(f"❌ Login failed: {result.get('message')}")
                return False
        else:
            print(f"❌ Login request failed with status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Login error: {e}")
        return False

def test_brands_api():
    """Test brands API"""
    print("\n🔄 Testing brands API...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/brands")
        if response.status_code == 200:
            brands = response.json()
            if len(brands) > 0:
                print(f"✅ Brands API working - found {len(brands)} brands")
                return True
            else:
                print("❌ No brands found")
                return False
        else:
            print(f"❌ Brands API failed with status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Brands API error: {e}")
        return False

def main():
    print("🧪 Testing SeltzerTracker Backend")
    print("=" * 40)
    
    # Test server connection
    if not test_connection():
        print("\n❌ Backend tests failed - server not running")
        print("   Run: python3 app.py")
        sys.exit(1)
    
    # Test APIs
    tests = [
        test_brands_api,
        test_registration,
        test_login
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Backend is working correctly.")
        print("\n🌐 You can now:")
        print("   - Open http://localhost:5000 in your browser")
        print("   - Register a new account")
        print("   - Start logging seltzers!")
    else:
        print("❌ Some tests failed. Check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
