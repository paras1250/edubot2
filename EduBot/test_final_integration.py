#!/usr/bin/env python3
"""
Final comprehensive test for faculty handling and Gemini AI integration
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.chatbot.engine import chatbot_engine

def test_comprehensive_functionality():
    """Test all functionality including faculty departments and Gemini AI"""
    
    app = create_app()
    
    with app.app_context():
        # Initialize chatbot engine
        chatbot_engine.initialize()
        
        print("🔧 COMPREHENSIVE FUNCTIONALITY TEST")
        print("=" * 60)
        
        # Test cases covering all scenarios
        test_cases = [
            # Faculty intent tests
            ("faculty", "Should show full faculty list from database", "faculty_info"),
            ("computer science", "Should show CS department faculty from database", "faculty_info"),
            ("cs", "Should show Computer Science faculty from database", "faculty_info"),
            ("mathematics", "Should show Math department faculty from database", "faculty_info"),
            ("engineering", "Should show Engineering faculty from database", "faculty_info"),
            
            # Database intents (should never use Gemini)
            ("attendance", "Should respond with attendance info (or auth error)", "attendance"),
            ("events", "Should show events from database", "events"),
            ("courses", "Should show courses from database", "courses"),
            
            # Gemini AI tests (should use AI for unknown questions)
            ("how to improve speaking skills", "Should use Gemini AI", "gemini_ai"),
            ("what is the capital of France", "Should use Gemini AI", "gemini_ai"),
            ("tell me a joke", "Should use Gemini AI", "gemini_ai"),
            ("how to study effectively", "Should use Gemini AI", "gemini_ai"),
            ("explain photosynthesis", "Should use Gemini AI", "gemini_ai"),
            ("career advice for computer science students", "Should use Gemini AI", "gemini_ai"),
        ]
        
        for user_input, expected_behavior, expected_intent_type in test_cases:
            print(f"\n📝 Testing: '{user_input}'")
            print(f"📋 Expected: {expected_behavior}")
            
            try:
                # Process message
                response = chatbot_engine.process_message(user_input)
                
                actual_intent = response.get('intent', 'unknown')
                confidence = response.get('confidence', 0)
                bot_response = response.get('response', 'No response')
                
                print(f"🎯 Intent: {actual_intent}")
                print(f"📊 Confidence: {confidence}")
                print(f"💬 Response: {bot_response[:100]}...")
                
                # Check if response is from Gemini
                is_gemini = bot_response.startswith('This answer is provided by AI:')
                print(f"🤖 Gemini AI: {'Yes' if is_gemini else 'No'}")
                
                # Validate expected vs actual
                if expected_intent_type == "gemini_ai":
                    if is_gemini:
                        print("✅ PASS: Gemini AI responded as expected")
                    else:
                        print("❌ FAIL: Expected Gemini AI but got database response")
                elif expected_intent_type in actual_intent:
                    if not is_gemini:
                        print("✅ PASS: Database responded as expected")
                    else:
                        print("❌ FAIL: Expected database but got Gemini AI")
                else:
                    print(f"⚠️  PARTIAL: Got {actual_intent}, expected {expected_intent_type}")
                
            except Exception as e:
                print(f"❌ ERROR: {e}")
            
            print("-" * 60)
        
        print("\n🏁 TEST COMPLETED")
        print("Check the results above to verify:")
        print("1. Faculty department queries work correctly")
        print("2. Database intents are protected from Gemini override")
        print("3. Unknown/general questions use Gemini AI")

if __name__ == "__main__":
    test_comprehensive_functionality()
