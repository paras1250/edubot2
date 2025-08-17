#!/usr/bin/env python3
"""
Debug script to test intent recognition
"""

from app.chatbot.intents import intent_recognizer

def test_intent_recognition():
    """Test what intent is recognized for different questions"""
    
    # Initialize with default intents
    intent_recognizer._load_default_intents()
    
    test_questions = [
        "how to study for exam",
        "what is machine learning",
        "tell me about faculty",
        "help me with attendance",
        "hello",
        "what is photosynthesis",
        "how to improve my grades",
        "study tips for students"
    ]
    
    print("🔍 Testing Intent Recognition...")
    print("=" * 60)
    
    for question in test_questions:
        intent_name, confidence, pattern = intent_recognizer.recognize_intent(question)
        print(f"Question: {question}")
        print(f"Intent: {intent_name}")
        print(f"Confidence: {confidence:.2f}")
        print(f"Pattern: {pattern}")
        print(f"Should use Gemini? {'YES' if intent_name == 'default' or confidence < 0.7 else 'NO'}")
        print("-" * 60)

if __name__ == "__main__":
    test_intent_recognition()
