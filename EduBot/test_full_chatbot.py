#!/usr/bin/env python3
"""
End-to-end test script for chatbot with Gemini integration
"""

import os
from dotenv import load_dotenv
from app import create_app
from app.chatbot.engine import chatbot_engine
from app.services.gemini_service import gemini_service

def test_full_chatbot():
    """Test the complete chatbot flow including Gemini integration"""
    
    # Load environment variables
    load_dotenv()
    
    print("🚀 Testing Full EduBot Integration...")
    print("=" * 60)
    
    # Create Flask app with proper context
    app = create_app()
    
    with app.app_context():
        # Test Gemini service initialization
        print("🔧 Testing Gemini Service...")
        print(f"Gemini Available: {gemini_service.is_available()}")
        print(f"Gemini Status: {gemini_service.get_status()}")
        
        # Test questions that should trigger Gemini
        test_questions = [
            "how to study for exam",
            "what is machine learning",
            "explain photosynthesis",
            "study tips for students",
            "how to improve grades"
        ]
        
        print("\n🧪 Testing Chatbot Responses...")
        print("-" * 60)
        
        for i, question in enumerate(test_questions, 1):
            print(f"\n{i}. Testing: '{question}'")
            
            try:
                # Process the message using chatbot engine
                result = chatbot_engine.process_message(
                    user_message=question,
                    user_id=1,  # Mock user ID
                    session_id="test-session"
                )
                
                print(f"   Intent: {result['intent']}")
                print(f"   Confidence: {result['confidence']:.2f}")
                print(f"   Response: {result['response'][:100]}...")
                print(f"   Success: {result['success']}")
                
                # Check if Gemini was used
                if result['intent'] == 'gemini_ai' or "This answer is provided by AI:" in result['response']:
                    print("   ✅ Gemini AI was used!")
                else:
                    print("   ❌ Gemini AI was NOT used")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
            
            print("-" * 40)
        
        print("\n" + "=" * 60)
        print("Test completed!")

if __name__ == "__main__":
    test_full_chatbot()
