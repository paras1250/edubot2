#!/usr/bin/env python3
"""
Initialize the database with sample data
"""

import os
from app import create_app, db
from app.models.user import User
from app.models.quote import Quote

def init_database():
    """Initialize database with sample data"""
    print("🗄️  Initializing database...")
    
    # Create application context
    app = create_app()
    
    with app.app_context():
        # Drop all tables and recreate
        print("📋 Creating database tables...")
        db.drop_all()
        db.create_all()
        
        # Create admin user
        print("👤 Creating admin user...")
        admin = User(
            username='admin',
            email='admin@edubot.com',
            first_name='Admin',
            last_name='User',
            role='admin'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        
        # Create a sample student
        print("👨‍🎓 Creating sample student...")
        student = User(
            username='student1',
            email='student1@college.edu',
            first_name='John',
            last_name='Doe',
            role='student',
            student_id='STU001',
            year_of_study=2,
            phone='+1234567890'
        )
        student.set_password('student123')
        db.session.add(student)
        
        # Add some motivational quotes
        print("💭 Adding motivational quotes...")
        quotes = [
            Quote(
                quote="The only way to do great work is to love what you do.",
                author="Steve Jobs",
                category="motivation"
            ),
            Quote(
                quote="Education is the most powerful weapon which you can use to change the world.",
                author="Nelson Mandela",
                category="education"
            ),
            Quote(
                quote="Success is not final, failure is not fatal: it is the courage to continue that counts.",
                author="Winston Churchill",
                category="success"
            ),
            Quote(
                quote="The future belongs to those who believe in the beauty of their dreams.",
                author="Eleanor Roosevelt",
                category="motivation"
            ),
            Quote(
                quote="Learning never exhausts the mind.",
                author="Leonardo da Vinci",
                category="learning"
            )
        ]
        
        for quote in quotes:
            db.session.add(quote)
        
        # Commit all changes
        print("💾 Saving to database...")
        db.session.commit()
        
        print("✅ Database initialized successfully!")
        print("\n🔐 Default Login Credentials:")
        print("   Admin: admin / admin123")
        print("   Student: student1 / student123")
        print("\n🚀 You can now run: python run.py")

if __name__ == "__main__":
    init_database()
