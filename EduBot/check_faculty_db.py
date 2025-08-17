#!/usr/bin/env python3
"""
Check faculty records in database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models.faculty import Faculty

def check_faculty_records():
    """Check what faculty records exist in the database"""
    
    app = create_app()
    
    with app.app_context():
        print("🔍 CHECKING FACULTY DATABASE")
        print("=" * 40)
        
        try:
            # Get all faculty members
            faculty_members = Faculty.query.all()
            
            print(f"Total faculty records: {len(faculty_members)}")
            
            if faculty_members:
                print("\nFaculty List:")
                for faculty in faculty_members:
                    print(f"- {faculty.name} ({faculty.department}) - Active: {faculty.is_active}")
                    if faculty.user:
                        print(f"  User: {faculty.user.full_name}")
                    else:
                        print("  No associated user")
                
                # Check unique departments
                departments = list(set([f.department for f in faculty_members if f.department]))
                print(f"\nDepartments found: {departments}")
                
            else:
                print("❌ No faculty records found in database!")
                
        except Exception as e:
            print(f"Error accessing database: {e}")

if __name__ == "__main__":
    check_faculty_records()
