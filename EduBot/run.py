#!/usr/bin/env python3
"""
EduBot - College Chatbot Application
Main application runner
"""

import os
from dotenv import load_dotenv
from app import create_app, socketio

# Load environment variables from .env file
load_dotenv()

# Create Flask application
app = create_app()

if __name__ == '__main__':
    # Get configuration from environment
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    host = os.environ.get('FLASK_HOST', '127.0.0.1')
    port = int(os.environ.get('FLASK_PORT', 5000))
    
    # Print startup information
    print("=" * 50)
    print("EduBot - College Chatbot Starting...")
    print("=" * 50)
    print(f"Server: http://{host}:{port}")
    print(f"Debug Mode: {debug}")
    print(f"Database: {app.config.get('SQLALCHEMY_DATABASE_URI', 'Not configured')}")
    print("=" * 50)
    
    # Run the application (simplified version)
    try:
        # Try SocketIO first
        socketio.run(
            app,
            debug=debug,
            host=host,
            port=port,
            use_reloader=debug,
            log_output=debug
        )
    except Exception as e:
        print(f"SocketIO failed: {e}")
        print("Falling back to standard Flask server...")
        # Fallback to standard Flask server
        app.run(
            debug=debug,
            host=host,
            port=port,
            use_reloader=debug
        )
