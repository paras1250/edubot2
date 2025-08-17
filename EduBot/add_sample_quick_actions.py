#!/usr/bin/env python3
"""
Add sample Quick Actions to test the functionality
"""

import os
import sys
from app import create_app, db
from app.models.quick_action import QuickAction
from app.models.user import User

def add_sample_quick_actions():
    """Add sample Quick Actions to the database"""
    
    # Sample Quick Actions data
    quick_actions_data = [
        {
            'question': 'What are the library hours?',
            'response': '📚 **Library Hours:**\n\nMonday - Friday: 8:00 AM - 8:00 PM\nSaturday: 9:00 AM - 5:00 PM\nSunday: 10:00 AM - 4:00 PM\n\n📖 Extended hours during exam periods!',
            'category': 'Library',
            'keywords': 'library, hours, time, open, close, timings',
            'priority': 8
        },
        {
            'question': 'How do I check my fees?',
            'response': '💰 **Fee Payment & Status:**\n\n1. Log into the student portal\n2. Navigate to "Fees" section\n3. View current balance and payment history\n4. Download fee receipts\n\n💳 Payment methods: Online banking, UPI, Credit/Debit cards\n\n📞 For queries: Contact accounts office at ext. 234',
            'category': 'Finance',
            'keywords': 'fees, payment, tuition, cost, money, balance, pay',
            'priority': 9
        },
        {
            'question': 'Where is the cafeteria?',
            'response': '🍽️ **Cafeteria Location:**\n\n📍 2nd Floor, Main Building (next to student lounge)\n\n⏰ **Timings:**\nBreakfast: 7:00 AM - 10:00 AM\nLunch: 12:00 PM - 3:00 PM\nDinner: 6:00 PM - 9:00 PM\n\n🍕 Special menu on weekends!',
            'category': 'Facilities',
            'keywords': 'cafeteria, food, canteen, dining, eat, restaurant, lunch, breakfast, dinner',
            'priority': 6
        },
        {
            'question': 'What is the admission process?',
            'response': '🎓 **Admission Process:**\n\n1. **Application:** Fill online form at college website\n2. **Documents:** Submit required certificates\n3. **Merit List:** Check published lists\n4. **Counseling:** Attend admission counseling\n5. **Fee Payment:** Complete within deadline\n\n📋 **Required Documents:**\n• 10th & 12th mark sheets\n• Transfer certificate\n• Migration certificate\n• ID proof\n• Passport photos\n\n📞 **Admissions Office:** +91-XXX-XXXXXXX',
            'category': 'Admissions',
            'keywords': 'admission, apply, application, process, documents, eligibility, requirements',
            'priority': 10
        },
        {
            'question': 'How do I find campus events?',
            'response': '📅 **Find Campus Events:**\n\n🔍 **Ways to stay updated:**\n• Check the official events calendar\n• Visit the notice board\n• Follow college social media\n• Ask me about \"upcoming events\" for real-time info\n\n📱 **Tip:** I can show you live event information from our database - just ask about events!',
            'category': 'Information',
            'keywords': 'events info, find events, events calendar, how to check events',
            'priority': 5
        },
        {
            'question': 'How do I reset my password?',
            'response': '🔐 **Password Reset Instructions:**\n\n1. Go to login page\n2. Click "Forgot Password"\n3. Enter your email/student ID\n4. Check your email for reset link\n5. Follow the link and create new password\n\n📧 **Note:** Reset link expires in 24 hours\n\n❓ **Still having issues?**\nContact IT Help Desk:\n📞 Extension: 567\n📧 helpdesk@college.edu',
            'category': 'IT Support',
            'keywords': 'password, reset, forgot, login, access, account, help',
            'priority': 8
        },
        {
            'question': 'What are the hostel rules?',
            'response': '🏠 **Hostel Rules & Regulations:**\n\n⏰ **Timings:**\n• Entry Gate closes: 10:00 PM\n• Study hours: 7:00 PM - 10:00 PM\n• Lights out: 11:00 PM\n\n📋 **Important Rules:**\n• No outside guests after 8:00 PM\n• Keep rooms clean and tidy\n• No loud music/noise\n• Respect mess timings\n• Follow visitor procedures\n\n📞 **Warden Contact:** +91-XXX-XXXXXXX',
            'category': 'Hostel',
            'keywords': 'hostel, rules, regulations, timings, warden, accommodation',
            'priority': 6
        },
        {
            'question': 'How do I apply for a transfer certificate?',
            'response': '📄 **Transfer Certificate Application:**\n\n📝 **Steps:**\n1. Fill TC application form\n2. Clear all dues (library, fees, etc.)\n3. Submit form to academic office\n4. Pay processing fee: ₹500\n5. Collect TC after 5 working days\n\n📋 **Required:**\n• Application form\n• No-dues certificate\n• Fee clearance\n• ID proof\n\n📞 **Academic Office:** Extension 123',
            'category': 'Academic',
            'keywords': 'transfer certificate, TC, application, documents, clearance',
            'priority': 7
        }
    ]
    
    print("Adding sample Quick Actions...")
    
    try:
        # Get admin user (or create a default one)
        admin_user = User.query.filter_by(role='admin').first()
        if not admin_user:
            print("No admin user found. Quick Actions will be created without creator.")
            admin_user_id = None
        else:
            admin_user_id = admin_user.id
            print(f"Using admin user: {admin_user.username}")
        
        # Add each Quick Action
        for qa_data in quick_actions_data:
            # Check if this Quick Action already exists
            existing = QuickAction.query.filter_by(question=qa_data['question']).first()
            if existing:
                print(f"Quick Action already exists: {qa_data['question'][:50]}...")
                continue
            
            # Create new Quick Action
            quick_action = QuickAction(
                question=qa_data['question'],
                response=qa_data['response'],
                category=qa_data['category'],
                keywords=qa_data['keywords'],
                priority=qa_data['priority'],
                is_active=True,
                created_by=admin_user_id
            )
            
            db.session.add(quick_action)
            print(f"Added: {qa_data['question'][:50]}...")
        
        # Commit all changes
        db.session.commit()
        print(f"\n✅ Successfully added {len(quick_actions_data)} Quick Actions!")
        
        # Show summary
        total_qa = QuickAction.query.count()
        active_qa = QuickAction.query.filter_by(is_active=True).count()
        print(f"📊 Total Quick Actions in database: {total_qa}")
        print(f"📊 Active Quick Actions: {active_qa}")
        
    except Exception as e:
        print(f"❌ Error adding Quick Actions: {e}")
        db.session.rollback()

if __name__ == '__main__':
    app = create_app()
    
    with app.app_context():
        add_sample_quick_actions()
