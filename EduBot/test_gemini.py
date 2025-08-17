#!/usr/bin/env python3
"""
Test script to verify Gemini API integration
"""

import os
from dotenv import load_dotenv
from app.services.gemini_service import gemini_service

def test_gemini_integration():
    """Test the Gemini AI integration"""
    
    # Load environment variables
    load_dotenv()
    
    print("🔧 Testing Gemini AI Integration...")
    print("-" * 50)
    
    # Initialize the service
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key or api_key == 'your-gemini-api-key-here':
        print("❌ No valid Gemini API key found in .env file")
        return False
    
    print(f"✅ API Key found: {api_key[:10]}...")
    
    # Initialize Gemini service
    success = gemini_service.initialize(api_key)
    
    if not success:
        print("❌ Failed to initialize Gemini service")
        return False
    
    print("✅ Gemini service initialized successfully")
    
    # Test questions
    test_questions = [
        "What is machine learning?",
        "How to study effectively for exams?",
        "Explain photosynthesis in simple terms",
        "What career options are there in computer science?"
    ]
    
    print("\n🧪 Testing sample questions...")
    print("-" * 50)
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n{i}. Question: {question}")
        
        # Generate response
        response = gemini_service.generate_response(
            question, 
            context={'user_name': 'Test User', 'is_authenticated': True}
        )
        
        if response:
            print(f"✅ Response: {response[:100]}...")
        else:
            print("❌ No response generated")
    
    print("\n" + "=" * 50)
    print("Test completed!")
    
    return True

if __name__ == "__main__":
    test_gemini_integration()
