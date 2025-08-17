"""
EduBot Response Handlers
Handles specific responses for different intents with database queries
"""

import random
from datetime import datetime, timedelta
from typing import Dict, Any
from flask_login import current_user
from app import db
from app.models.user import User
from app.models.faculty import Faculty
from app.models.quote import Quiz
from app.models.quiz_session import QuizSession
from app.models.event import Event
from app.models.attendance import Attendance
from app.models.course import Course

class ResponseHandler:
    """Handles generating intelligent responses for different intents"""
    
    def __init__(self):
        self.handlers = {
            'handle_greeting': self.handle_greeting,
            'handle_faculty': self.handle_faculty,
            'handle_attendance': self.handle_attendance,
            'handle_events': self.handle_events,
            'handle_quiz': self.handle_quiz,
            'handle_courses': self.handle_courses,
            'handle_notes': self.handle_notes,
            'handle_thanks': self.handle_thanks,
            'handle_goodbye': self.handle_goodbye,
            'handle_help': self.handle_help,
            'handle_default': self.handle_default
        }
    
    def handle_intent(self, intent_name: str, user_message: str, template_response: str, 
                     user_context: Dict = None) -> str:
        """Handle the intent and generate appropriate response"""
        # First, try to get the handler from the intent recognizer
        from app.chatbot.intents import intent_recognizer
        
        handler_function_name = None
        if intent_name in intent_recognizer.intents:
            handler_function_name = intent_recognizer.intents[intent_name].get('handler')
        
        if handler_function_name and handler_function_name in self.handlers:
            return self.handlers[handler_function_name](user_message, template_response, user_context)
        else:
            # Fallback to the old method
            handler_name = f"handle_{intent_name}"
            if handler_name in self.handlers:
                return self.handlers[handler_name](user_message, template_response, user_context)
            else:
                return template_response
    
    def handle_greeting(self, user_message: str, template_response: str, user_context: Dict = None) -> str:
        """Handle greeting messages"""
        user_name = current_user.first_name if current_user.is_authenticated else "there"
        
        greetings = [
            f"Hello {user_name}! 👋 How can I help you today?",
            f"Hi {user_name}! What would you like to know about college?",
            f"Hey {user_name}! I'm here to assist you with faculty info, attendance, events, and more!",
            f"Greetings {user_name}! How may I assist you today?"
        ]
        
        # Add time-based greetings
        current_hour = datetime.now().hour
        if 5 <= current_hour < 12:
            greetings.append(f"Good morning {user_name}! Ready to start the day?")
        elif 12 <= current_hour < 17:
            greetings.append(f"Good afternoon {user_name}! How's your day going?")
        elif 17 <= current_hour < 22:
            greetings.append(f"Good evening {user_name}! Hope you had a productive day!")
        
        return random.choice(greetings)
    
    def handle_faculty(self, user_message: str, template_response: str, user_context: Dict = None) -> str:
        """Handle faculty information queries - directly show faculty list"""
        try:
            message_lower = user_message.lower().strip()
            
            # Get all faculty members first
            faculty_members = Faculty.query.filter_by(is_active=True).all()
            
            if not faculty_members:
                return "I don't have any faculty information available at the moment. Please contact the administration for faculty details."
            
            # Check if user is asking for specific faculty member by name
            for faculty in faculty_members:
                if faculty.user and (
                    faculty.user.first_name.lower() in message_lower or 
                    faculty.user.last_name.lower() in message_lower
                ):
                    return self._format_faculty_info(faculty)
            
            # PRIORITY: Check department names with keywords and exact matches
            department_response = self._check_department_query(message_lower, faculty_members)
            if department_response:
                return department_response
            
            # If just "faculty" or general request, show complete faculty list
            if any(keyword in message_lower for keyword in ['faculty', 'show me faculty', 'faculty list', 'all faculty']):
                return self._show_faculty_list()
            
            # If department name is mentioned but no faculty found, still show all faculty
            return self._show_faculty_list()
            
        except Exception as e:
            print(f"Error handling faculty query: {e}")
            return "I'm having trouble accessing faculty information right now. Please try again later."
    
    def _show_faculty_list(self) -> str:
        """Show complete list of faculty members"""
        try:
            faculty_members = Faculty.query.filter_by(is_active=True).all()
            
            if not faculty_members:
                return "I don't have any faculty information available at the moment. Please contact the administration for faculty details."
            
            response = "👥 **Faculty Members List:**\n\n"
            
            # Group by department
            departments = {}
            for faculty in faculty_members:
                dept = faculty.department or "Other"
                if dept not in departments:
                    departments[dept] = []
                departments[dept].append(faculty)
            
            # Display by department
            for dept_name, dept_faculty in departments.items():
                response += f"📚 **{dept_name}:**\n"
                for faculty in dept_faculty:
                    response += f"   👨‍🏫 **{faculty.name}** - {faculty.designation}\n"
                    if faculty.office_location:
                        response += f"      📍 Office: {faculty.office_location}\n"
                    if faculty.email:
                        response += f"      📧 {faculty.email}\n"
                response += "\n"
            
            response += "💡 **Need more details?** Just mention any faculty member's name and I'll provide their complete information!"
            return response
            
        except Exception as e:
            print(f"Error showing faculty list: {e}")
            return "I'm having trouble loading the faculty list right now. Please try again later."
    
    def _format_faculty_info(self, faculty: Faculty) -> str:
        """Format detailed faculty information"""
        response = f"👨‍🏫 **{faculty.name}**\n\n"
        response += f"🏢 **Department:** {faculty.department}\n"
        response += f"🎓 **Designation:** {faculty.designation}\n"
        
        if faculty.specialization:
            response += f"🔬 **Specialization:** {faculty.specialization}\n"
        
        if faculty.office_location:
            response += f"📍 **Office:** {faculty.office_location}\n"
        
        if faculty.office_hours:
            response += f"🕒 **Office Hours:** {faculty.office_hours}\n"
        
        if faculty.email:
            response += f"📧 **Email:** {faculty.email}\n"
        
        if faculty.phone:
            response += f"📞 **Phone:** {faculty.phone}\n"
        
        if faculty.bio:
            response += f"\n📝 **About:** {faculty.bio}\n"
        
        return response
    
    def _format_department_faculty(self, faculty_list, department):
        """Format faculty list for a department"""
        response = f"👥 **Faculty in {department.title()} Department:**\n\n"
        for faculty in faculty_list:
            response += f"• **{faculty.name}** - {faculty.designation}\n"
        response += f"\nWould you like detailed information about any of these faculty members?"
        return response
    
    def handle_attendance(self, user_message: str, template_response: str, user_context: Dict = None) -> str:
        """Handle attendance queries"""
        if not current_user.is_authenticated or not current_user.is_student():
            return "I can only check attendance for logged-in students. Please make sure you're logged in as a student."
        
        try:
            # Get user's attendance records
            attendance_records = Attendance.query.filter_by(student_id=current_user.id).all()
            
            if not attendance_records:
                return f"Hi {current_user.first_name}! I don't see any attendance records for you yet. Your attendance will appear here once classes begin and attendance is marked."
            
            # Calculate overall attendance
            total_classes = len(attendance_records)
            present_classes = len([a for a in attendance_records if a.status == 'present'])
            percentage = round((present_classes / total_classes) * 100, 1) if total_classes > 0 else 0
            
            response = f"📊 **Attendance Summary for {current_user.full_name}**\n\n"
            response += f"📈 **Overall Attendance:** {percentage}% ({present_classes}/{total_classes} classes)\n"
            
            # Status emoji based on percentage
            if percentage >= 85:
                response += "✅ Excellent attendance! Keep it up!\n\n"
            elif percentage >= 75:
                response += "👍 Good attendance, but try to improve!\n\n"
            else:
                response += "⚠️ Low attendance! Please attend more classes.\n\n"
            
            # Recent attendance (last 5 records)
            recent_records = sorted(attendance_records, key=lambda x: x.date, reverse=True)[:5]
            if recent_records:
                response += "📅 **Recent Attendance:**\n"
                for record in recent_records:
                    status_emoji = "✅" if record.status == "present" else "❌" if record.status == "absent" else "🕐"
                    course_name = record.course.course_name if record.course else "Unknown Course"
                    response += f"   {status_emoji} {record.date.strftime('%b %d')} - {course_name} ({record.status.title()})\n"
            
            response += "\n💡 Tip: Maintain at least 75% attendance to be eligible for exams!"
            return response
            
        except Exception as e:
            print(f"Error handling attendance query: {e}")
            return "I'm having trouble accessing your attendance records right now. Please try again later."
    
    def handle_events(self, user_message: str, template_response: str, user_context: Dict = None) -> str:
        """Handle events and calendar queries"""
        try:
            # Get ALL upcoming events (from today onwards)
            today = datetime.now().date()
            
            upcoming_events = Event.query.filter(
                Event.start_date >= today,
                Event.is_active == True
            ).order_by(Event.start_date).limit(20).all()
            
            if not upcoming_events:
                return "📅 No upcoming events scheduled. Stay tuned for updates!"
            
            response = "📅 **Upcoming Events & Holidays:**\n\n"
            
            for event in upcoming_events:
                # Event type emoji
                type_emoji = {
                    'academic': '📚',
                    'cultural': '🎭',
                    'sports': '⚽',
                    'holiday': '🎉',
                    'exam': '📝',
                    'other': '📌'
                }.get(event.event_type, '📌')
                
                response += f"{type_emoji} **{event.title}**\n"
                response += f"   📅 {event.start_date.strftime('%B %d, %Y')}"
                
                if event.start_time:
                    response += f" at {event.start_time.strftime('%I:%M %p')}"
                
                if event.end_date and event.end_date != event.start_date:
                    response += f" - {event.end_date.strftime('%B %d, %Y')}"
                
                response += "\n"
                
                if event.location:
                    response += f"   📍 {event.location}\n"
                
                if event.description:
                    response += f"   📝 {event.description}\n"
                
                response += "\n"
            
            response += "🔔 Mark your calendars and don't miss out!"
            return response
            
        except Exception as e:
            print(f"Error handling events query: {e}")
            return "I'm having trouble accessing the events calendar right now. Please try again later."
    
    def handle_quiz(self, user_message: str, template_response: str, user_context: Dict = None) -> str:
        """Handle quiz questions with proper two-step system"""
        try:
            # Check if user answered with A, B, C, or D
            message_clean = user_message.strip().upper()
            if message_clean in ['A', 'B', 'C', 'D'] and user_context and user_context.get('user_id'):
                user_id = user_context['user_id']
                
                # Find the most recent active quiz session for this user
                active_session = QuizSession.query.filter_by(
                    user_id=user_id,
                    is_active=True,
                    user_answer=None
                ).order_by(QuizSession.created_at.desc()).first()
                
                if active_session:
                    return self._handle_quiz_answer(active_session, message_clean)
            
            # If not answering, start a new quiz
            return self._start_new_quiz(user_message, user_context)
            
        except Exception as e:
            print(f"Error handling quiz query: {e}")
            return "🧠 Here's a quick question: What's the best way to learn? Practice, practice, practice! 🎯"
    
    def _start_new_quiz(self, user_message: str, user_context: Dict = None) -> str:
        """Start a new quiz question"""
        try:
            # Check if user is asking for specific subject or difficulty
            message_lower = user_message.lower()
            category = None
            difficulty = None
            
            # Check for subjects
            if 'computer' in message_lower or 'programming' in message_lower:
                category = 'computer_science'
            elif 'math' in message_lower or 'mathematics' in message_lower:
                category = 'mathematics'
            elif 'science' in message_lower:
                category = 'science'
            elif 'history' in message_lower:
                category = 'history'
            elif 'literature' in message_lower:
                category = 'literature'
            
            # Check for difficulty
            if 'easy' in message_lower:
                difficulty = 'easy'
            elif 'hard' in message_lower or 'difficult' in message_lower:
                difficulty = 'hard'
            elif 'medium' in message_lower:
                difficulty = 'medium'
            
            # Get quiz questions
            query = Quiz.query.filter_by(is_active=True)
            if category:
                query = query.filter_by(category=category)
            if difficulty:
                query = query.filter_by(difficulty=difficulty)
            
            quizzes = query.all()
            
            if not quizzes:
                return "🧠 I don't have any quiz questions available right now. Check back later for brain teasers! 🤔"
            
            quiz = random.choice(quizzes)
            
            # Create quiz session if user is authenticated
            if user_context and user_context.get('user_id'):
                # Deactivate any previous active sessions for this user
                QuizSession.query.filter_by(
                    user_id=user_context['user_id'],
                    is_active=True
                ).update({'is_active': False})
                db.session.commit()
                
                # Create new quiz session
                quiz_session = QuizSession(
                    user_id=user_context['user_id'],
                    quiz_id=quiz.id,
                    session_id='quiz-session',
                    is_active=True
                )
                db.session.add(quiz_session)
                db.session.commit()
            
            # Format response WITHOUT answer or explanation
            response = f"🧠 **Quiz Time!** 🎯\n\n"
            response += f"**Subject:** {quiz.subject.title()}\n"
            response += f"**Difficulty:** {quiz.difficulty.title()}\n"
            response += f"**Points:** {quiz.points}\n\n"
            response += f"**Question:** {quiz.question}\n\n"
            
            # Add options
            options = []
            if quiz.option_a:
                options.append(f"A) {quiz.option_a}")
            if quiz.option_b:
                options.append(f"B) {quiz.option_b}")
            if quiz.option_c:
                options.append(f"C) {quiz.option_c}")
            if quiz.option_d:
                options.append(f"D) {quiz.option_d}")
            
            response += "\n".join(options)
            response += "\n\n🤔 Think you know the answer? Reply with A, B, C, or D!"
            
            return response
            
        except Exception as e:
            print(f"Error starting new quiz: {e}")
            return "🧠 I'm having trouble loading a quiz question right now. Please try again! 🤔"
    
    def _handle_quiz_answer(self, quiz_session: QuizSession, user_answer: str) -> str:
        """Handle user's quiz answer and provide feedback"""
        try:
            quiz = quiz_session.quiz
            is_correct = quiz.check_answer(user_answer)
            
            # Update quiz session
            quiz_session.user_answer = user_answer
            quiz_session.is_correct = is_correct
            quiz_session.points_earned = quiz.points if is_correct else 0
            quiz_session.answered_at = datetime.utcnow()
            quiz_session.is_active = False
            db.session.commit()
            
            # Build response
            if is_correct:
                response = "🎉 **Correct!** Well done! 🌟\n\n"
                response += f"✅ Your answer: **{user_answer}**\n"
                response += f"🏆 You earned **{quiz.points} points**!\n\n"
            else:
                response = "❌ **Incorrect!** Don't worry, keep learning! 📚\n\n"
                response += f"❌ Your answer: **{user_answer}**\n"
                response += f"✅ Correct answer: **{quiz.correct_answer}**\n\n"
            
            # Add explanation if available
            if quiz.explanation:
                response += f"📚 **Explanation:** {quiz.explanation}\n\n"
            
            # Encourage more quizzes
            response += "🧠 Want to try another quiz? Just ask me for another question!"
            
            return response
            
        except Exception as e:
            print(f"Error handling quiz answer: {e}")
            return "🤔 Something went wrong processing your answer. Please try again!"
    
    def handle_courses(self, user_message: str, template_response: str, user_context: Dict = None) -> str:
        """Handle course-related queries"""
        try:
            courses = Course.query.filter_by(is_active=True).limit(10).all()
            
            if not courses:
                return "No course information is available at the moment. Please contact the administration for course details."
            
            response = "📚 **Available Courses:**\n\n"
            
            for course in courses:
                response += f"📖 **{course.course_name}** ({course.course_code})\n"
                response += f"   🎓 Credits: {course.credits}\n"
                response += f"   📅 Semester: {course.semester}, Year: {course.year}\n"
                response += f"   🏢 Department: {course.department}\n"
                
                if course.faculty:
                    response += f"   👨‍🏫 Instructor: {course.faculty.name}\n"
                
                if course.description:
                    response += f"   📝 {course.description}\n"
                
                response += "\n"
            
            response += "Need more details about any specific course? Just ask!"
            return response
            
        except Exception as e:
            print(f"Error handling courses query: {e}")
            return "I'm having trouble accessing course information right now. Please try again later."
    
    def handle_notes(self, user_message: str, template_response: str, user_context: Dict = None) -> str:
        """Handle study notes queries"""
        return "📚 Study notes and materials will be available soon! In the meantime, make sure to:\n\n" + \
               "✏️ Take good notes during lectures\n" + \
               "📖 Review your textbooks regularly\n" + \
               "👥 Form study groups with classmates\n" + \
               "🤔 Ask questions when you don't understand\n\n" + \
               "Keep checking back for uploaded notes and study materials!"
    
    def handle_thanks(self, user_message: str, template_response: str, user_context: Dict = None) -> str:
        """Handle thank you messages"""
        responses = [
            "You're very welcome! 😊 Happy to help!",
            "Glad I could assist you! 🌟 Feel free to ask anytime!",
            "My pleasure! 👍 That's what I'm here for!",
            "You're welcome! 🎉 Don't hesitate to reach out if you need anything else!",
            "Anytime! 😄 I'm always here to help students like you!"
        ]
        return random.choice(responses)
    
    def handle_goodbye(self, user_message: str, template_response: str, user_context: Dict = None) -> str:
        """Handle goodbye messages"""
        user_name = current_user.first_name if current_user.is_authenticated else ""
        
        goodbyes = [
            f"Goodbye {user_name}! 👋 Have a fantastic day!",
            f"See you later {user_name}! 🌟 Take care!",
            f"Farewell {user_name}! 😊 Don't hesitate to come back if you need help!",
            f"Until next time {user_name}! 🎓 Best of luck with your studies!",
            f"Bye {user_name}! 🌈 Hope I was helpful today!"
        ]
        return random.choice(goodbyes)
    
    def handle_help(self, user_message: str, template_response: str, user_context: Dict = None) -> str:
        """Handle help and feature queries"""
        response = "🤖 **EduBot Help Center** 🤖\n\n"
        response += "I'm your college assistant! Here's what I can help you with:\n\n"
        response += "👨‍🏫 **Faculty Info:** Ask about professors, departments, and contact details\n"
        response += "📊 **Attendance:** Check your attendance records and percentages\n"
        response += "📅 **Events:** See upcoming college events and holidays\n"
        response += "📚 **Courses:** Get information about available courses\n"
        response += "🧠 **Quiz:** Test your knowledge with interactive questions\n"
        response += "📖 **Study Notes:** Find study materials and resources\n\n"
        response += "💡 **How to use:**\n"
        response += "• Just type naturally! Ask questions like:\n"
        response += "  - \"Show me faculty info\"\n"
        response += "  - \"What's my attendance?\"\n"
        response += "  - \"Any upcoming events?\"\n"
        response += "  - \"Give me motivation\"\n\n"
        response += "🚀 Try the quick action buttons below for easy access!"
        
        return response
    
    def handle_default(self, user_message: str, template_response: str, user_context: Dict = None) -> str:
        """Handle unrecognized messages - check if it's a faculty name or department"""
        try:
            # First, check if the message contains a faculty name
            faculty_response = self._check_for_faculty_name(user_message)
            if faculty_response:
                return faculty_response
                
            # Then, check if the message contains a department name
            department_response = self._check_for_department_name(user_message)
            if department_response:
                return department_response
        except Exception as e:
            print(f"Error checking for faculty/department: {e}")
            
        # If not a faculty name or department, return a simple template response
        # This allows the Gemini AI to take over in the main engine
        return template_response
        
    def _check_for_faculty_name(self, user_message: str) -> str:
        """Check if the user message contains a faculty member's name"""
        try:
            message_lower = user_message.lower().strip()
            
            # Get all active faculty members
            faculty_members = Faculty.query.filter_by(is_active=True).all()
            
            if not faculty_members:
                return None
            
            # Check for exact name matches (first name, last name, or full name)
            for faculty in faculty_members:
                if faculty.user:
                    first_name = faculty.user.first_name.lower()
                    last_name = faculty.user.last_name.lower()
                    full_name = faculty.user.full_name.lower()
                    
                    # Check various name combinations
                    if (
                        message_lower == first_name or
                        message_lower == last_name or
                        message_lower == full_name or
                        message_lower == f"{first_name} {last_name}" or
                        message_lower == f"{last_name} {first_name}" or
                        message_lower == f"prof {first_name}" or
                        message_lower == f"prof {last_name}" or
                        message_lower == f"professor {first_name}" or
                        message_lower == f"professor {last_name}" or
                        message_lower == f"dr {first_name}" or
                        message_lower == f"dr {last_name}" or
                        message_lower == f"dr. {first_name}" or
                        message_lower == f"dr. {last_name}"
                    ):
                        return self._format_faculty_info(faculty)
                    
                    # Check if the message contains both first and last name (in any order)
                    if first_name in message_lower and last_name in message_lower:
                        return self._format_faculty_info(faculty)
            
            # Check for partial matches if no exact match found
            best_matches = []
            for faculty in faculty_members:
                if faculty.user:
                    first_name = faculty.user.first_name.lower()
                    last_name = faculty.user.last_name.lower()
                    
                    # Check if message contains either first or last name
                    if first_name in message_lower or last_name in message_lower:
                        best_matches.append(faculty)
            
            # If we found partial matches, show them
            if len(best_matches) == 1:
                return self._format_faculty_info(best_matches[0])
            elif len(best_matches) > 1:
                response = "👨‍🏫 I found multiple faculty members matching your search:\n\n"
                for faculty in best_matches:
                    response += f"• **{faculty.name}** - {faculty.designation} ({faculty.department})\n"
                response += "\n💡 Please be more specific with the full name for detailed information."
                return response
            
            return None
            
        except Exception as e:
            print(f"Error in _check_for_faculty_name: {e}")
            return None
    
    def _check_for_department_name(self, user_message: str) -> str:
        """Check if the user message contains a department name"""
        try:
            message_lower = user_message.lower().strip()
            
            # Get all departments from faculty members
            faculty_members = Faculty.query.filter_by(is_active=True).all()
            
            if not faculty_members:
                return None
            
            # Extract unique departments
            departments = list(set([f.department for f in faculty_members if f.department]))
            
            if not departments:
                return None
            
            # Check for exact department matches
            for dept in departments:
                dept_lower = dept.lower()
                
                # Check various department name formats
                if (
                    message_lower == dept_lower or
                    message_lower == f"{dept_lower} department" or
                    message_lower == f"department of {dept_lower}" or
                    message_lower in dept_lower or
                    dept_lower in message_lower
                ):
                    # Get faculty in this department
                    dept_faculty = Faculty.query.filter(
                        Faculty.department.ilike(f'%{dept}%')
                    ).filter_by(is_active=True).all()
                    
                    if dept_faculty:
                        return self._format_department_faculty_list(dept_faculty, dept)
            
            # Check for partial matches with common department keywords
            department_keywords = {
                'computer': 'Computer Science',
                'cs': 'Computer Science',
                'it': 'Information Technology',
                'math': 'Mathematics',
                'mathematics': 'Mathematics',
                'physics': 'Physics',
                'chemistry': 'Chemistry',
                'biology': 'Biology',
                'english': 'English',
                'literature': 'English Literature',
                'history': 'History',
                'economics': 'Economics',
                'business': 'Business Administration',
                'management': 'Management',
                'engineering': 'Engineering'
            }
            
            for keyword, dept_name in department_keywords.items():
                if keyword in message_lower:
                    # Look for faculty with department containing this keyword
                    dept_faculty = Faculty.query.filter(
                        Faculty.department.ilike(f'%{keyword}%')
                    ).filter_by(is_active=True).all()
                    
                    # If no results with keyword, try the full department name
                    if not dept_faculty:
                        dept_faculty = Faculty.query.filter(
                            Faculty.department.ilike(f'%{dept_name}%')
                        ).filter_by(is_active=True).all()
                    
                    if dept_faculty:
                        return self._format_department_faculty_list(dept_faculty, dept_name)
            
            return None
            
        except Exception as e:
            print(f"Error in _check_for_department_name: {e}")
            return None
    
    def _check_department_query(self, message_lower: str, faculty_members) -> str:
        """Check if the message contains department-related queries and return appropriate response"""
        try:
            # Common department keywords and their mappings
            department_keywords = {
                'computer science': ['computer science', 'cs', 'cse'],
                'computer': ['computer science', 'computer'],
                'cs': ['computer science', 'cs'],
                'information technology': ['information technology', 'it'],
                'it': ['information technology', 'it'],
                'mathematics': ['mathematics', 'math', 'maths'],
                'math': ['mathematics', 'math'],
                'physics': ['physics'],
                'chemistry': ['chemistry'],
                'biology': ['biology'],
                'english': ['english', 'literature'],
                'literature': ['english', 'literature'],
                'history': ['history'],
                'economics': ['economics'],
                'business': ['business', 'management'],
                'management': ['management', 'business'],
                'engineering': ['engineering']
            }
            
            # First check for exact department names from database
            departments = list(set([f.department for f in faculty_members if f.department]))
            
            for dept in departments:
                dept_lower = dept.lower()
                if (
                    message_lower == dept_lower or
                    message_lower == f"{dept_lower} department" or
                    message_lower == f"department of {dept_lower}" or
                    dept_lower in message_lower
                ):
                    dept_faculty = Faculty.query.filter(
                        Faculty.department.ilike(f'%{dept}%')
                    ).filter_by(is_active=True).all()
                    
                    if dept_faculty:
                        return self._format_department_faculty_list(dept_faculty, dept)
            
            # Then check common keywords
            for keyword, search_terms in department_keywords.items():
                if any(term in message_lower for term in search_terms):
                    # Search for faculty with department containing these terms
                    dept_faculty = []
                    for term in search_terms:
                        faculty_results = Faculty.query.filter(
                            Faculty.department.ilike(f'%{term}%')
                        ).filter_by(is_active=True).all()
                        dept_faculty.extend(faculty_results)
                    
                    # Remove duplicates
                    dept_faculty = list(set(dept_faculty))
                    
                    if dept_faculty:
                        dept_name = dept_faculty[0].department if dept_faculty else keyword.title()
                        return self._format_department_faculty_list(dept_faculty, dept_name)
            
            return None
            
        except Exception as e:
            print(f"Error in _check_department_query: {e}")
            return None
    
    def _format_department_faculty_list(self, faculty_list, department_name):
        """Format faculty list for a specific department"""
        try:
            if not faculty_list:
                return f"I couldn't find any faculty members in the {department_name} department."
            
            response = f"👥 **Faculty Members in {department_name} Department:**\n\n"
            
            for faculty in faculty_list:
                response += f"👨‍🏫 **{faculty.name}** - {faculty.designation}\n"
                if faculty.office_location:
                    response += f"   📍 Office: {faculty.office_location}\n"
                if faculty.email:
                    response += f"   📧 Email: {faculty.email}\n"
                if faculty.specialization:
                    response += f"   🔬 Specialization: {faculty.specialization}\n"
                response += "\n"
            
            response += f"💡 **Want more details?** Just mention any faculty member's name for complete information!"
            return response
            
        except Exception as e:
            print(f"Error formatting department faculty list: {e}")
            return f"I found faculty in {department_name} but had trouble displaying the information. Please try again."
    
    def _is_faculty_query(self, user_message: str) -> bool:
        """Check if user message is related to faculty information"""
        try:
            message_lower = user_message.lower()
            
            # Check for faculty-related keywords
            faculty_keywords = [
                'faculty', 'professor', 'teacher', 'instructor', 'staff',
                'department', 'teaches', 'teaching', 'lecturer', 'dr.',
                'computer science', 'mathematics', 'physics', 'chemistry',
                'biology', 'history', 'english', 'psychology', 'economics'
            ]
            
            # Check if any faculty keywords are present
            if any(keyword in message_lower for keyword in faculty_keywords):
                return True
            
            # Check if message contains a faculty member's name
            faculty_members = Faculty.query.filter_by(is_active=True).all()
            for faculty in faculty_members:
                if faculty.user:
                    first_name = faculty.user.first_name.lower()
                    last_name = faculty.user.last_name.lower()
                    full_name = faculty.user.full_name.lower()
                    
                    # Check for exact name matches
                    if (first_name in message_lower and last_name in message_lower) or \
                       full_name in message_lower or \
                       (len(first_name) > 2 and first_name in message_lower) or \
                       (len(last_name) > 2 and last_name in message_lower):
                        return True
            
            return False
            
        except Exception as e:
            print(f"Error checking if faculty query: {e}")
            return False
    

# Global response handler instance
response_handler = ResponseHandler()
