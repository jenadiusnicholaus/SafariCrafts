#!/usr/bin/env python3
"""
SafariCrafts API Demo Script
Test the API endpoints with the loaded test data
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api"

def print_header(title):
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print(f"{'='*60}")

def print_response(response, title="Response"):
    print(f"\n📡 {title}:")
    print(f"Status: {response.status_code}")
    if response.status_code < 400:
        try:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                print(f"Count: {len(data)}")
                print(f"First item: {json.dumps(data[0], indent=2)[:500]}...")
            else:
                print(json.dumps(data, indent=2)[:500])
        except:
            print(response.text[:500])
    else:
        print(f"Error: {response.text[:200]}")

def test_catalog():
    """Test catalog endpoints"""
    print_header("CATALOG TESTING")
    
    # Test categories
    print("\n📂 Testing Categories:")
    response = requests.get(f"{BASE_URL}/catalog/categories/")
    print_response(response, "Categories List")
    
    # Test collections
    print("\n📚 Testing Collections:")
    response = requests.get(f"{BASE_URL}/catalog/collections/")
    print_response(response, "Collections List")
    
    # Test artworks
    print("\n🎨 Testing Artworks:")
    response = requests.get(f"{BASE_URL}/catalog/artworks/")
    print_response(response, "Artworks List")

def test_artists():
    """Test artist endpoints"""
    print_header("ARTISTS TESTING")
    
    # Test artists list
    print("\n🎭 Testing Artists:")
    response = requests.get(f"{BASE_URL}/artists/")
    print_response(response, "Artists List")

def main():
    """Run all API tests"""
    print("🚀 SafariCrafts API Demo Starting...")
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Test basic endpoints first
        test_catalog()
        test_artists()
        
        print_header("DEMO COMPLETE")
        print("✅ API demo completed successfully!")
        print("\n🌐 Available endpoints:")
        print("• Admin Panel: http://localhost:8000/admin/")
        print("• API Docs: http://localhost:8000/api/docs/")
        print("• API Root: http://localhost:8000/api/")
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the Django server is running on localhost:8000")
        print("Run: python manage.py runserver")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
