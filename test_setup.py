#!/usr/bin/env python
"""
Test script to check if Django can load properly
"""
import os
import sys
import django

# Add the project directory to the Python path
sys.path.insert(0, '/Users/mac/development/python_projects/SafariCrafts')

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.settings')

try:
    django.setup()
    print("✅ Django setup successful!")
    
    # Test imports
    from authentication.models import User
    print("✅ Authentication models imported successfully!")
    
    from catalog.models import Artwork
    print("✅ Catalog models imported successfully!")
    
    from django.contrib.auth import get_user_model
    UserModel = get_user_model()
    print(f"✅ Custom user model: {UserModel}")
    
    # Test database connection
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        print(f"✅ Database connection successful: {result}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
