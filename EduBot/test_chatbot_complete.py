#!/usr/bin/env python3
"""
Test script to verify complete chatbot functionality including Gemini AI
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Flask app context for testing
from app import create_app
from app.chatbot.engine import chatbot_engine

def test_chatbot_responses():
    """Test chatbot responses with various inputs"""
    
    # Create Flask app context
    app = create_app()
    
    with app.app_context():
        # Initialize chatbot engine
        chatbot_engine.initialize()
        
        test_cases = [
            ("faculty", "Should respond with faculty info from database"),
            ("computer science", "Should respond with CS department faculty from database"),
            ("attendance", "Should respond with attendance info"),
            ("how to improve speaking skills", "Should respond with Gemini AI"),
            ("what is the capital of France", "Should respond with Gemini AI"),
            ("tell me a joke", "Should respond with Gemini AI"),
            ("how to study effectively", "Should respond with Gemini AI")
        ]
        
        print("🤖 Testing Complete Chatbot Functionality")
        print("=" * 60)
        
        for user_input, expected_behavior in test_cases:
            print(f"\n📝 Input: '{user_input}'")
            print(f"📋 Expected: {expected_behavior}")
            
            # Process message
            response = chatbot_engine.process_message(user_input)
            
            print(f"🎯 Intent: {response.get('intent', 'unknown')}")
            print(f"📊 Confidence: {response.get('confidence', 0)}")
            print(f"💬 Response: {response.get('response', 'No response')[:100]}...")
            
            # Check if response is from Gemini
            is_gemini = response.get('response', '').startswith('This answer is provided by AI:')
            print(f"🤖 Gemini AI: {'Yes' if is_gemini else 'No'}")
            print("-" * 60)

if __name__ == "__main__":
    test_chatbot_responses()
