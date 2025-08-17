#!/usr/bin/env python3
"""
Test script to verify faculty intent recognition works correctly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.chatbot.intents import intent_recognizer

def test_faculty_intent():
    """Test faculty intent recognition with various inputs"""
    
    # Load default intents
    intent_recognizer._load_default_intents()
    
    test_cases = [
        "faculty",
        "show me faculty",
        "faculty information",
        "computer science",
        "computer science department",
        "cs",
        "mathematics",
        "math department",
        "physics",
        "engineering",
        "who teaches computer science",
        "computer science faculty"
    ]
    
    print("🧪 Testing Faculty Intent Recognition")
    print("=" * 50)
    
    for test_input in test_cases:
        intent_name, confidence, pattern = intent_recognizer.recognize_intent(test_input)
        
        print(f"Input: '{test_input}'")
        print(f"  Intent: {intent_name}")
        print(f"  Confidence: {confidence}")
        print(f"  Pattern: {pattern}")
        print(f"  Expected: faculty_info ✅" if intent_name == 'faculty_info' else f"  Expected: faculty_info ❌")
        print()

if __name__ == "__main__":
    test_faculty_intent()
