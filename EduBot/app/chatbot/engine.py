"""
EduBot Main Chatbot Engine
Orchestrates intent recognition, response generation, and conversation flow
"""

import time
from typing import Dict, Tuple
from flask import request
from flask_login import current_user
from app import db
from app.models.chat_log import ChatLog
from app.models.quick_action import QuickAction
from app.models.quiz_session import QuizSession
from app.chatbot.intents import intent_recognizer
from app.chatbot.handlers import response_handler
from app.services.gemini_service import gemini_service

class ChatbotEngine:
    """Main chatbot engine that processes user messages and generates responses"""
    
    def __init__(self):
        self.intent_recognizer = intent_recognizer
        self.response_handler = response_handler
        self.conversation_context = {}
        self._initialized = False
    
    def initialize(self):
        """Initialize the chatbot engine with Flask app context"""
        if not self._initialized:
            try:
                self.intent_recognizer.load_intents()
                self._initialized = True
                print("Chatbot engine initialized successfully")
            except Exception as e:
                print(f"Error initializing chatbot engine: {e}")
                # Fall back to default intents
                self.intent_recognizer._load_default_intents()
                self._initialized = True
    
    def process_message(self, user_message: str, user_id: int = None, session_id: str = None) -> Dict:
        """
        Process a user message and generate an intelligent response
        
        Args:
            user_message: The user's input message
            user_id: ID of the user (for logging and context)
            session_id: Session ID for conversation tracking
            
        Returns:
            Dict containing response, intent, confidence, and metadata
        """
        # Ensure initialization
        if not self._initialized:
            self.initialize()
            
        start_time = time.time()
        
        try:
            # Clean and validate input
            user_message = user_message.strip()
            if not user_message:
                return self._create_error_response("Please enter a message.")
            
            # FIRST: Check for active quiz sessions if message looks like quiz answer
            quiz_response = self._check_quiz_answer(user_message, user_id)
            if quiz_response:
                response_time = int((time.time() - start_time) * 1000)
                
                # Log the conversation with quiz intent
                if user_id:
                    self._log_conversation(
                        user_id, session_id, user_message, quiz_response,
                        'quiz', 0.98, response_time
                    )
                
                return {
                    'response': quiz_response,
                    'intent': 'quiz',
                    'confidence': 0.98,
                    'response_time_ms': response_time,
                    'matched_pattern': 'quiz_answer',
                    'success': True
                }
            
            # SECOND: Check for Quick Actions before intent recognition
            quick_action_response = self._check_quick_actions(user_message)
            if quick_action_response:
                response_time = int((time.time() - start_time) * 1000)
                
                # Log the conversation with quick_action intent
                if user_id:
                    self._log_conversation(
                        user_id, session_id, user_message, quick_action_response,
                        'quick_action', 0.95, response_time
                    )
                
                return {
                    'response': quick_action_response,
                    'intent': 'quick_action',
                    'confidence': 0.95,
                    'response_time_ms': response_time,
                    'matched_pattern': 'quick_action',
                    'success': True
                }
            
            # If no Quick Action matched, proceed with normal intent recognition
            intent_name, confidence, matched_pattern = self.intent_recognizer.recognize_intent(user_message)
            
            # Get base response template
            template_response = self.intent_recognizer.get_response_template(intent_name)
            
            # Get user context
            user_context = self._get_user_context(user_id)
            
            # Generate intelligent response using handlers
            final_response = self.response_handler.handle_intent(
                intent_name, 
                user_message, 
                template_response, 
                user_context
            )
            
            # Use Gemini AI for questions that are truly unknown
            # Protect database responses - STRONGEST protection for internal data
            
            # Define intents that should ALWAYS use internal database (NEVER override)
            protected_intents = ['faculty_info', 'attendance', 'events', 'courses', 'quiz', 'notes', 'greeting', 'thanks', 'bye', 'help', 'quick_action']
            
            # Check if the message might be a faculty name or department before using Gemini
            is_faculty_related = self._is_faculty_related(user_message)
            
            # ABSOLUTE PROTECTION: Never use Gemini for protected intents OR faculty-related queries
            if intent_name in protected_intents or is_faculty_related:
                should_use_gemini = False
            else:
                # Use Gemini for 'default' intent with low confidence (unknown questions)
                # This means the user asked something not in our database
                should_use_gemini = (
                    intent_name == 'default' and confidence < 0.7
                )
            
            if should_use_gemini:
                gemini_response = self._try_gemini_response(user_message, user_context)
                if gemini_response:
                    final_response = "This answer is provided by AI: " + gemini_response
                    intent_name = 'gemini_ai'
                    confidence = 0.85
            
            # Calculate response time
            response_time = int((time.time() - start_time) * 1000)
            
            # Log the conversation
            if user_id:
                self._log_conversation(
                    user_id, session_id, user_message, final_response,
                    intent_name, confidence, response_time
                )
            
            # Update conversation context
            self._update_context(user_id, intent_name, user_message)
            
            return {
                'response': final_response,
                'intent': intent_name,
                'confidence': confidence,
                'response_time_ms': response_time,
                'matched_pattern': matched_pattern,
                'success': True
            }
            
        except Exception as e:
            print(f"Chatbot engine error: {e}")
            return self._create_error_response("I'm experiencing some technical difficulties. Please try again.")
    
    def _get_user_context(self, user_id: int = None) -> Dict:
        """Get user context for personalized responses"""
        context = {
            'is_authenticated': False,
            'user_role': None,
            'user_name': None,
            'conversation_history': []
        }
        
        if current_user and current_user.is_authenticated:
            context.update({
                'is_authenticated': True,
                'user_role': current_user.role,
                'user_name': current_user.first_name,
                'user_id': current_user.id,
                'full_name': current_user.full_name
            })
            
            # Get recent conversation history
            if user_id:
                recent_logs = ChatLog.query.filter_by(user_id=user_id)\
                                         .order_by(ChatLog.created_at.desc())\
                                         .limit(5).all()
                context['conversation_history'] = [
                    {
                        'user_message': log.user_message,
                        'bot_response': log.bot_response,
                        'intent': log.intent,
                        'timestamp': log.created_at
                    }
                    for log in recent_logs
                ]
        
        return context
    
    def _update_context(self, user_id: int, intent_name: str, user_message: str):
        """Update conversation context for continuity"""
        if user_id:
            if user_id not in self.conversation_context:
                self.conversation_context[user_id] = {
                    'last_intent': None,
                    'message_count': 0,
                    'topics_discussed': [],
                    'last_interaction': None
                }
            
            context = self.conversation_context[user_id]
            context['last_intent'] = intent_name
            context['message_count'] += 1
            context['last_interaction'] = time.time()
            
            # Track topics
            if intent_name not in context['topics_discussed']:
                context['topics_discussed'].append(intent_name)
    
    def _log_conversation(self, user_id: int, session_id: str, user_message: str, 
                         bot_response: str, intent: str, confidence: float, 
                         response_time: int):
        """Log conversation to database"""
        try:
            chat_log = ChatLog(
                user_id=user_id,
                session_id=session_id or 'no-session',
                user_message=user_message,
                bot_response=bot_response,
                intent=intent,
                confidence_score=confidence,
                response_time_ms=response_time,
                ip_address=request.remote_addr if request else None,
                user_agent=request.headers.get('User-Agent', '') if request else ''
            )
            
            db.session.add(chat_log)
            db.session.commit()
            
        except Exception as e:
            print(f"Error logging conversation: {e}")
            # Don't fail the response if logging fails
            try:
                db.session.rollback()
            except:
                pass
    
    def _check_quiz_answer(self, user_message: str, user_id: int = None) -> str:
        """Check if user message is a quiz answer and handle it"""
        try:
            # Check if message looks like a quiz answer (A, B, C, D)
            message_clean = user_message.strip().upper()
            if message_clean not in ['A', 'B', 'C', 'D'] or not user_id:
                return None
            
            # Find the most recent active quiz session for this user
            active_session = QuizSession.query.filter_by(
                user_id=user_id,
                is_active=True,
                user_answer=None
            ).order_by(QuizSession.created_at.desc()).first()
            
            if active_session:
                # Handle the quiz answer using the response handler
                return self.response_handler._handle_quiz_answer(active_session, message_clean)
            
            return None
            
        except Exception as e:
            print(f"Error checking quiz answer: {e}")
            return None
    
    def _check_quick_actions(self, user_message: str) -> str:
        """Check if user message matches any Quick Actions and return response"""
        try:
            # Search for matching Quick Action responses
            matching_actions = QuickAction.search_for_answer(user_message, limit=1)
            
            if matching_actions:
                # Get the best match (highest priority)
                quick_action = matching_actions[0]
                quick_action.increment_usage()  # Track usage
                return quick_action.response
            
            return None
            
        except Exception as e:
            print(f"Error checking Quick Actions: {e}")
            return None
    
    def _try_gemini_response(self, user_message: str, user_context: Dict = None) -> str:
        """Try to get a response from Gemini AI"""
        try:
            if not gemini_service.is_available():
                return None
                
            # Generate response using Gemini
            gemini_response = gemini_service.generate_response(user_message, user_context)
            
            if gemini_response:
                return gemini_response
            else:
                return None
                
        except Exception as e:
            print(f"Error getting Gemini response: {e}")
            return None
    
    def _create_error_response(self, message: str) -> Dict:
        """Create a standardized error response"""
        return {
            'response': message,
            'intent': 'error',
            'confidence': 0.0,
            'response_time_ms': 0,
            'matched_pattern': None,
            'success': False
        }
    
    def get_conversation_stats(self, user_id: int) -> Dict:
        """Get conversation statistics for a user"""
        try:
            logs = ChatLog.query.filter_by(user_id=user_id).all()
            
            if not logs:
                return {'message_count': 0, 'topics_discussed': 0, 'avg_response_time': 0}
            
            total_messages = len(logs)
            unique_intents = len(set(log.intent for log in logs if log.intent))
            avg_response_time = sum(log.response_time_ms or 0 for log in logs) / total_messages
            
            # Most common intents
            intent_counts = {}
            for log in logs:
                if log.intent:
                    intent_counts[log.intent] = intent_counts.get(log.intent, 0) + 1
            
            most_common_intent = max(intent_counts.items(), key=lambda x: x[1])[0] if intent_counts else None
            
            return {
                'message_count': total_messages,
                'topics_discussed': unique_intents,
                'avg_response_time': round(avg_response_time, 2),
                'most_common_intent': most_common_intent,
                'intent_distribution': intent_counts
            }
            
        except Exception as e:
            print(f"Error getting conversation stats: {e}")
            return {'error': 'Unable to fetch statistics'}
    
    def reload_intents(self):
        """Reload intents from database (useful for admin updates)"""
        try:
            self.intent_recognizer.reload_intents()
            return True
        except Exception as e:
            print(f"Error reloading intents: {e}")
            return False
    
    def add_dynamic_response(self, intent_name: str, user_message: str, 
                           admin_response: str, confidence_threshold: float = 0.8):
        """Add a dynamic response based on user feedback (admin feature)"""
        try:
            # This could be expanded to learn from user interactions
            # For now, it's a placeholder for future machine learning integration
            return True
        except Exception as e:
            print(f"Error adding dynamic response: {e}")
            return False
    
    def _is_faculty_related(self, user_message: str) -> bool:
        """Check if the user message is related to faculty information"""
        try:
            # Use the response handler's faculty detection logic
            return self.response_handler._is_faculty_query(user_message)
        except Exception as e:
            print(f"Error checking if faculty related: {e}")
            return False
    

# Global chatbot engine instance
chatbot_engine = ChatbotEngine()
