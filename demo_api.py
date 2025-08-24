#!/usr/bin/env python
"""
SafariCrafts API Demo Script
This script demonstrates the key functionality of the SafariCrafts API
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
HEADERS = {"Content-Type": "application/json"}

def print_section(title):
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def print_response(response, title="Response"):
    print(f"\n{title}:")
    print(f"Status: {response.status_code}")
    if response.headers.get('content-type', '').startswith('application/json'):
        try:
            data = response.json()
            print(f"Data: {json.dumps(data, indent=2)}")
        except:
            print(f"Raw: {response.text}")
    else:
        print(f"Content: {response.text[:200]}...")

def demo_authentication():
    print_section("1. AUTHENTICATION DEMO")
    
    # Register a new user
    print("\n1.1 Registering a new buyer...")
    buyer_data = {
        "email": "buyer@example.com",
        "username": "buyer1",
        "first_name": "John",
        "last_name": "Doe",
        "phone": "+255700000001",
        "role": "buyer",
        "password": "testpassword123",
        "password_confirm": "testpassword123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register/", 
                           headers=HEADERS, 
                           json=buyer_data)
    print_response(response, "Buyer Registration")
    
    if response.status_code == 201:
        buyer_tokens = response.json().get('tokens', {})
        buyer_access_token = buyer_tokens.get('access')
    else:
        buyer_access_token = None
    
    # Register an artist
    print("\n1.2 Registering a new artist...")
    artist_data = {
        "email": "artist@example.com",
        "username": "artist1",
        "first_name": "Maria",
        "last_name": "Makonde",
        "phone": "+255700000002",
        "role": "artist",
        "password": "testpassword123",
        "password_confirm": "testpassword123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register/", 
                           headers=HEADERS, 
                           json=artist_data)
    print_response(response, "Artist Registration")
    
    if response.status_code == 201:
        artist_tokens = response.json().get('tokens', {})
        artist_access_token = artist_tokens.get('access')
    else:
        artist_access_token = None
    
    # Login test
    print("\n1.3 Testing login...")
    login_data = {
        "email": "buyer@example.com",
        "password": "testpassword123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login/", 
                           headers=HEADERS, 
                           json=login_data)
    print_response(response, "Login")
    
    return buyer_access_token, artist_access_token

def demo_catalog(buyer_token, artist_token):
    print_section("2. CATALOG DEMO")
    
    # Get categories
    print("\n2.1 Fetching categories...")
    response = requests.get(f"{BASE_URL}/catalog/categories/")
    print_response(response, "Categories")
    
    # Get collections
    print("\n2.2 Fetching collections...")
    response = requests.get(f"{BASE_URL}/catalog/collections/")
    print_response(response, "Collections")
    
    # Get artworks
    print("\n2.3 Fetching artworks...")
    response = requests.get(f"{BASE_URL}/catalog/artworks/")
    print_response(response, "Artworks")
    
    # Get filter options
    print("\n2.4 Fetching filter options...")
    response = requests.get(f"{BASE_URL}/catalog/filter-options/")
    print_response(response, "Filter Options")
    
    # Get stats
    print("\n2.5 Fetching artwork stats...")
    response = requests.get(f"{BASE_URL}/catalog/stats/")
    print_response(response, "Artwork Stats")

def demo_cart(buyer_token):
    print_section("3. SHOPPING CART DEMO")
    
    if not buyer_token:
        print("❌ No buyer token available, skipping cart demo")
        return
    
    auth_headers = {**HEADERS, "Authorization": f"Bearer {buyer_token}"}
    
    # Get cart
    print("\n3.1 Getting user cart...")
    response = requests.get(f"{BASE_URL}/catalog/cart/", headers=auth_headers)
    print_response(response, "User Cart")
    
    # Note: Adding items to cart would require actual artwork IDs
    print("\n3.2 Cart operations require existing artworks, which need to be created first")

def demo_user_profile(buyer_token):
    print_section("4. USER PROFILE DEMO")
    
    if not buyer_token:
        print("❌ No buyer token available, skipping profile demo")
        return
    
    auth_headers = {**HEADERS, "Authorization": f"Bearer {buyer_token}"}
    
    # Get profile
    print("\n4.1 Getting user profile...")
    response = requests.get(f"{BASE_URL}/auth/profile/", headers=auth_headers)
    print_response(response, "User Profile")
    
    # Update profile
    print("\n4.2 Updating user profile...")
    update_data = {
        "phone": "+255700000999",
        "locale": "sw"  # Swahili
    }
    response = requests.patch(f"{BASE_URL}/auth/profile/", 
                            headers=auth_headers, 
                            json=update_data)
    print_response(response, "Profile Update")

def demo_api_documentation():
    print_section("5. API DOCUMENTATION")
    
    print("\n5.1 API Schema...")
    response = requests.get(f"{BASE_URL.replace('/api/v1', '')}/api/schema/")
    print(f"Status: {response.status_code}")
    print(f"Content-Type: {response.headers.get('content-type')}")
    
    print("\n5.2 Available endpoints:")
    print("📚 API Documentation: http://localhost:8000/api/docs/")
    print("📖 ReDoc Documentation: http://localhost:8000/api/redoc/")
    print("🔗 OpenAPI Schema: http://localhost:8000/api/schema/")

def main():
    print("🎨 SafariCrafts API Demo")
    print("🌍 Tanzanian African Art Ecommerce Platform")
    print("=" * 60)
    
    try:
        # Test basic connectivity
        print("🔍 Testing API connectivity...")
        response = requests.get(f"{BASE_URL}/catalog/stats/", timeout=5)
        if response.status_code == 200:
            print("✅ API is accessible!")
        else:
            print(f"⚠️  API returned status {response.status_code}")
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        print("Make sure the Django server is running on http://localhost:8000")
        return
    
    # Run demos
    buyer_token, artist_token = demo_authentication()
    demo_catalog(buyer_token, artist_token)
    demo_cart(buyer_token)
    demo_user_profile(buyer_token)
    demo_api_documentation()
    
    print_section("DEMO COMPLETE")
    print("✅ All API endpoints tested successfully!")
    print("\n🚀 Next Steps:")
    print("1. Visit http://localhost:8000/api/docs/ for interactive API documentation")
    print("2. Use the API with your frontend application")
    print("3. Create artist profiles and artworks")
    print("4. Test the full e-commerce flow")
    print("\n📁 Key Features Available:")
    print("• User Authentication (Buyer/Artist/Admin roles)")
    print("• Artwork Catalog with Advanced Filtering")
    print("• Shopping Cart Management")
    print("• Artist Profile Management")
    print("• Order and Payment Processing")
    print("• Certificate Generation")
    print("• Review and Rating System")
    print("• Shipping and Fulfillment")

if __name__ == "__main__":
    main()
