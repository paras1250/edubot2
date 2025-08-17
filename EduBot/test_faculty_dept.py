#!/usr/bin/env python3
"""
Test faculty department query logic specifically
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.chatbot.handlers import response_handler
from app.models.faculty import Faculty

def test_faculty_department_logic():
    """Test the faculty department query logic directly"""
    
    app = create_app()
    
    with app.app_context():
        print("🧪 TESTING FACULTY DEPARTMENT LOGIC")
        print("=" * 50)
        
        # Get faculty members from database
        faculty_members = Faculty.query.filter_by(is_active=True).all()
        print(f"Found {len(faculty_members)} active faculty members")
        
        test_inputs = [
            "computer science",
            "cs", 
            "mathematics",
            "math",
            "physics"
        ]
        
        for test_input in test_inputs:
            print(f"\n🔍 Testing: '{test_input}'")
            
            try:
                # Test the department query method directly
                result = response_handler._check_department_query(test_input.lower(), faculty_members)
                
                if result:
                    print(f"✅ Found department match:")
                    print(f"   Response: {result[:100]}...")
                else:
                    print("❌ No department match found")
                    
                # Also test the full faculty handler
                full_response = response_handler.handle_faculty(test_input, "template", None)
                print(f"📝 Full handler response: {full_response[:100]}...")
                
            except Exception as e:
                print(f"❌ Error: {e}")
            
            print("-" * 50)

if __name__ == "__main__":
    test_faculty_department_logic()
