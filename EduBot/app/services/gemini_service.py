"""
Gemini AI Service Module
Handles integration with Google's Gemini AI API for intelligent responses
"""

import os
import time
import logging
from typing import Optional, Dict, Any
import google.generativeai as genai
from flask import current_app

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeminiService:
    """Service class for interacting with Google Gemini AI"""
    
    def __init__(self):
        self.model = None
        self.is_initialized = False
        self.max_retries = 3
        self.retry_delay = 1
        
    def initialize(self, api_key: str = None):
        """Initialize the Gemini AI service with API key"""
        try:
            # Get API key from parameter or environment
            if not api_key:
                api_key = os.environ.get('GEMINI_API_KEY')
            
            if not api_key or api_key == 'your-gemini-api-key-here':
                logger.warning("Gemini API key not configured. Gemini features will be disabled.")
                return False
            
            # Configure the API
            genai.configure(api_key=api_key)
            
            # Initialize the model
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Skip the test connection for now to prevent startup hanging
            # The connection will be tested when first used
            self.is_initialized = True
            logger.info("Gemini AI service initialized successfully")
            return True
                
        except Exception as e:
            logger.error(f"Error initializing Gemini AI service: {e}")
            return False
    
    def generate_response(self, user_message: str, context: Dict[str, Any] = None) -> Optional[str]:
        """
        Generate a response using Gemini AI
        
        Args:
            user_message: The user's input message
            context: Additional context about the user and conversation
            
        Returns:
            Generated response string or None if failed
        """
        if not self.is_initialized:
            return None
            
        try:
            # Build the prompt with context
            prompt = self._build_prompt(user_message, context)
            
            # Generate response with retries
            for attempt in range(self.max_retries):
                try:
                    response = self.model.generate_content(prompt)
                    
                    if response and response.text:
                        # Clean and validate the response
                        cleaned_response = self._clean_response(response.text)
                        logger.info(f"Gemini response generated successfully (attempt {attempt + 1})")
                        return cleaned_response
                    else:
                        logger.warning(f"Empty response from Gemini (attempt {attempt + 1})")
                        
                except Exception as e:
                    error_str = str(e)
                    # Handle quota exceeded specifically
                    if "429" in error_str and "quota" in error_str.lower():
                        logger.error(f"Gemini API quota exceeded: {e}")
                        return "I'd love to help with that question, but I've reached my daily limit for AI responses. Please try again tomorrow, or ask about college-specific topics like faculty, courses, events, or attendance that I can answer from our database!"
                    
                    logger.warning(f"Gemini API call failed (attempt {attempt + 1}): {e}")
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay * (attempt + 1))
                    
            logger.error("All Gemini API attempts failed")
            return None
            
        except Exception as e:
            logger.error(f"Error generating Gemini response: {e}")
            return None
    
    def _build_prompt(self, user_message: str, context: Dict[str, Any] = None) -> str:
        """Build a comprehensive prompt for Gemini AI"""
        
        # Base system prompt for EduBot
        system_prompt = """You are EduBot, an intelligent college chatbot assistant. You help students with educational queries.

IMPORTANT: You are being used as a fallback when the college's internal database doesn't have the answer.

Your role:
- Provide general educational guidance and study tips
- Answer academic questions (math, science, literature, etc.)
- Give career advice and course selection help
- Explain concepts and provide learning resources
- Offer motivational support for students
- Help with assignment and project ideas

Guidelines:
- Be helpful, encouraging, and educational
- Keep responses concise (under 200 words)
- If asked about specific college details (faculty, events, schedules), politely say you don't have access to that institutional data
- Focus on being a learning companion and study assistant
- Always maintain a supportive, academic tone
"""
        
        # Add user context if available
        context_info = ""
        if context:
            if context.get('is_authenticated'):
                context_info += f"User: {context.get('user_name', 'Student')}\n"
                context_info += f"Role: {context.get('user_role', 'student')}\n"
            
            # Add conversation history if available
            if context.get('conversation_history'):
                context_info += "Recent conversation:\n"
                for msg in context['conversation_history'][-2:]:  # Last 2 messages
                    context_info += f"User: {msg['user_message']}\n"
                    context_info += f"Bot: {msg['bot_response']}\n"
        
        # Build final prompt
        full_prompt = f"""{system_prompt}

{context_info}

Current Question: {user_message}

Please provide a helpful response:"""
        
        return full_prompt
    
    def _clean_response(self, response: str) -> str:
        """Clean and format the Gemini response"""
        if not response:
            return ""
            
        # Remove excessive whitespace
        cleaned = ' '.join(response.split())
        
        # Limit response length (for chat interface)
        max_length = 800
        if len(cleaned) > max_length:
            cleaned = cleaned[:max_length] + "..."
        
        return cleaned
    
    def is_available(self) -> bool:
        """Check if Gemini service is available"""
        return self.is_initialized
    
    def get_status(self) -> Dict[str, Any]:
        """Get service status information"""
        return {
            'initialized': self.is_initialized,
            'available': self.is_available(),
            'model': 'gemini-pro' if self.is_initialized else None
        }


# Global service instance
gemini_service = GeminiService()
