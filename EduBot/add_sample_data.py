#!/usr/bin/env python3
"""
Add sample data for testing EduBot functionality
"""

from datetime import datetime, date, timedelta
from app import create_app, db
from app.models.user import User
from app.models.faculty import Faculty
from app.models.course import Course
from app.models.event import Event
from app.models.attendance import Attendance

def add_sample_data():
    """Add sample data for testing"""
    print("🗄️ Adding sample data...")
    
    app = create_app()
    
    with app.app_context():
        # Add sample faculty users
        print("👨‍🏫 Creating faculty users...")
        
        # Faculty 1
        faculty_user1 = User(
            username='prof_smith',
            email='john.smith@college.edu',
            first_name='John',
            last_name='Smith',
            role='faculty'
        )
        faculty_user1.set_password('faculty123')
        db.session.add(faculty_user1)
        db.session.flush()  # To get the ID
        
        faculty1 = Faculty(
            user_id=faculty_user1.id,
            employee_id='FAC001',
            department='Computer Science',
            designation='Professor',
            specialization='Artificial Intelligence, Machine Learning',
            office_location='Room 101, CS Building',
            office_hours='Mon-Wed-Fri 2:00 PM - 4:00 PM',
            bio='Dr. John Smith has 15 years of experience in AI and ML research.'
        )
        db.session.add(faculty1)
        
        # Faculty 2
        faculty_user2 = User(
            username='dr_jones',
            email='sarah.jones@college.edu',
            first_name='Sarah',
            last_name='Jones',
            role='faculty'
        )
        faculty_user2.set_password('faculty123')
        db.session.add(faculty_user2)
        db.session.flush()
        
        faculty2 = Faculty(
            user_id=faculty_user2.id,
            employee_id='FAC002',
            department='Mathematics',
            designation='Associate Professor',
            specialization='Statistics, Data Analysis',
            office_location='Room 205, Math Building',
            office_hours='Tue-Thu 10:00 AM - 12:00 PM',
            bio='Dr. Sarah Jones specializes in statistical analysis and data science.'
        )
        db.session.add(faculty2)
        
        # Faculty 3
        faculty_user3 = User(
            username='prof_brown',
            email='michael.brown@college.edu',
            first_name='Michael',
            last_name='Brown',
            role='faculty'
        )
        faculty_user3.set_password('faculty123')
        db.session.add(faculty_user3)
        db.session.flush()
        
        faculty3 = Faculty(
            user_id=faculty_user3.id,
            employee_id='FAC003',
            department='Physics',
            designation='Assistant Professor',
            specialization='Quantum Physics, Electronics',
            office_location='Room 302, Physics Lab',
            office_hours='Mon-Thu 1:00 PM - 3:00 PM',
            bio='Prof. Michael Brown teaches quantum physics and electronics.'
        )
        db.session.add(faculty3)
        
        print("📚 Creating sample courses...")
        
        
        print("📅 Creating sample events...")
        
        # Add sample events
        today = date.today()
        
        event1 = Event(
            title='Annual Tech Fest',
            description='College technical festival with competitions and workshops',
            event_type='cultural',
            start_date=today + timedelta(days=15),
            end_date=today + timedelta(days=17),
            location='Main Auditorium',
            organizer='Student Council'
        )
        db.session.add(event1)
        
        event2 = Event(
            title='Mid-term Examinations',
            description='Mid-semester examinations for all courses',
            event_type='exam',
            start_date=today + timedelta(days=30),
            end_date=today + timedelta(days=35),
            location='Examination Hall'
        )
        db.session.add(event2)
        
        event3 = Event(
            title='Independence Day',
            description='National holiday celebration',
            event_type='holiday',
            start_date=date(2024, 8, 15),
            is_holiday=True,
            location='College Campus'
        )
        db.session.add(event3)
        
        event4 = Event(
            title='Career Fair 2024',
            description='Job placement drive with top companies',
            event_type='academic',
            start_date=today + timedelta(days=45),
            location='Sports Complex',
            organizer='Placement Cell'
        )
        db.session.add(event4)
        
        
        # Commit all changes
        print("💾 Saving all data to database...")
        db.session.commit()
        
        print("✅ Sample data added successfully!")
        print("\n📋 Summary:")
        print(f"   👨‍🏫 Faculty members: 3")
        print(f"   📚 Courses: 0 (Admin can add courses as needed)") 
        print(f"   📅 Events: 4")
        print(f"   📊 Attendance records: 0")
        
        print("\n🔗 Faculty Login Credentials:")
        print("   prof_smith / faculty123")
        print("   dr_jones / faculty123")
        print("   prof_brown / faculty123")
        
        print("\n🤖 Now you can test the chatbot with queries like:")
        print("   - 'Tell me about faculty'")
        print("   - 'Who is John Smith?'")
        print("   - 'Show me events'")
        print("   - 'Check my attendance'")

if __name__ == "__main__":
    add_sample_data()
