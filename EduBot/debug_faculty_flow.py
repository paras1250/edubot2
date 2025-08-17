#!/usr/bin/env python3
"""
Debug the complete faculty query flow to identify the issue
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.chatbot.engine import chatbot_engine
from app.models.faculty import Faculty
from app.models.user import User

def test_faculty_flow():
    """Test the complete faculty query flow"""
    
    app = create_app()
    
    with app.app_context():
        print("🔍 TESTING FACULTY CHATBOT FLOW")
        print("=" * 50)
        
        # Initialize chatbot engine
        chatbot_engine.initialize()
        
        # Test cases that should trigger faculty responses
        test_cases = [
            "faculty",
            "show me faculty",
            "faculty list",
            "computer science",
            "computer science faculty",
            "mathematics",
            "mathematics department",
            "physics",
            "John Smith",
            "Sarah Jones",
            "Michael Brown"
        ]
        
        print(f"Found {Faculty.query.count()} faculty members in database:")
        for faculty in Faculty.query.all():
            print(f"  - {faculty.name} ({faculty.department})")
        print()
        
        for test_input in test_cases:
            print(f"🧪 Testing: '{test_input}'")
            print("-" * 30)
            
            # Process the message through the chatbot engine
            response = chatbot_engine.process_message(test_input, user_id=1)
            
            print(f"Intent: {response['intent']}")
            print(f"Confidence: {response['confidence']}")
            print(f"Success: {response['success']}")
            print(f"Response Preview: {response['response'][:100]}...")
            
            # Check if we're getting faculty information
            if 'faculty' in response['response'].lower() or any(name in response['response'] for name in ['John Smith', 'Sarah Jones', 'Michael Brown']):
                print("✅ Faculty data found in response")
            else:
                print("❌ No faculty data in response")
                
            print()

def test_specific_department_queries():
    """Test specific department queries"""
    
    app = create_app()
    
    with app.app_context():
        print("🔍 TESTING DEPARTMENT-SPECIFIC QUERIES")
        print("=" * 50)
        
        # Initialize chatbot engine
        chatbot_engine.initialize()
        
        department_queries = [
            "Computer Science department",
            "Mathematics department", 
            "Physics department",
            "CS faculty",
            "Math faculty",
            "Who teaches in Computer Science?",
            "Show me mathematics teachers"
        ]
        
        for query in department_queries:
            print(f"🧪 Testing: '{query}'")
            print("-" * 30)
            
            response = chatbot_engine.process_message(query, user_id=1)
            
            print(f"Intent: {response['intent']}")
            print(f"Response: {response['response'][:200]}...")
            
            # Check if response contains department-specific faculty
            contains_dept_info = any(dept in response['response'] for dept in ['Computer Science', 'Mathematics', 'Physics'])
            print(f"Contains department info: {'✅' if contains_dept_info else '❌'}")
            print()

if __name__ == "__main__":
    test_faculty_flow()
    print("\n" + "=" * 50)
    test_specific_department_queries()
