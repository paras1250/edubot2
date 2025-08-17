#!/usr/bin/env python3
"""
Test script to check environment variables and Gemini service
"""

import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("🔍 Environment Variables Check")
print("=" * 40)
print(f"GEMINI_API_KEY: {os.environ.get('GEMINI_API_KEY', 'NOT SET')}")
print(f"FLASK_ENV: {os.environ.get('FLASK_ENV', 'NOT SET')}")
print()

# Test Gemini service directly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from app.services.gemini_service import gemini_service
    
    print("🤖 Testing Gemini Service")
    print("=" * 40)
    
    # Initialize the service
    api_key = os.environ.get('GEMINI_API_KEY')
    if api_key:
        result = gemini_service.initialize(api_key)
        print(f"Initialization result: {result}")
        print(f"Service available: {gemini_service.is_available()}")
        
        if gemini_service.is_available():
            print("\n🧪 Testing Gemini Response")
            test_response = gemini_service.generate_response("What is the capital of France?")
            print(f"Response: {test_response}")
        else:
            print("❌ Gemini service not available")
    else:
        print("❌ No API key found")
        
except Exception as e:
    print(f"❌ Error testing Gemini service: {e}")
