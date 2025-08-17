"""
EduBot Intent Recognition Engine
Handles pattern matching and intent classification for user messages
"""

import re
import json
import random
from typing import Dict, List, Tuple, Optional
from app import db
from app.models.intent import Intent

class IntentRecognizer:
    """Recognizes user intents from text input using pattern matching"""
    
    def __init__(self):
        self.intents = {}
        # Don't load intents immediately - wait for app context
    
    def load_intents(self):
        """Load intents from database"""
        try:
            db_intents = Intent.query.filter_by(is_active=True).order_by(Intent.priority.desc()).all()
            
            for intent in db_intents:
                try:
                    patterns = json.loads(intent.patterns)
                    responses = json.loads(intent.responses)
                    
                    self.intents[intent.intent_name] = {
                        'patterns': patterns,
                        'responses': responses,
                        'handler': intent.handler_function,
                        'priority': intent.priority,
                        'description': intent.description
                    }
                except json.JSONDecodeError:
                    print(f"Error parsing intent {intent.intent_name}: Invalid JSON")
                    
        except Exception as e:
            print(f"Error loading intents: {e}")
            self._load_default_intents()
    
    def _load_default_intents(self):
        """Load hardcoded default intents as fallback"""
        self.intents = {
            'greeting': {
                'patterns': [r'\b(hello|hi|hey|greetings|good morning|good afternoon|good evening)\b'],
                'responses': [
                    "Hello! How can I help you today?",
                    "Hi there! What would you like to know?",
                    "Hey! I'm here to assist you.",
                    "Greetings! How may I assist you?"
                ],
                'handler': 'handle_greeting',
                'priority': 10
            },
            'faculty_info': {
                'patterns': [
                    r'\b(faculty|teacher|professor|instructor|staff|who teaches)\b',
                    r'\b(faculty details|faculty information|about faculty)\b',
                    r'\b(find faculty|search faculty)\b',
                    r'\b(computer science|computer|cs|it|information technology)\b',
                    r'\b(mathematics|math|maths|physics|chemistry|biology)\b',
                    r'\b(english|literature|history|economics|business)\b',
                    r'\b(engineering|mechanical|electrical|civil)\b',
                    r'\b(department|dept)\b'
                ],
                'responses': [
                    "I can help you find faculty information. Which faculty member are you looking for?",
                    "Let me help you with faculty details. Please specify the faculty name or department."
                ],
                'handler': 'handle_faculty',
                'priority': 8
            },
            'attendance': {
                'patterns': [
                    r'\b(attendance|present|absent|attendance record|my attendance)\b',
                    r'\b(attendance percentage|how many classes)\b',
                    r'\b(check attendance|attendance status)\b'
                ],
                'responses': [
                    "Let me check your attendance records.",
                    "I'll fetch your attendance information."
                ],
                'handler': 'handle_attendance',
                'priority': 8
            },
            'events': {
                'patterns': [
                    r'\b(events|holiday|holidays|upcoming events|college events)\b',
                    r'\b(festival|celebration|calendar|schedule)\b',
                    r'\b(what events|any events|show events)\b'
                ],
                'responses': [
                    "Here are the upcoming events and holidays.",
                    "Let me show you the college calendar."
                ],
                'handler': 'handle_events',
                'priority': 7
            },
            'quiz': {
                'patterns': [
                    r'\b(quiz|question|test|challenge|brain teaser)\b',
                    r'\b(quiz me|ask me|test my knowledge)\b',
                    r'\b(trivia|game|puzzle)\b',
                    r'^[ABCD]$',  # Single letter quiz answers
                    r'^[abcd]$'   # Lowercase quiz answers
                ],
                'responses': [
                    "Let me give you a quiz question!",
                    "Time for a brain teaser!"
                ],
                'handler': 'handle_quiz',
                'priority': 6
            },
            'courses': {
                'patterns': [
                    r'\b(courses|subjects|course details|curriculum)\b',
                    r'\b(syllabus|course content|what courses)\b',
                    r'\b(my courses|enrolled courses)\b'
                ],
                'responses': [
                    "Let me help you with course information.",
                    "I can provide details about courses and curriculum."
                ],
                'handler': 'handle_courses',
                'priority': 7
            },
            'notes': {
                'patterns': [
                    r'\b(notes|study material|lecture notes|notes download)\b',
                    r'\b(study resources|materials|downloads)\b'
                ],
                'responses': [
                    "I can help you find study notes and materials.",
                    "Let me show you available study resources."
                ],
                'handler': 'handle_notes',
                'priority': 6
            },
            'thanks': {
                'patterns': [
                    r'\b(thanks|thank you|thankyou|appreciate|grateful)\b'
                ],
                'responses': [
                    "You're welcome! Happy to help!",
                    "Glad I could assist you!",
                    "Anytime! Feel free to ask if you need anything else."
                ],
                'handler': 'handle_thanks',
                'priority': 5
            },
            'bye': {
                'patterns': [
                    r'\b(bye|goodbye|see you|farewell|exit|quit)\b'
                ],
                'responses': [
                    "Goodbye! Have a great day!",
                    "See you later! Take care!",
                    "Farewell! Don't hesitate to come back if you need help."
                ],
                'handler': 'handle_goodbye',
                'priority': 5
            },
            'help': {
                'patterns': [
                    r'\b(help|what can you do|commands|features|assist)\b',
                    r'\b(how to use|instructions|guide)\b'
                ],
                'responses': [
                    "I can help you with faculty info, attendance, events, motivational quotes, and much more!",
                    "Here's what I can do for you: Check faculty details, view attendance, see upcoming events, get motivational quotes, and answer general questions."
                ],
                'handler': 'handle_help',
                'priority': 6
            },
            'default': {
                'patterns': [r'.*'],
                'responses': [
                    "I'm sorry, I didn't understand that. Could you please rephrase?",
                    "I'm not sure how to help with that. Try asking about faculty, attendance, events, or motivational quotes.",
                    "Could you please be more specific? I can help with faculty info, attendance, events, and more!"
                ],
                'handler': 'handle_default',
                'priority': 1
            }
        }
    
    def recognize_intent(self, message: str) -> Tuple[str, float, str]:
        """
        Recognize intent from user message
        Returns: (intent_name, confidence_score, matched_pattern)
        """
        # Load intents if not already loaded
        if not self.intents:
            self._load_default_intents()
            
        message = message.lower().strip()
        
        # Check each intent in priority order
        for intent_name, intent_data in sorted(
            self.intents.items(), 
            key=lambda x: x[1]['priority'], 
            reverse=True
        ):
            for pattern in intent_data['patterns']:
                if re.search(pattern, message, re.IGNORECASE):
                    # Special handling for default intent - low confidence
                    if intent_name == 'default':
                        return intent_name, 0.3, pattern
                    
                    # Calculate confidence based on match quality for other intents
                    confidence = self._calculate_confidence(message, pattern)
                    return intent_name, confidence, pattern
        
        # Fallback to default intent
        return 'default', 0.3, '.*'
    
    def _calculate_confidence(self, message: str, pattern: str) -> float:
        """Calculate confidence score for pattern match"""
        try:
            match = re.search(pattern, message, re.IGNORECASE)
            if not match:
                return 0.1
            
            # Base confidence
            confidence = 0.7
            
            # Boost confidence for exact keyword matches
            if match.group(0).lower() in message.lower():
                confidence += 0.2
            
            # Boost for longer matches
            match_length = len(match.group(0))
            message_length = len(message)
            if match_length > message_length * 0.3:
                confidence += 0.1
            
            return min(confidence, 0.95)  # Cap at 95%
            
        except Exception:
            return 0.1
    
    def get_response_template(self, intent_name: str) -> str:
        """Get a random response template for the given intent"""
        if intent_name in self.intents:
            responses = self.intents[intent_name]['responses']
            return random.choice(responses)
        return "I'm not sure how to help with that."
    
    def get_handler_function(self, intent_name: str) -> Optional[str]:
        """Get the handler function name for the given intent"""
        if intent_name in self.intents:
            return self.intents[intent_name].get('handler')
        return None
    
    def add_intent(self, intent_name: str, patterns: List[str], responses: List[str], 
                   handler: str = None, priority: int = 5):
        """Add a new intent dynamically"""
        self.intents[intent_name] = {
            'patterns': patterns,
            'responses': responses,
            'handler': handler,
            'priority': priority
        }
    
    def reload_intents(self):
        """Reload intents from database"""
        self.load_intents()
    
    def get_all_intents(self) -> Dict:
        """Get all loaded intents"""
        return self.intents

# Global intent recognizer instance
intent_recognizer = IntentRecognizer()
